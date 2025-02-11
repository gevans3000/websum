#!/usr/bin/env python3
"""
WebSum: A web content extraction and summarization tool
This module provides functionality to crawl web pages, extract meaningful content,
and save it in various knowledge base formats optimized for both human reading
and LLM processing.

Key features:
- Intelligent web crawling with rate limiting and caching
- Content extraction focused on documentation and technical content
- Multiple output formats (standard and condensed summaries)
- Knowledge base organization with metadata
"""

import os
import sys
import json
import logging
import logging.config
import datetime
import argparse
import asyncio
import re
from urllib.parse import urljoin, urlparse
from crawl4ai import (
    AsyncWebCrawler,
    BrowserConfig,
    CrawlerRunConfig,
    CacheMode,
    ChunkingStrategy
)
from crawl4ai.content_filter_strategy import PruningContentFilter, BM25ContentFilter
from crawl4ai.markdown_generation_strategy import DefaultMarkdownGenerator
from crawl4ai.extraction_strategy import ExtractionStrategy, CosineStrategy, JsonCssExtractionStrategy
from io import StringIO
from contextlib import redirect_stdout, redirect_stderr
from bs4 import BeautifulSoup, NavigableString
from enum import Enum, auto
import time
from modules.utils import (
    clean_text,
    is_navigation_text,
    ensure_url_scheme,
    process_code,
    process_markdown_content
)
from playwright.async_api import async_playwright
from tqdm import tqdm

# Configure structured logging
logging_config = {
    'version': 1,
    'disable_existing_loggers': True,  # Disable other loggers to prevent interference
    'formatters': {
        'standard': {
            'format': '\r%(message)s\n',  # Use carriage return to clear progress bar line
        },
    },
    'handlers': {
        'default': {
            'level': 'INFO',
            'formatter': 'standard',
            'class': 'logging.StreamHandler',
            'stream': 'ext://sys.stdout',
        },
    },
    'loggers': {
        '': {
            'handlers': ['default'],
            'level': 'INFO',
            'propagate': True
        }
    }
}

# Apply logging configuration
logging.config.dictConfig(logging_config)
logger = logging.getLogger("websum")

# Custom exception for WebSum-specific errors
class WebSumError(Exception):
    """Base exception class for WebSum errors"""
    def __init__(self, message, details=None):
        super().__init__(message)
        self.details = details or {}
        self.timestamp = datetime.datetime.now(datetime.timezone.utc).isoformat()

class CrawlError(WebSumError):
    """Raised when crawling fails"""
    pass

class ProcessingError(WebSumError):
    """Raised when content processing fails"""
    pass

class StorageError(WebSumError):
    """Raised when saving content fails"""
    pass

# Utility functions
def format_code_block(code):
    """
    Format code blocks with proper markdown syntax and intelligent indentation.
    
    This function:
    1. Detects Python code through common patterns
    2. Cleans up whitespace while preserving meaningful empty lines
    3. Fixes indentation for better readability
    4. Adds proper line breaks around key structures (imports, classes, functions)
    5. Handles multi-line strings correctly
    
    Args:
        code (str): Raw code block content
        
    Returns:
        str: Formatted code block with markdown syntax and language hint
    """
    # Detect if this is a Python code block
    is_python = bool(re.search(r'(import\s+\w+|from\s+\w+\s+import|def\s+\w+|class\s+\w+|async\s+def)', code))
    
    # Clean up the code
    code = code.strip()
    
    # Format Python code
    if is_python:
        try:
            # Split into lines
            lines = code.split('\n')
            
            # Remove empty lines at start/end while preserving internal empty lines
            while lines and not lines[0].strip():
                lines.pop(0)
            while lines and not lines[-1].strip():
                lines.pop()
            
            # Find common indentation
            def get_indentation(line):
                return len(line) - len(line.lstrip()) if line.strip() else None
            
            indentation_levels = [get_indentation(line) for line in lines if get_indentation(line) is not None]
            if indentation_levels:
                common_indent = min(indentation_levels)
                # Remove common indentation
                lines = [line[common_indent:] if line.strip() else '' for line in lines]
            
            # Join lines back together
            code = '\n'.join(lines)
            
            # Add proper line breaks for readability
            code = re.sub(r'(\s*import\s+[^;]+?;?\s*$)', r'\1\n', code, flags=re.MULTILINE)  # After imports
            code = re.sub(r'(\s*from\s+[^;]+?import[^;]+?;?\s*$)', r'\1\n', code, flags=re.MULTILINE)  # After from imports
            code = re.sub(r'(\s*class\s+[^:]+:\s*$)', r'\1\n', code, flags=re.MULTILINE)  # Before class
            code = re.sub(r'(\s*def\s+[^:]+:\s*$)', r'\1\n', code, flags=re.MULTILINE)  # Before function
            code = re.sub(r'(\s*async\s+def\s+[^:]+:\s*$)', r'\1\n', code, flags=re.MULTILINE)  # Before async function
            
            # Fix indentation for multi-line strings
            code = re.sub(r'(["\'\']).*?\1', lambda m: m.group().replace('\n', '\n    '), code, flags=re.DOTALL)
            
        except Exception as e:
            logger.warning(f"Error formatting Python code: {e}")
    
    return code

def format_text_content(text):
    """
    Format text content with proper line breaks for readability.
    Ensures consistent spacing between paragraphs while avoiding excessive whitespace.
    
    Args:
        text (str): Raw text content
        
    Returns:
        str: Formatted text with normalized line breaks
    """
    return text.replace("\n\n", "\n")

# Configure logging for debugging and monitoring
logger = logging.getLogger(__name__)

# Version tracking for compatibility and updates
VERSION = "1.0.0"

