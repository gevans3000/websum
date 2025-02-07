#!/usr/bin/env python3
import os
import sys
import json
import logging
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
from crawl4ai.extraction_strategy import ExtractionStrategy, CosineStrategy
from io import StringIO
from contextlib import redirect_stdout, redirect_stderr
from bs4 import BeautifulSoup, NavigableString
from enum import Enum, auto
import datetime
import time

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Constants
VERSION = "1.0.0"

# Browser configuration
BROWSER_CONFIG = BrowserConfig(
    browser_type="chromium",
    headless=True,
    viewport_width=1920,
    viewport_height=1080,
    user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    ignore_https_errors=True
)

# Crawler configuration
CRAWLER_CONFIG = CrawlerRunConfig(
    word_count_threshold=3,
    scan_full_page=True,
    wait_until="networkidle",  # Wait for full JS execution
    page_timeout=90000,  # 90 sec timeout for large pages
    css_selector=".md-content__inner, .md-typeset, table.docutils, pre code",
    process_iframes=True,
    remove_overlay_elements=True,
    cache_mode=CacheMode.BYPASS,
    exclude_external_links=False
)

# Markdown generator with enhanced formatting
MARKDOWN_GENERATOR = DefaultMarkdownGenerator(
    options={
        "preserve_tables": True,  # Keeps technical parameter tables
        "retain_code_blocks": True,  # Preserves syntax-highlighted code
        "escape_html": False,  # Avoids unnecessary escaping
        "inline_code_format": "backticks",
        "strip_comments": True  
    }
)

class SummaryFormat(Enum):
    STANDARD = auto()
    CONDENSED = auto()

# Memory and performance optimization
os.environ["CRAWL4AI_MAX_BUFFER_SIZE"] = "1000000"  # 1MB buffer
os.environ["CRAWL4AI_CHUNK_SIZE"] = "524288"  # 512KB chunks
os.environ["CRAWL4AI_STREAM_MODE"] = "True"

# Content extraction strategy
EXTRACTION_STRATEGY = CosineStrategy(
    target_content_type="documentation",
    word_count_threshold=10,
    similarity_threshold=0.7
)

class CrawlProgress:
    """Track crawl progress"""
    def __init__(self, page_limit=None):
        self.page_limit = page_limit
        self.pages_processed = 0
        self.start_time = None
        
    def should_process_more(self):
        """Check if we should process more pages"""
        if self.page_limit is None:
            return True
        return self.pages_processed < self.page_limit
    
    def update(self):
        """Update progress after processing a page"""
        self.pages_processed += 1

class RateLimiter:
    """Simple rate limiter to prevent overwhelming servers"""
    def __init__(self, delay_seconds=1.0):
        self.delay = delay_seconds
        self.last_request = 0
        
    async def wait(self):
        """Wait if needed to maintain rate limit"""
        now = time.time()
        elapsed = now - self.last_request
        if elapsed < self.delay:
            await asyncio.sleep(self.delay - elapsed)
        self.last_request = time.time()

class URLCache:
    """Simple cache to track processed URLs"""
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
    """Store crawl results"""
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

async def crawl_page(url, crawler_config=None):
    """Crawl a page and return structured content"""
    try:
        # Configure browser for optimal content extraction
        browser_config = BROWSER_CONFIG
        
        # Configure crawler with optimized settings
        if crawler_config is None:
            crawler_config = CRAWLER_CONFIG
        
        result = CrawlResult()
        result.url = url
        
        async with AsyncWebCrawler(browser_config) as crawler:
            crawl_result = await crawler.arun(url=url, config=crawler_config)
            
            if crawl_result.success:
                result.success = True
                result.html = crawl_result.html
                result.markdown = crawl_result.markdown
                result.links = crawl_result.links if hasattr(crawl_result, 'links') else []
                
                # Extract metadata if HTML is available
                if result.html:
                    soup = BeautifulSoup(result.html, 'html.parser')
                    
                    # Extract title
                    title_elem = soup.find('title')
                    if title_elem:
                        result.title = title_elem.text.strip()
                    
                    # Extract meta description as summary
                    meta_desc = soup.find('meta', {'name': 'description'})
                    if meta_desc:
                        result.summary = meta_desc.get('content', '')
                    
                    # Extract keywords
                    meta_keywords = soup.find('meta', {'name': 'keywords'})
                    if meta_keywords:
                        result.keywords = [k.strip() for k in meta_keywords.get('content', '').split(',')]
                    
                    # Extract last modified date
                    meta_modified = soup.find('meta', {'name': 'last-modified'})
                    if meta_modified:
                        result.last_modified = meta_modified.get('content', '')
            else:
                result.error = crawl_result.error if hasattr(crawl_result, 'error') else "Unknown error"
                
        return result
        
    except Exception as e:
        logger.error(f"Error crawling {url}: {str(e)}")
        result = CrawlResult()
        result.url = url
        result.error = str(e)
        return result