# Browser configuration optimized for reliable content extraction
BROWSER_CONFIG = {
    'browser_type': "chromium",  # Most compatible and stable for web scraping
    'headless': True,           # Run without GUI for better performance
    'viewport_width': 1280,     # Standard desktop resolution
    'viewport_height': 1080,    # Ensures full page content is visible
    'user_agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",  # Modern browser UA
    'verbose': False,           # Minimize noise in logs
    'ignore_https_errors': True # Handle sites with SSL issues
}

# Content extraction strategy focused on documentation pages
EXTRACTION_STRATEGY = JsonCssExtractionStrategy({
    "name": "Documentation Extraction",
    "baseSelector": ".md-content__inner",  # Common documentation content wrapper
    "fields": [
        {"name": "title", "selector": "h1", "type": "text"},           # Main page title
        {"name": "content", "selector": ".md-typeset", "type": "text"},# Main content body
        {"name": "code_blocks", "selector": "pre code", "type": "text"}# Code examples
    ]
})

# Crawler configuration optimized for documentation sites
CRAWLER_CONFIG = CrawlerRunConfig(
    word_count_threshold=3,           # Minimum words for content blocks
    wait_until="networkidle",         # Ensure dynamic content is loaded
    page_timeout=30000,               # 30s timeout for slow pages
    extraction_strategy=EXTRACTION_STRATEGY,
    process_iframes=True,             # Handle embedded content
    remove_overlay_elements=True,      # Remove popups/modals
    cache_mode=CacheMode.ENABLED,     # Cache results for efficiency
    exclude_external_links=False,      # Allow relevant external links
    excluded_tags=['nav', 'footer', 'header', 'script']  # Skip non-content areas
)

# Configure markdown generation for clean, consistent output
MARKDOWN_GENERATOR = DefaultMarkdownGenerator(
    options={
        "preserve_tables": True,      # Keep table formatting
        "retain_code_blocks": True,   # Preserve code examples
        "escape_html": False,         # Allow HTML when needed
        "inline_code_format": "backticks",  # Standard markdown code format
        "strip_comments": True        # Remove HTML comments
    }
)

class SummaryFormat(Enum):
    """
    Defines available summary output formats:
    - STANDARD: Detailed summary with full content structure
    - CONDENSED: Brief overview with key points only
    """
    STANDARD = auto()
    CONDENSED = auto()

# Performance optimization settings
os.environ["CRAWL4AI_MAX_BUFFER_SIZE"] = "1000000"  # 1MB buffer for memory efficiency
os.environ["CRAWL4AI_CHUNK_SIZE"] = "524288"       # 512KB chunks for streaming
os.environ["CRAWL4AI_STREAM_MODE"] = "True"        # Enable streaming for large pages

class CrawlProgress:
    """
    Tracks and manages crawling progress with optional page limits.
    
    This class:
    - Monitors number of pages processed
    - Enforces optional page limits
    - Helps prevent runaway crawling
    """
    def __init__(self, page_limit=None):
        """
        Initialize progress tracker.
        
        Args:
            page_limit (int, optional): Maximum pages to process. None for unlimited.
        """
        self.page_limit = page_limit
        self.pages_processed = 0
        self.start_time = None
        
    def should_process_more(self):
        """Check if more pages can be processed within the limit"""
        if self.page_limit is None:
            return True
        return self.pages_processed < self.page_limit
        
    def update(self):
        """Increment the processed page counter"""
        self.pages_processed += 1
        
    def limit_reached(self):
        """Check if we've hit the page processing limit"""
        if self.page_limit is None:
            return False
        return self.pages_processed >= self.page_limit

class RateLimiter:
    """
    Implements rate limiting to prevent overwhelming target servers.
    Ensures polite crawling by maintaining minimum delays between requests.
    """
    def __init__(self, delay_seconds=1.0):
        """
        Initialize rate limiter.
        
        Args:
            delay_seconds (float): Minimum delay between requests
        """
        self.delay = delay_seconds
        self.last_request = 0
        
    async def wait(self):
        """
        Wait if needed to maintain rate limit.
        Uses asyncio.sleep for non-blocking delays.
        """
        now = time.time()
        elapsed = now - self.last_request
        if elapsed < self.delay:
            await asyncio.sleep(self.delay - elapsed)
        self.last_request = time.time()

class URLCache:
    """
    Manages URL processing history to:
    - Prevent duplicate processing
    - Enable resume capability
    - Track crawling progress
    
    Uses JSON file for persistence between runs.
    """
    def __init__(self, cache_file='url_cache.json', enabled=True):
        self.cache_file = cache_file
        self.enabled = enabled
        self.cache = self._load_cache()
        
    def _load_cache(self):
        """Load cache from file"""
        try:
            with open(self.cache_file, 'r') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return {}
            
    def _save_cache(self):
        """Save cache to file"""
        if self.enabled:
            with open(self.cache_file, 'w') as f:
                json.dump(self.cache, f, indent=2)
            
    def add_url(self, url):
        """Add URL to cache with timestamp"""
        if self.enabled:
            self.cache[url] = {
                'timestamp': datetime.datetime.now().isoformat(),
                'count': self.cache.get(url, {}).get('count', 0) + 1
            }
            self._save_cache()
        
    def has_url(self, url):
        """Check if URL is in cache"""
        return url in self.cache if self.enabled else False
        
    def get_stats(self):
        """Get cache statistics"""
        if not isinstance(self.cache, dict):
            self.cache = {}  # Reset if invalid
        return {
            'total_urls': len(self.cache),
            'total_visits': sum(item.get('count', 0) for item in self.cache.values())
        }
        
    def merge(self, other_cache_file):
        """Merge another cache file into this one"""
        try:
            with open(other_cache_file, 'r') as f:
                other_cache = json.load(f)
            
            # Merge entries
            for url, data in other_cache.items():
                if url in self.cache:
                    # Update count if URL exists
                    self.cache[url]['count'] += data.get('count', 1)
                else:
                    # Add new URL
                    self.cache[url] = data
            
            self._save_cache()
            return len(other_cache)
        except (FileNotFoundError, json.JSONDecodeError) as e:
            logger.error(f"Error merging cache file {other_cache_file}: {e}")
            return 0

class CrawlResult:
    """
    Stores comprehensive results from a single page crawl.
    
    Attributes:
        url (str): Source URL of the crawled page
        success (bool): Whether the crawl was successful
        error (str): Error message if crawl failed
        html (str): Raw HTML content
        markdown (str): Processed markdown content
        links (list): Extracted links from the page
        title (str): Page title
        summary (str): Generated content summary
        keywords (list): Extracted keywords
        categories (list): Detected content categories
        last_modified (datetime): Last modification timestamp
    """
    def __init__(self):
        self.url = None
        self.success = False
        self.error = None
        self.html = None
        self.markdown = None
        self.links = []
        self.title = None
        self.summary = None
        self.keywords = []
        self.categories = []
        self.last_modified = None

async def crawl_page(url, crawler_config=None, media_dir=None):
    """
    Crawls a single page and extracts structured content.
    
    This function:
    1. Initializes browser with optimized settings
    2. Fetches and processes page content
    3. Extracts relevant links and metadata
    4. Generates clean markdown output
    
    Args:
        url (str): URL to crawl
        crawler_config (CrawlerRunConfig, optional): Custom crawler configuration
        media_dir (str, optional): Directory for media files
        
    Returns:
        CrawlResult: Structured result containing extracted content and metadata
    """
    try:
        # Configure crawler with optimized settings
        if crawler_config is None:
            crawler_config = CRAWLER_CONFIG
        
        result = CrawlResult()
        result.url = url
        
        async with AsyncWebCrawler() as crawler:
            config = crawler_config or CrawlerRunConfig(
                verbose=True,
                cache_mode=CacheMode.ENABLED,
                wait_until="networkidle"
            )
            
            # Configure media capture if requested
            if hasattr(crawler_config, 'media_options'):
                base_name = sanitize_filename(url)
                
                # Update crawler config with media options
                if 'screenshot' in crawler_config.media_options:
                    screenshot_path = os.path.join(media_dir, f"{base_name}.png")
                    crawler_config.screenshot = True
                    result.screenshot_path = screenshot_path
                
                if 'pdf' in crawler_config.media_options:
                    pdf_path = os.path.join(media_dir, f"{base_name}.pdf")
                    crawler_config.pdf = True
                    result.pdf_path = pdf_path
            
            page_result = await crawler.arun(url, crawler_config)
            
            if not page_result.success:
                result.error = page_result.error
                return result
                
            result.success = True
            result.html = page_result.html
            result.markdown = page_result.markdown
            result.links = extract_page_links(result.html, url)
            
            # Handle media capture if requested
            if hasattr(crawler_config, 'media_options'):
                if 'screenshot' in crawler_config.media_options:
                    screenshot_path = os.path.join(media_dir, f"{sanitize_filename(url)}.png")
                    try:
                        async with async_playwright() as p:
                            browser = await p.chromium.launch()
                            page = await browser.new_page()
                            await page.goto(url, wait_until='networkidle')
                            await page.screenshot(path=screenshot_path, full_page=True)
                            await browser.close()
                            result.screenshot_path = screenshot_path
                            logger.info(f"Screenshot saved to {result.screenshot_path}")
                    except Exception as e:
                        logger.warning(f"Failed to capture screenshot: {str(e)}")
                
                if 'pdf' in crawler_config.media_options:
                    pdf_path = os.path.join(media_dir, f"{sanitize_filename(url)}.pdf")
                    try:
                        async with async_playwright() as p:
                            browser = await p.chromium.launch()
                            page = await browser.new_page()
                            await page.goto(url, wait_until='networkidle')
                            await page.pdf(path=pdf_path)
                            await browser.close()
                            result.pdf_path = pdf_path
                            logger.info(f"PDF saved to {result.pdf_path}")
                    except Exception as e:
                        logger.warning(f"Failed to generate PDF: {str(e)}")
            
            return result
            
    except Exception as e:
        result.error = str(e)
        return result

async def safe_crawl(url):
    """
    Crawls a URL with built-in error handling and retry logic.
    
    Features:
    - Exponential backoff for retries
    - Handles common network errors
    - Logs failures for monitoring
    
    Args:
        url (str): URL to crawl safely
        
    Returns:
        CrawlResult: Crawl results or error information
    """
    retries = 3
    for attempt in range(retries):
        try:
            async with AsyncWebCrawler() as crawler:
                result = await crawler.arun(url=url, config=CRAWLER_CONFIG)
                if result.success:
                    logger.info(f"✅ Successfully crawled: {url}")
                    return result
                else:
                    logger.warning(f"❌ Failed to crawl {url} (attempt {attempt + 1}): {result.error}")
        except Exception as e:
            logger.error(f"Error crawling {url} (attempt {attempt + 1}): {str(e)}")
            await asyncio.sleep(2 ** attempt)  # Exponential backoff
    
    return None

def extract_page_links(html_content, base_url):
    """
    Extracts and processes links from HTML content.
    
    This function:
    1. Parses HTML with BeautifulSoup
    2. Finds all <a> tags
    3. Filters for documentation-related links
    4. Resolves relative URLs
    5. Removes duplicates
    
    Args:
        html_content (str): Raw HTML to process
        base_url (str): Base URL for resolving relative links
        
    Returns:
        list: Filtered and processed list of relevant links
    """
    soup = BeautifulSoup(html_content, 'html.parser')
    links = set()
    base_domain = urlparse(base_url).netloc

    for a in soup.find_all('a', href=True):
        href = a['href']
        if not href.startswith(('http://', 'https://')):
            href = urljoin(base_url, href)

        parsed = urlparse(href)
        if parsed.netloc == base_domain or "docs" in parsed.netloc:
            # Normalize URL by removing fragments and trailing slashes
            normalized = href.split('#')[0].rstrip('/')
            links.add(normalized)
    
    return sorted(links)