async def safe_crawl(url):
    """Crawl a URL with retries and exponential backoff"""
    retries = 3
    for attempt in range(retries):
        try:
            async with AsyncWebCrawler(browser_config=BROWSER_CONFIG) as crawler:
                result = await crawler.arun(url, config=CRAWLER_CONFIG)
                if result.success:
                    logger.info(f"✅ Successfully crawled: {url}")
                    return result
                else:
                    logger.warning(f"⚠️ Attempt {attempt+1}/{retries} failed for {url}: {result.error}")
        except Exception as e:
            logger.error(f"❌ Error crawling {url}: {str(e)}")
            if attempt < retries - 1:
                await asyncio.sleep(2 ** attempt)  # Exponential backoff
    logger.error(f"⛔ Failed to crawl {url} after {retries} attempts.")
    return None

def extract_page_links(html_content, base_url):
    """Extract relevant documentation links from HTML content."""
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

def extract_metadata(html_content):
    """Extract metadata from HTML content"""
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
    """Convert URL to safe filename"""
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

def save_readable_text(markdown_content, output_path, include_links=True, include_sections=True):
    """
    Extract and save clean readable text from markdown content.
    Args:
        markdown_content (str): The markdown content to process
        output_path (str): Path to save the readable text file
        include_links (bool): Whether to include links as a list at the end
        include_sections (bool): Whether to add section breaks (---)
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
    
    # Save the clean text
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(text.strip())

def extract_readable_text(markdown_content):
    """Extract clean readable text from markdown content"""
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

def create_condensed_summary(content, metadata):
    """
    Creates a condensed hierarchical summary of the content
    Args:
        content (str): The full content to summarize
        metadata (dict): Metadata extracted from the page
    Returns:
        dict: Structured summary with core message, key points, and metadata
    """
    if not content:
        return None
        
    # First clean and extract readable text
    content = extract_readable_text(content)
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

def save_knowledge_base_entry(content, output_dir, kb_root=None, kb_category=None):
    """Save content in knowledge base format"""
    if kb_root and kb_category:
        kb_dir = os.path.join(kb_root, kb_category)
        os.makedirs(kb_dir, exist_ok=True)
    else:
        kb_dir = output_dir
    
    # Create knowledge base structure with enhanced metadata
    kb_entry = {
        'url': content.url,
        'timestamp': datetime.datetime.now().isoformat(),
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
            'structured_text': extract_readable_text(content.markdown)
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
        
        f.write(extract_readable_text(content.markdown))
        
        if content.links:
            f.write("\nRelated Documentation\n--------------------\n")
            for link in content.links:
                f.write(f"• {link}\n")

def extract_technical_terms(text):
    """Extract likely technical terms from the content"""
    # Common technical word patterns
    patterns = [
        r'\b[A-Z][a-z]+(?:[A-Z][a-z]+)+\b',  # CamelCase
        r'\b[a-z]+_[a-z_]+\b',  # snake_case
        r'`[^`]+`',  # Code in backticks
        r'\b(?:API|REST|HTTP|JSON|XML|HTML|CSS|URL|SDK|CLI)\b',  # Common acronyms
        r'\b(?:function|class|method|object|variable|parameter)\b'  # Programming terms
    ]
    
    terms = set()
    for pattern in patterns:
        terms.update(re.findall(pattern, text))
    
    return list(terms)

def get_safe_filename(title, url):
    """Generate a safe, descriptive filename from title and URL"""
    # Extract meaningful parts from URL
    url_path = urlparse(url).path.strip('/')
    url_parts = [part for part in url_path.split('/') if part]
    
    # Clean the title
    if not title:
        title = url_parts[-1] if url_parts else "untitled"
    
    # Remove version numbers and common words
    title = re.sub(r'\s*[-–—]\s*(?:v\d+\.\d+\.\d+\w*|Documentation|\(.*?\))', '', title)
    title = re.sub(r'\s+', '_', title.strip())
    
    # Create safe filename
    safe_chars = re.sub(r'[^a-zA-Z0-9_-]', '', title.lower())
    safe_chars = re.sub(r'_+', '_', safe_chars)
    
    return safe_chars

def save_unified_knowledge(content, output_dir, kb_root=None, kb_category=None):
    """Save content in a unified format for both LLMs and humans"""
    if kb_root and kb_category:
        kb_dir = os.path.join(kb_root, kb_category)
        os.makedirs(kb_dir, exist_ok=True)
    else:
        kb_dir = output_dir

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

def save_to_knowledge_base(result, output_dir):
    """Save extracted content in structured knowledge base format."""
    if not result or not result.success:
        return None

    # Parse HTML with BeautifulSoup
    soup = BeautifulSoup(result.html, "html.parser")

    # Extract Title
    title = soup.find("title").text.strip() if soup.find("title") else "Untitled"

    # Extract metadata
    metadata = {
        "url": result.url,
        "title": title,
        "timestamp": datetime.datetime.now().isoformat(),
        "word_count": len(result.markdown.split()),
        "summary": result.markdown[:500],  # First 500 chars
        "last_modified": soup.find("meta", attrs={"name": "last-modified"})["content"] if soup.find("meta", attrs={"name": "last-modified"}) else None,
        "links": extract_page_links(result.html, result.url)
    }

    # Create safe filename
    safe_title = "".join(c if c.isalnum() or c in " _-" else "_" for c in title)[:50]

    # Save extracted Markdown
    markdown_file = os.path.join(output_dir, safe_title + ".md")
    with open(markdown_file, "w", encoding="utf-8") as f:
        f.write(f"# {title}\n\n")
        f.write(f"URL: {result.url}\n")
        f.write(f"Extracted: {metadata['timestamp']}\n\n")
        f.write("-" * 80 + "\n\n")
        f.write(result.markdown)

    # Save metadata as JSON
    json_file = os.path.join(output_dir, safe_title + ".json")
    with open(json_file, "w", encoding="utf-8") as f:
        json.dump(metadata, f, indent=2)

    logger.info(f"📄 Saved: {markdown_file}, 📊 Metadata: {json_file}")
    return markdown_file

def clean_text(text):
    """Clean text by removing special characters and normalizing whitespace"""
    # Remove markdown links
    text = re.sub(r'\[([^\]]+)\]\([^\)]+\)', r'\1', text)
    
    # Remove special characters and normalize whitespace
    text = re.sub(r'[=\-\*•◦○●]+', '', text)  # Remove decorative characters
    text = re.sub(r'\s+', ' ', text)  # Normalize whitespace
    text = text.strip()
    
    # Fix common encoding issues
    text = text.replace('â€™', "'")
    text = text.replace('â€"', "-")
    text = text.replace('â€œ', '"')
    text = text.replace('â€', '"')
    text = text.replace('â€¢', '•')
    
    return text

def is_navigation_text(text):
    """Check if text appears to be navigation or boilerplate content"""
    nav_patterns = [
        r'home|search|blog|changelog|quick\s+start|installation|deployment',
        r'previous|next|menu|navigation',
        r'copyright|terms|privacy|contact'
    ]
    return any(re.search(pattern, text.lower()) for pattern in nav_patterns)

def ensure_url_scheme(url):
    """Ensure URL has a proper scheme"""
    if not url.startswith(('http://', 'https://')):
        url = 'https://' + url.lstrip('/')
    return url

def format_condensed_summary(summary):
    """Format a condensed summary into a readable string"""
    if not summary:
        return "No content could be extracted"
        
    output = []
    
    # Add title
    if summary.get("title"):
        output.append(f"# {summary['title']}")
        output.append("")
    
    # Add core message if present
    if summary.get("core_message"):
        output.append("## Core Message")
        output.append(summary["core_message"])
        output.append("")
    
    # Add key points if present
    if summary.get("key_points"):
        output.append("## Key Points")
        for point in summary["key_points"]:
            output.append(f"- {point}")
        output.append("")
    
    # Add technical terms if present
    if summary.get("technical_terms"):
        output.append("## Technical Terms")
        for term in summary["technical_terms"]:
            output.append(f"- {term}")
        output.append("")
    
    return "\n".join(output)

async def crawl_docs(urls, output_dir, page_limit=None, format=SummaryFormat.STANDARD):
    """Crawl documentation pages and save structured content."""
    os.makedirs(output_dir, exist_ok=True)
    crawled_urls = set()
    queue = asyncio.Queue()
    progress = CrawlProgress(page_limit)
    
    # Add initial URLs to queue
    for url in urls:
        await queue.put(ensure_url_scheme(url))
    
    async with AsyncWebCrawler(BROWSER_CONFIG) as crawler:
        while not queue.empty() and not progress.limit_reached():
            url = await queue.get()
            
            if url in crawled_urls:
                continue
                
            logger.info(f"Crawling {url}")
            result = await safe_crawl(url)
            
            if result and result.success:
                # Save content
                save_to_knowledge_base(result, output_dir)
                crawled_urls.add(url)
                progress.increment()
                
                # Extract and queue new links
                links = extract_page_links(result.html, url)
                for link in links:
                    if link not in crawled_urls and not progress.limit_reached():
                        await queue.put(link)
            else:
                logger.error(f"Failed to crawl {url}")
    
    return len(crawled_urls)

async def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description='Crawl and summarize web content')
    parser.add_argument('urls', nargs='+', help='URLs to crawl')
    parser.add_argument('--output-dir', '-o', default='crawl_output', help='Output directory')
    parser.add_argument('--page-limit', '-l', type=int, help='Maximum pages to crawl')
    parser.add_argument('--format', '-f', choices=['standard', 'condensed'], default='standard', help='Summary format')
    parser.add_argument('--test', action='store_true', help='Test mode - crawl single page')
    parser.add_argument('--debug', action='store_true', help='Enable debug logging')
    args = parser.parse_args()
    
    # Configure logging
    log_level = logging.DEBUG if args.debug else logging.INFO
    logging.basicConfig(
        level=log_level,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )
    
    # Create output directory
    output_dir = os.path.abspath(args.output_dir)
    os.makedirs(output_dir, exist_ok=True)
    logger.debug(f"Using output directory: {output_dir}")
    
    # Process URLs
    if args.test:
        # Test mode - single page
        for url in args.urls:
            url = ensure_url_scheme(url)
            logger.info(f"Testing extraction on {url}")
            
            result = await safe_crawl(url)
            logger.debug(f"Crawl result: success={result.success if result else 'None'}")
            if result and result.success:
                if result.html:
                    logger.debug(f"HTML content length: {len(result.html)}")
                if result.markdown:
                    logger.debug(f"Markdown content length: {len(result.markdown)}")
                output_file = save_to_knowledge_base(result, output_dir)
                logger.info(f"Content saved to {output_file}")
            else:
                error_msg = result.error if result and hasattr(result, 'error') else "Unknown error"
                logger.error(f"Failed to extract content from {url}: {error_msg}")
    else:
        # Normal mode - crawl with link following
        format = SummaryFormat.CONDENSED if args.format == 'condensed' else SummaryFormat.STANDARD
        total_pages = await crawl_docs(args.urls, output_dir, args.page_limit, format)
        logger.info(f"Crawled {total_pages} pages")

if __name__ == "__main__":
    asyncio.run(main())