async def extract_metadata(html_content):
    """
    Extracts key metadata from HTML content.
    
    Processes:
    - Meta tags (description, keywords)
    - OpenGraph tags
    - Schema.org markup
    - Last modified dates
    - Author information
    
    Args:
        html_content (str): Raw HTML to process
        
    Returns:
        dict: Extracted metadata key-value pairs
    """
    soup = BeautifulSoup(html_content, 'html.parser')
    metadata = {
        'title': '',
        'description': '',
        'keywords': [],
        'last_modified': None
    }
    
    # Extract title
    title_tag = soup.find('title')
    if title_tag:
        metadata['title'] = title_tag.text.strip()
    
    # Extract meta tags
    for meta in soup.find_all('meta'):
        name = meta.get('name', '').lower()
        content = meta.get('content', '')
        
        if name == 'description':
            metadata['description'] = content
        elif name == 'keywords':
            metadata['keywords'] = [k.strip() for k in content.split(',')]
        elif name == 'last-modified':
            try:
                metadata['last_modified'] = datetime.datetime.fromisoformat(content)
            except:
                pass
    
    return metadata

def sanitize_filename(url):
    """
    Converts a URL into a safe filename for storage.
    
    This function:
    1. Removes unsafe characters
    2. Handles URL encoding
    3. Limits filename length
    4. Ensures unique names
    5. Preserves important URL parts
    
    Args:
        url (str): URL to convert
        
    Returns:
        str: Safe filename for the URL
    """
    # Parse URL
    parsed = urlparse(url)
    
    # Get domain and path parts
    domain = parsed.netloc
    path_parts = parsed.path.strip('/').split('/')
    
    # Handle empty path or trailing slash
    if not path_parts or not path_parts[0]:
        path_parts = ['index']
    
    # Clean up each part
    clean_parts = []
    for part in path_parts:
        # Remove URL parameters
        part = part.split('?')[0]
        # Replace unsafe characters
        part = re.sub(r'[<>:"/\\|?*]', '_', part)
        # Limit length
        if len(part) > 50:
            part = part[:47] + '...'
        clean_parts.append(part)
    
    # Join with underscores and add domain
    return f"{domain}_{'_'.join(clean_parts)}"

async def save_readable_text(markdown_content, include_links=True, include_sections=True):
    """
    Extracts and saves clean readable text from markdown content.
    
    This function:
    1. Processes markdown to plain text
    2. Preserves important formatting
    3. Handles links appropriately
    4. Maintains section structure
    5. Creates clean output files
    
    Args:
        markdown_content (str): Source markdown
        include_links (bool): Whether to include links at end
        include_sections (bool): Whether to preserve sections
    """
    if not markdown_content:
        return
        
    # Basic cleanup of markdown syntax
    text = markdown_content
    
    # Remove code blocks (both inline and multi-line)
    text = re.sub(r'```[^`]*```', '', text)  # Remove multi-line code blocks
    text = re.sub(r'`[^`]+`', '', text)  # Remove inline code
    
    # Handle links based on preference
    if include_links:
        # Convert links to text with footnotes
        links = []
        def link_replace(match):
            text, url = match.groups()
            links.append(url)
            return f"{text} [{len(links)}]"
        text = re.sub(r'\[([^\]]+)\]\(([^\)]+)\)', link_replace, text)
    else:
        # Just keep link text, remove URLs
        text = re.sub(r'\[([^\]]+)\]\([^\)]+\)', r'\1', text)
    
    # Remove headers and formatting
    text = re.sub(r'#{1,6}\s+', '', text)  # Remove headers
    text = re.sub(r'\*\*([^\*]+)\*\*', r'\1', text)  # Remove bold
    text = re.sub(r'\*([^\*]+)\*', r'\1', text)  # Remove italic
    text = re.sub(r'_([^_]+)_', r'\1', text)  # Remove underscores
    
    # Clean up lists
    text = re.sub(r'\n\s*[-\*\+]\s+', '\n• ', text)  # Convert unordered lists to bullets
    text = re.sub(r'\n\s*\d+\.\s+', '\n• ', text)  # Convert ordered lists to bullets
    
    # Clean up whitespace
    text = re.sub(r'\n{3,}', '\n\n', text)  # Normalize multiple newlines
    text = re.sub(r'[ \t]+', ' ', text)  # Normalize spaces and tabs
    
    # Add section breaks if requested
    if include_sections:
        text = re.sub(r'\n\n+', '\n\n---\n\n', text)
    
    # Add collected links as footnotes
    if include_links and links:
        text += '\n\nReferences:\n'
        for i, url in enumerate(links, 1):
            text += f'[{i}] {url}\n'
    
    return text

async def extract_readable_text(markdown_content):
    """
    Converts markdown to clean readable text.
    
    Processing steps:
    1. Strip markdown syntax
    2. Preserve paragraph structure
    3. Handle special elements (lists, code)
    4. Clean up whitespace
    5. Format for readability
    
    Args:
        markdown_content (str): Source markdown
        
    Returns:
        str: Clean readable text
    """
    # Remove code blocks
    text = re.sub(r'```[\s\S]*?```', '', markdown_content)
    text = re.sub(r'`[^`]+`', '', text)
    
    # Remove URLs and links but keep link text
    text = re.sub(r'\[([^\]]+)\]\([^\)]+\)', r'\1', text)
    text = re.sub(r'https?://\S+', '', text)
    
    # Remove HTML tags
    text = re.sub(r'<[^>]+>', '', text)
    
    # Remove special characters and normalize whitespace
    text = re.sub(r'[=\-\*•◦○●\[\]]+', '', text)
    text = re.sub(r'\s+', ' ', text)
    
    # Fix common encoding issues
    text = text.replace('â€™', "'")
    text = text.replace('â€"', "-")
    text = text.replace('â€œ', '"')
    text = text.replace('â€', '"')
    text = text.replace('â€¢', '•')
    text = text.replace('ðŸ˜…', '')  # Remove emojis
    
    # Split into paragraphs and clean each one
    paragraphs = []
    for p in text.split('\n'):
        p = p.strip()
        if p and len(p) > 20 and not is_navigation_text(p):
            paragraphs.append(p)
    
    return '\n\n'.join(paragraphs)

async def create_condensed_summary(content, metadata):
    """
    Creates a condensed hierarchical summary of the content.
    
    This function:
    1. Extracts key topics and themes
    2. Identifies main points
    3. Organizes into hierarchy
    4. Integrates metadata
    5. Generates concise overview
    
    Args:
        content (str): Full content to summarize
        metadata (dict): Additional page metadata
        
    Returns:
        dict: Structured summary with core message and key points
    """
    if not content:
        return None
        
    # First clean and extract readable text
    content = await extract_readable_text(content)
    if not content:
        return None
    
    # Split into paragraphs
    paragraphs = [p for p in content.split('\n\n') if p.strip()]
    if not paragraphs:
        return None
    
    # Extract core message from the first substantial paragraph
    core_message = ""
    for p in paragraphs:
        words = p.split()
        if len(words) >= 10:  # Look for a substantial paragraph
            core_message = ' '.join(words[:25])
            if not core_message.endswith(('.',',','!','?')):
                core_message += '...'
            break
    
    # Extract key points from subsequent paragraphs
    key_points = []
    for p in paragraphs[1:]:
        # Skip very short paragraphs and navigation-like content
        if len(p.split()) < 8 or is_navigation_text(p):
            continue
        
        # Clean and add the point
        if len(key_points) >= 5:  # Limit to 5 key points
            break
        key_points.append(p)
    
    # Extract technical terms
    tech_terms = []
    raw_terms = extract_technical_terms(content)
    for term in raw_terms:
        if len(tech_terms) >= 5:  # Limit to 5 terms
            break
        if len(term) > 2 and not is_navigation_text(term):
            tech_terms.append(term)
    
    # Create the condensed summary structure
    summary = {
        "title": metadata.get("title", "").strip(),
        "core_message": core_message,
        "key_points": key_points,
        "technical_terms": tech_terms
    }
    
    return summary

async def save_knowledge_base_entry(content, kb_root=None, kb_category=None):
    """
    Saves content in a structured knowledge base format.
    
    This function:
    1. Organizes content hierarchically
    2. Adds metadata and categories
    3. Creates consistent structure
    4. Handles file organization
    5. Maintains KB integrity
    
    Args:
        content (str): Content to save
        kb_root (str, optional): Knowledge base root path
        kb_category (str, optional): Content category
    """
    if kb_root and kb_category:
        kb_dir = os.path.join(kb_root, kb_category)
        os.makedirs(kb_dir, exist_ok=True)
    else:
        kb_dir = os.getcwd()
    
    # Create knowledge base structure with enhanced metadata
    kb_entry = {
        'url': content.url,
        'timestamp': datetime.datetime.now(datetime.timezone.utc).isoformat(),
        'title': content.title,
        'categories': content.categories,
        'summary': content.summary,
        'keywords': content.keywords,
        'last_modified': content.last_modified,
        'metadata': {
            'type': 'technical_documentation',
            'contains_code_examples': bool(re.search(r'```', content.markdown)),
            'contains_steps': bool(re.search(r'^\s*(?:\d+\.|[-\*\+])\s+', content.markdown, re.M)),
            'programming_languages': list(set(re.findall(r'```(\w+)', content.markdown))),
            'technical_terms': extract_technical_terms(content.markdown)
        },
        'content': {
            'html': content.html,
            'markdown': content.markdown,
            'structured_text': await extract_readable_text(content.markdown)
        },
        'links': content.links,
        'references': []
    }
    
    # Save as JSON
    kb_file = os.path.join(kb_dir, 'kb_entry.json')
    with open(kb_file, 'w', encoding='utf-8') as f:
        json.dump(kb_entry, f, indent=2, ensure_ascii=False)
    
    # Save LLM-friendly version
    text_file = os.path.join(kb_dir, 'llm_instructions.txt')
    with open(text_file, 'w', encoding='utf-8') as f:
        f.write(f"{content.title}\n{'=' * len(content.title)}\n\n")
        
        if content.summary:
            f.write(f"Purpose\n-------\n{content.summary}\n\n")
        
        if content.keywords:
            f.write(f"Technical Scope\n--------------\n{', '.join(content.keywords) if content.keywords else 'None'}\n\n")
        
        f.write(await extract_readable_text(content.markdown))
        
        if content.links:
            f.write("\nRelated Documentation\n--------------------\n")
            for link in content.links:
                f.write(f"• {link}\n")

async def save_unified_knowledge(content, kb_root=None, kb_category=None):
    """
    Saves content in a format optimized for both LLMs and humans.
    
    This function:
    1. Structures content for dual use
    2. Preserves semantic relationships
    3. Adds metadata and context
    4. Organizes hierarchically
    5. Maintains searchability
    
    Args:
        content (str): Content to save
        kb_root (str, optional): Knowledge base root
        kb_category (str, optional): Content category
    """
    if kb_root and kb_category:
        kb_dir = os.path.join(kb_root, kb_category)
        os.makedirs(kb_dir, exist_ok=True)
    else:
        kb_dir = os.getcwd()

    # Generate specific filename from content
    filename = get_safe_filename(content.title, content.url)
    unified_file = os.path.join(kb_dir, f'{filename}.md')
    
    with open(unified_file, 'w', encoding='utf-8') as f:
        # Document Header
        f.write(f"# {content.title}\n\n")
        
        # Metadata Section
        f.write("## 📚 Document Metadata\n\n")
        f.write("```yaml\n")
        f.write(f"title: {content.title}\n")
        f.write(f"source_url: {content.url}\n")
        f.write(f"category: {'/'.join(content.categories) if content.categories else 'Uncategorized'}\n")
        f.write(f"keywords: {', '.join(content.keywords) if content.keywords else 'None'}\n")
        f.write(f"last_modified: {content.last_modified or 'Unknown'}\n")
        f.write(f"type: Technical Documentation\n")
        f.write("```\n\n")

        # Quick Summary
        if content.summary:
            f.write("## 📋 Quick Summary\n\n")
            f.write(f"{content.summary}\n\n")

        # Technical Context
        f.write("## 🔧 Technical Context\n\n")
        code_langs = list(set(re.findall(r'```(\w+)', content.markdown)))
        if code_langs:
            f.write("### Programming Languages\n")
            for lang in code_langs:
                f.write(f"- {lang}\n")
            f.write("\n")

        tech_terms = extract_technical_terms(content.markdown)
        if tech_terms:
            f.write("### Key Technical Terms\n")
            for term in tech_terms:
                f.write(f"- {term}\n")
            f.write("\n")

        # Main Content
        f.write("## 📖 Main Content\n\n")
        
        # Process content by sections
        sections = []
        current_section = {"level": 0, "title": "", "content": [], "parameters": []}
        code_blocks = []
        
        for line in content.markdown.split('\n'):
            header_match = re.match(r'^(#{1,6})\s+(.+)$', line)
            if header_match:
                if current_section:
                    sections.append((current_header, '\n'.join(current_section)))
                current_header = (len(header_match.group(1)), header_match.group(2))
                current_section = []
            else:
                current_section.append(line)
        
        if current_section:
            sections.append((current_header, '\n'.join(current_section)))

        # Process each section
        for header, section_content in sections:
            if header:
                level, title = header
                f.write(f"{'#' * (level + 2)} {title}\n\n")  # Adjust header level

            # Extract and format code blocks
            code_pattern = r'```(\w+)?\n(.*?)```'
            code_blocks = list(re.finditer(code_pattern, section_content, re.DOTALL))
            
            # Replace code blocks with placeholders and store them
            code_replacements = []
            for i, match in enumerate(code_blocks):
                lang = match.group(1) or 'text'
                code = match.group(2).strip()
                placeholder = f"__CODE_BLOCK_{i}__"
                code_replacements.append((placeholder, f"Code Example ({lang}):\n```{lang}\n{code}\n```\n"))
                section_content = section_content.replace(match.group(0), placeholder)

            # Process steps and instructions
            lines = section_content.split('\n')
            in_steps = False
            processed_lines = []
            
            for line in lines:
                if re.match(r'^\s*(?:\d+\.|[-\*\+])\s+', line):
                    if not in_steps:
                        in_steps = True
                        processed_lines.append("\n🔍 Instructions:\n")
                    processed_lines.append(re.sub(r'^\s*(?:\d+\.|[-\*\+])\s+', '• ', line))
                else:
                    if in_steps:
                        in_steps = False
                        processed_lines.append("")
                    processed_lines.append(line)
            
            section_content = '\n'.join(processed_lines)

            # Add semantic markup
            section_content = re.sub(r'\*\*([^\*]+)\*\*', r'❗ Important: \1', section_content)
            section_content = re.sub(r'\*([^\*]+)\*', r'💡 Note: \1', section_content)
            section_content = re.sub(r'`([^`]+)`', r'`\1`', section_content)

            # Restore code blocks
            for placeholder, code_block in code_replacements:
                section_content = section_content.replace(placeholder, f"\n{code_block}\n")

            f.write(f"{section_content}\n\n")

        # Related Resources
        if content.links:
            f.write("## 🔗 Related Resources\n\n")
            for link in content.links:
                f.write(f"- [{link}]({link})\n")

        # Training Notes for LLMs
        f.write("\n## 🤖 LLM Training Notes\n\n")
        f.write("This document is structured for both human readability and LLM training:\n\n")
        f.write("1. 📚 **Metadata Section**: Contains document classification and context\n")
        f.write("2. 📋 **Quick Summary**: High-level overview of the content\n")
        f.write("3. 🔧 **Technical Context**: Programming languages and key terms\n")
        f.write("4. 📖 **Main Content**: Organized with:\n")
        f.write("   - Clear section headers\n")
        f.write("   - Code examples with language tags\n")
        f.write("   - Step-by-step instructions\n")
        f.write("   - Important points and notes clearly marked\n")
        f.write("5. 🔗 **Related Resources**: Links to additional information\n\n")
        f.write("Special markers used:\n")
        f.write("- ❗ Important: Critical information\n")
        f.write("- 💡 Note: Additional context\n")
        f.write("- 🔍 Instructions: Step-by-step procedures\n")
        f.write("- ```language: Code blocks with language specification\n")

    return unified_file

async def save_to_knowledge_base(result, kb_root=None, format=SummaryFormat.STANDARD):
    """
    Saves extracted content in structured knowledge base format.
    
    This function:
    1. Processes crawl results
    2. Extracts key information
    3. Organizes content
    4. Adds metadata
    5. Maintains KB structure
    
    Args:
        result (CrawlResult): Crawl results to save
        kb_root (str, optional): Knowledge base root path
        format (SummaryFormat): Output format to use
        
    Returns:
        str: Path to saved markdown file
        
    Raises:
        StorageError: If saving content fails
        ProcessingError: If content processing fails
    """
    try:
        if not result or not result.success:
            raise ProcessingError("Invalid or failed crawl result", {
                "url": result.url if result else None,
                "error": result.error if result else None
            })
            
        # Create output directory
        if kb_root:
            os.makedirs(kb_root, exist_ok=True)
        
        # Generate base filename from URL
        base_name = sanitize_filename(result.url)
        
        # Save markdown file
        md_path = os.path.join(kb_root, f"{base_name}.md")
        with open(md_path, 'w', encoding='utf-8') as f:
            f.write(result.markdown)
            
            # Add media references if they exist
            if hasattr(result, 'screenshot_path') or hasattr(result, 'pdf_path'):
                f.write("\n\n## 📎 Media Files\n\n")
                if hasattr(result, 'screenshot_path'):
                    rel_path = os.path.relpath(result.screenshot_path, kb_root)
                    f.write(f"- [📸 Screenshot]({rel_path})\n")
                if hasattr(result, 'pdf_path'):
                    rel_path = os.path.relpath(result.pdf_path, kb_root)
                    f.write(f"- [📄 PDF Version]({rel_path})\n")
            
        # Only save metadata as JSON for standard format
        if format == SummaryFormat.STANDARD:
            # Extract title from HTML if available
            title = "Untitled"
            try:
                soup = BeautifulSoup(result.html, "html.parser")
                if soup.find("title"):
                    title = soup.find("title").text.strip()
            except:
                pass
                
            metadata = {
                "url": result.url,
                "title": title,
                "timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat(),
                "word_count": len(result.markdown.split()) if result.markdown else 0,
                "summary": result.summary if hasattr(result, "summary") else None,
                "last_modified": result.last_modified.isoformat() if hasattr(result, "last_modified") and result.last_modified else None,
                "media": {
                    "screenshot": result.screenshot_path if hasattr(result, "screenshot_path") else None,
                    "pdf": result.pdf_path if hasattr(result, "pdf_path") else None
                }
            }
            
            json_path = os.path.join(kb_root, f"{base_name}.json")
            with open(json_path, 'w', encoding='utf-8') as f:
                json.dump(metadata, f, indent=2, ensure_ascii=False)
            
        return md_path
            
    except Exception as e:
        raise StorageError(f"Failed to save content: {str(e)}", {
            "url": result.url if result else None,
            "kb_root": kb_root,
            "error": str(e)
        })

async def crawl_docs(urls, output_dir, page_limit=None, format=SummaryFormat.STANDARD, media_options=None):
    """
    Crawls documentation pages and saves structured content.
    
    This function:
    1. Processes multiple URLs
    2. Manages crawl progress
    3. Handles rate limiting
    4. Saves structured output
    5. Maintains organization
    
    Args:
        urls (list): URLs to crawl
        output_dir (str): Output directory
        page_limit (int, optional): Maximum pages to process
        format (SummaryFormat): Output format to use
        media_options (list, optional): Media to capture (screenshots, pdf, or all)
    """
    try:
        # Create output directory if it doesn't exist
        os.makedirs(output_dir, exist_ok=True)
        
        # Create media directory if needed
        if media_options:
            media_dir = os.path.join(output_dir, "media")
            os.makedirs(media_dir, exist_ok=True)
        else:
            media_dir = None
        
        # Configure crawler
        crawler_config = CRAWLER_CONFIG
        if media_options:
            crawler_config.media_options = media_options
        
        # Initialize progress bar with more details
        total_urls = len(urls)
        with tqdm(total=total_urls, 
                 desc="Processing pages", 
                 unit="page",
                 bar_format="\r{desc} |{bar:50}| {percentage:3.0f}% • {n_fmt}/{total_fmt} [{elapsed}<{remaining}] {postfix}",
                 ncols=120,
                 position=0,
                 leave=True,
                 dynamic_ncols=True,
                 ascii=True) as pbar:  # Use ASCII for better compatibility
            
            for url in urls:
                # Update description with current URL (shortened)
                url_short = os.path.basename(url)[:20]
                pbar.set_description(f"Processing {url_short:<20}")
                pbar.refresh()  # Force refresh of progress bar
                
                try:
                    # Crawl the page
                    result = await crawl_page(url, crawler_config, media_dir)
                    
                    if result.success:
                        # Save to knowledge base
                        await save_to_knowledge_base(result, output_dir, format)
                        pbar.set_postfix_str("✓ Done")
                        logger.info(f"Successfully processed {url}")
                    else:
                        pbar.set_postfix_str("✗ Failed")
                        logger.error(f"Failed to process {url}: {result.error}")
                    
                except Exception as e:
                    pbar.set_postfix_str("! Error")
                    logger.error(f"Error processing {url}: {str(e)}")
                    continue
                
                # Update progress
                pbar.update(1)
                pbar.refresh()  # Force refresh after update
                
            # Clear progress bar on completion
            pbar.clear()
                
    except Exception as e:
        logger.error(f"Error in crawl_docs: {str(e)}")
        raise

async def extract_documentation(url):
    """
    Extract documentation with optimized settings.
    
    This function:
    1. Uses best-practice configuration
    2. Handles common doc formats
    3. Extracts structured content
    4. Processes metadata
    5. Returns clean output
    
    Args:
        url (str): Documentation URL to process
        
    Returns:
        CrawlResult: Extracted documentation content
    """
    config = get_default_config()
    
    browser_config = BrowserConfig(**config['browser_config'])
    crawler_config = CrawlerRunConfig(**config['crawler_config'])
    
    async with AsyncWebCrawler(browser_config) as crawler:
        result = await crawler.arun(url=url, config=crawler_config)
        return result

async def main():
    """
    Main entry point for the documentation crawler.
    
    This function:
    1. Parses command line arguments
    2. Sets up configuration
    3. Processes input URLs
    4. Manages output
    5. Handles errors
    """
    parser = argparse.ArgumentParser(description='Crawl and summarize web content')
    parser.add_argument('urls', nargs='+', help='URLs to crawl')
    parser.add_argument('--output-dir', '-o', default='crawl_output', help='Output directory')
    parser.add_argument('--page-limit', '-l', type=int, help='Maximum pages to crawl')
    parser.add_argument('--format', '-f', choices=['standard', 'condensed'], default='standard', help='Summary format')
    parser.add_argument('--media', '-m', choices=['screenshots', 'pdf', 'all'], help='Media to capture (screenshots, pdf, or all)')
    parser.add_argument('--test', action='store_true', help='Test mode - crawl single page')
    parser.add_argument('--debug', action='store_true', help='Enable debug logging')
    
    args = parser.parse_args()
    
    # Configure logging
    log_level = logging.DEBUG if args.debug else logging.INFO
    logging.basicConfig(
        level=log_level,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )
    
    try:
        # Create output directory
        output_dir = os.path.abspath(args.output_dir)
        os.makedirs(output_dir, exist_ok=True)
        
        # Create media directory if needed
        media_dir = None
        if args.media:
            media_dir = os.path.join(output_dir, 'media')
            os.makedirs(media_dir, exist_ok=True)
        
        # Configure crawler
        config = CrawlerRunConfig(
            verbose=args.debug,
            cache_mode=CacheMode.ENABLED,
            wait_until="networkidle",
            page_timeout=30000
        )
        
        # Configure media options
        if args.media:
            config.media_options = set()
            if args.media in ['screenshots', 'all']:
                config.media_options.add('screenshot')
            if args.media in ['pdf', 'all']:
                config.media_options.add('pdf')
        
        if args.test:
            # Test mode - single page
            result = await crawl_page(args.urls[0], config, media_dir)
            if not result.success:
                logger.error(f"Failed to process {args.urls[0]}: {result.error}")
                sys.exit(1)
            await save_to_knowledge_base(result, output_dir, SummaryFormat[args.format.upper()])
        else:
            # Normal mode - process all URLs
            await crawl_docs(args.urls, output_dir, args.page_limit, SummaryFormat[args.format.upper()], args.media)
            
    except Exception as e:
        logger.error(f"Error: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())

def process_url(url, kb_root=None, test=False):
    """
    Process a single URL.
    
    This function:
    1. Validates input URL
    2. Configures processing
    3. Extracts content
    4. Saves output
    5. Returns results
    
    Args:
        url (str): URL to process
        kb_root (str, optional): Knowledge base root path
        test (bool): Whether this is a test run
        
    Returns:
        CrawlResult: Processing results
    """
    if not url:
        return None
    
    if not kb_root:
        kb_root = os.path.join(os.getcwd(), "output")
    os.makedirs(kb_root, exist_ok=True)
    
    # Extract content
    result = extract_documentation(url)
    if not result or not result.success:
        return None
    
    # Save to knowledge base
    output_file = save_to_knowledge_base(result, kb_root)  # Not async
    return output_file

def process_markdown(result):
    """
    Process markdown result.
    
    This function:
    1. Cleans markdown content
    2. Formats code blocks
    3. Handles special syntax
    4. Normalizes structure
    5. Improves readability
    
    Args:
        result (CrawlResult): Result containing markdown
        
    Returns:
        str: Processed markdown content
        
    Raises:
        ProcessingError: If result is invalid or processing fails
    """
    if not result:
        raise ProcessingError("Invalid or failed crawl result")
    
    if not result.success:
        raise ProcessingError("Failed crawl result", {"error": result.error})
    
    # Process markdown
    markdown = result.markdown
    if not markdown:
        raise ProcessingError("No markdown content in result")
    
    # Clean and format
    try:
        markdown = clean_markdown(markdown)
        markdown = process_markdown_content(markdown)
        return markdown
    except Exception as e:
        raise ProcessingError("Failed to process markdown", {"error": str(e)})

def clean_markdown(markdown):
    """
    Clean and normalize markdown content.
    
    This function:
    1. Removes redundant whitespace
    2. Normalizes line endings
    3. Fixes common formatting issues
    4. Ensures consistent structure
    5. Preserves important whitespace
    
    Args:
        markdown (str): Raw markdown content
        
    Returns:
        str: Cleaned markdown content
    """
    if not markdown:
        return ""
    
    # Normalize line endings
    markdown = markdown.replace('\r\n', '\n')
    
    # Fix common formatting issues
    markdown = re.sub(r'\n{3,}', '\n\n', markdown)  # Remove excess newlines
    markdown = re.sub(r'[ \t]+\n', '\n', markdown)  # Remove trailing whitespace
    
    # Ensure proper spacing around headers
    markdown = re.sub(r'(\n#{1,6}.*?)\n([^\n])', r'\1\n\n\2', markdown)
    
    return markdown.strip()

def process_markdown_content(markdown):
    """
    Process markdown content for improved readability.
    
    This function:
    1. Formats code blocks
    2. Adjusts list indentation
    3. Normalizes headers
    4. Fixes link formatting
    5. Ensures consistent spacing
    
    Args:
        markdown (str): Raw markdown content
        
    Returns:
        str: Processed markdown content
    """
    if not markdown:
        return ""
    
    lines = markdown.split('\n')
    processed_lines = []
    in_code_block = False
    code_block_content = []
    
    for line in lines:
        if line.strip().startswith('```'):
            if in_code_block:
                # End of code block
                code_content = '\n'.join(code_block_content)
                formatted_code = format_code_block(code_content)
                processed_lines.append('```python')  # Always use python for code blocks
                processed_lines.extend(formatted_code.split('\n'))
                processed_lines.append('```')
                code_block_content = []
                in_code_block = False
            else:
                # Start of code block
                in_code_block = True
        elif in_code_block:
            code_block_content.append(line)
        else:
            # Process non-code content
            line = re.sub(r'^(\s*[-*+]\s+)', r'* ', line)  # Normalize list markers
            line = re.sub(r'^(\s*\d+\.\s+)', r'1. ', line)  # Normalize numbered lists
            processed_lines.append(line)
    
    # Handle unclosed code block
    if in_code_block and code_block_content:
        code_content = '\n'.join(code_block_content)
        formatted_code = format_code_block(code_content)
        processed_lines.append('```python')
        processed_lines.extend(formatted_code.split('\n'))
        processed_lines.append('```')
    
    return '\n'.join(processed_lines)

if __name__ == "__main__":
    asyncio.run(main())
