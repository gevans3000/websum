#!/usr/bin/env python3
import os
import sys
import json
import logging
import datetime
import argparse
import asyncio
import re
from urllib.parse import urljoin, urlparse
from crawl4ai import AsyncWebCrawler, BrowserConfig, CrawlerRunConfig, CacheMode
from io import StringIO
from contextlib import redirect_stdout, redirect_stderr
from bs4 import BeautifulSoup
import time

# Initialize colorama
init = None  # Removed unused import

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(message)s'
)
logger = logging.getLogger(__name__)

# Constants
VERSION = "1.0.0"
TERM_WIDTH = None  # Removed unused constant

# JavaScript code to extract clean content
JS_CODE = None  # Removed unused JavaScript code

# Browser configuration with proper settings
BROWSER_CONFIG = BrowserConfig(
    headless=True,
    ignore_https_errors=True,
    viewport_width=1920,
    viewport_height=1080,
    verbose=True
)

# Crawler configuration
CRAWLER_CONFIG = CrawlerRunConfig(
    cache_mode=CacheMode.BYPASS,
    wait_for="css:body",
    word_count_threshold=50,
    excluded_tags=['nav', 'footer', 'header'],
    exclude_external_links=True,
    process_iframes=True,
    remove_overlay_elements=True
)

class CrawlProgress:
    """Simple progress tracking for crawling"""
    def __init__(self, page_limit=None):
        self.total_pages = 0
        self.processed_pages = 0
        self.current_depth = 0
        self.start_time = None
        self.page_limit = page_limit
        
    def start(self):
        """Start tracking progress"""
        self.start_time = datetime.datetime.now()
        
    def update(self, pages_at_depth=None):
        """Update progress"""
        self.processed_pages += 1
        if pages_at_depth is not None:
            remaining = min(pages_at_depth, self.page_limit - self.processed_pages) if self.page_limit else pages_at_depth
            self.total_pages = self.processed_pages + remaining
            
    def should_process_more(self):
        """Check if we should process more pages"""
        return not self.page_limit or self.processed_pages < self.page_limit
            
    def get_stats(self):
        """Get current statistics"""
        elapsed = datetime.datetime.now() - self.start_time if self.start_time else None
        return {
            'processed': self.processed_pages,
            'total': self.total_pages,
            'depth': self.current_depth,
            'elapsed': str(elapsed).split('.')[0] if elapsed else None,
            'page_limit': self.page_limit
        }

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
    def __init__(self):
        self.url = ""
        self.html = ""
        self.markdown = ""
        self.links = []
        self.success = False
        self.error = None
        self.title = ""  # Page title
        self.categories = []  # Topic categories
        self.summary = ""  # Brief summary
        self.keywords = []  # Key terms
        self.last_modified = None  # Last modified date

def ensure_url_scheme(url):
    """Ensure URL has a proper scheme"""
    if not url.startswith(('http://', 'https://')):
        url = 'https://' + url.lstrip('/')
    return url

async def crawl_page(url, crawler_config=None):
    """Crawl a page and return structured content"""
    if crawler_config is None:
        crawler_config = BROWSER_CONFIG
        
    try:
        # Capture all output
        with redirect_stdout(io.StringIO()), redirect_stderr(io.StringIO()):
            async with AsyncWebCrawler(config=crawler_config) as crawler:
                result = await crawler.arun(url, run_config=CRAWLER_CONFIG)
                if not result.success:
                    if logger.level == logging.DEBUG:
                        logger.error(f"Failed to crawl {url}: {result.error_message}")
                    return None
                
                if not result.html:
                    if logger.level == logging.DEBUG:
                        logger.error(f"No HTML content returned from {url}")
                    return None
                
                try:
                    # Parse the extracted content
                    content = json.loads(result.extracted_content or '{}')
                    if not content or not content.get('content', '').strip():
                        if logger.level == logging.DEBUG:
                            logger.warning(f"No content extracted from {url}")
                        return None
                    
                    # Skip if no meaningful content
                    if len(content['content'].split()) < 50:
                        if logger.level == logging.DEBUG:
                            logger.warning(f"Skipping {url}: insufficient content")
                        return None
                    
                    # Add additional metadata
                    content['url'] = url
                    content['timestamp'] = datetime.datetime.now().isoformat()
                    content['word_count'] = len(content['content'].split())
                    
                    # Clean up content
                    content['content'] = content['content'].strip()
                    for section in content.get('sections', []):
                        section['content'] = section['content'].strip()
                    
                    return content
                    
                except json.JSONDecodeError:
                    if logger.level == logging.DEBUG:
                        logger.error(f"Failed to parse JSON from {url}")
                    return None
    except Exception as e:
        if logger.level == logging.DEBUG:
            logger.exception(f"Error crawling {url}: {e}")
        return None

def extract_page_links(html_content, base_url):
    """
    Extract valid links from HTML content.
    Args:
        html_content (str): HTML content to extract links from
        base_url (str): Base URL for resolving relative links
    Returns:
        list: List of normalized URLs
    """
    if not html_content:
        return []
        
    # Parse base URL
    parsed_base = urlparse(base_url)
    base_domain = parsed_base.netloc
    
    # Use BeautifulSoup to parse HTML
    soup = BeautifulSoup(html_content, 'html.parser')
    
    # Find all links
    links = set()
    for a in soup.find_all('a', href=True):
        href = a['href']
        
        # Skip empty links, fragments, and special links
        if not href or href.startswith(('javascript:', 'mailto:', 'tel:')):
            continue
            
        # Handle fragment-only links
        if href.startswith('#'):
            continue
            
        # Resolve relative URLs
        if not href.startswith(('http://', 'https://')):
            href = urljoin(base_url, href)
            
        # Parse the URL
        parsed = urlparse(href)
        
        # Only keep links from the same domain
        if parsed.netloc == base_domain:
            # Normalize the URL
            normalized = href.split('#')[0]  # Remove fragments
            normalized = normalized.rstrip('/')  # Remove trailing slash
            
            # Skip obvious non-content URLs
            skip_patterns = [
                '/search', '/tags/', '/categories/',  # Common doc site patterns
                'index.xml', '.rss', '.atom',  # Feed URLs
                '/page/', '/assets/', '/static/',  # Pagination and assets
            ]
            if any(pattern in normalized.lower() for pattern in skip_patterns):
                continue
                
            if normalized:
                links.add(normalized)
    
    return sorted(list(links))

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
    
    # Get path parts
    path_parts = parsed.path.strip('/').split('/')
    
    # Handle empty path or trailing slash
    if not path_parts[-1]:
        path_parts[-1] = 'index'
    
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
    
    return clean_parts

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
    """Extract clean readable text from markdown, preserving code and instructions"""
    if not markdown_content:
        return ""
    
    text = markdown_content
    sections = []
    
    # Split into sections based on headers
    header_pattern = r'^#{1,6}\s+(.+)$'
    current_section = []
    current_header = "Introduction"
    
    for line in text.split('\n'):
        header_match = re.match(header_pattern, line)
        if header_match:
            if current_section:
                sections.append((current_header, '\n'.join(current_section)))
            current_header = header_match.group(1)
            current_section = []
        else:
            current_section.append(line)
    
    if current_section:
        sections.append((current_header, '\n'.join(current_section)))
    
    # Process each section
    processed_sections = []
    for header, content in sections:
        processed = f"\n{header}\n{'=' * len(header)}\n"
        
        # Extract code blocks
        code_blocks = re.finditer(r'```(\w+)?\n(.*?)```', content, re.DOTALL)
        code_positions = []
        for match in code_blocks:
            lang = match.group(1) or 'text'
            code = match.group(2)
            code_positions.append({
                'start': match.start(),
                'end': match.end(),
                'replacement': f"\nCode Example ({lang}):\n-------------------\n{code.strip()}\n"
            })
        
        # Replace code blocks from end to start to maintain positions
        for pos in reversed(code_positions):
            content = content[:pos['start']] + pos['replacement'] + content[pos['end']:]
        
        # Handle inline code
        content = re.sub(r'`([^`]+)`', r'<code>\1</code>', content)
        
        # Extract steps or instructions
        step_pattern = r'^\s*(?:\d+\.|[-\*\+])\s+(.+)$'
        lines = content.split('\n')
        in_steps = False
        step_buffer = []
        
        for line in lines:
            if re.match(step_pattern, line):
                if not in_steps:
                    in_steps = True
                    step_buffer.append("\nSteps:\n------")
                step_buffer.append(re.sub(r'^\s*(?:\d+\.|[-\*\+])\s+', '• ', line))
            else:
                if in_steps:
                    in_steps = False
                    step_buffer.append("")
                step_buffer.append(line)
        
        content = '\n'.join(step_buffer)
        
        # Clean up formatting but preserve structure
        content = re.sub(r'\*\*([^\*]+)\*\*', r'[Important: \1]', content)  # Convert bold to semantic markup
        content = re.sub(r'\*([^\*]+)\*', r'[Note: \1]', content)  # Convert italic to semantic markup
        content = re.sub(r'_([^_]+)_', r'[Emphasis: \1]', content)  # Convert underscore to semantic markup
        
        processed += content + "\n"
        processed_sections.append(processed)
    
    return '\n'.join(processed_sections)

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
            f.write(f"Technical Scope\n--------------\n{', '.join(content.keywords)}\n\n")
        
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
        current_section = []
        current_header = None
        
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

async def process_page(url, depth, max_depth, crawler, progress, output_dir, debug=False):
    """Process a single page and return its links if within depth limit."""
    if depth > max_depth:
        return True, []
        
    if debug:
        logger.debug(f"Processing {url} (depth {depth}/{max_depth})")
    
    # Get the page content
    result = await crawler.arun(url, config=CRAWLER_CONFIG)
    if not result.success:
        logger.error(f"Failed to fetch page: {result.error_message}")
        return False, []
    
    # Update progress
    progress.current_depth = depth
    progress.update()
    stats = progress.get_stats()
    logger.info(f"Progress: {stats['processed']}/{stats['total'] or '?'} pages, depth {depth}/{max_depth}, {stats['elapsed']} elapsed")
    
    if debug:
        logger.debug(f"Successfully fetched page")
        logger.debug(f"HTML length: {len(result.html or '')}")
        logger.debug(f"Markdown length: {len(result.markdown or '')}")
    
    # Extract links from the page
    links = extract_page_links(result.html, url)
    if debug:
        logger.debug(f"Found {len(links)} links on the page:")
        for link in links[:5]:  
            logger.debug(f"  - {link}")
        if len(links) > 5:
            logger.debug(f"  ... and {len(links) - 5} more")
    
    # Generate safe filename from URL
    path_parts = sanitize_filename(url)
    
    # Create subdirectories if needed
    output_path = os.path.join(output_dir, *path_parts)
    if not output_path.endswith('.json'):
        output_path += '.json'
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    # Save the content
    content = CrawlResult()
    content.url = url
    content.html = result.html
    content.markdown = result.markdown
    content.links = links
    content.success = result.success
    metadata = extract_metadata(result.html)
    content.title = metadata['title']
    content.keywords = metadata['keywords']
    content.last_modified = metadata['last_modified']
    
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump({
            'url': content.url,
            'timestamp': datetime.datetime.now().isoformat(),
            'html': content.html,
            'markdown': content.markdown,
            'links': content.links,
            'title': content.title,
            'keywords': content.keywords,
            'last_modified': content.last_modified,
            'depth': depth,
            'stats': progress.get_stats()
        }, f, indent=2, ensure_ascii=False)
    
    if debug:
        logger.debug(f"Content saved to {output_path}")
    
    # Save readable text
    text_path = os.path.splitext(output_path)[0] + '.txt'
    save_readable_text(result.markdown, text_path)
    
    if debug:
        logger.debug(f"Readable text saved to {text_path}")
    
    # Save knowledge base entry
    unified_file = save_unified_knowledge(content, os.path.dirname(output_path))
    
    if debug:
        logger.debug(f"Unified knowledge file saved to {unified_file}")
    
    return True, links if depth < max_depth else []

async def main():
    parser = argparse.ArgumentParser(
        description=f'WebSum v{VERSION} - Website Content Extractor for LLM Training',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    parser.add_argument('url', help='URL to crawl')
    parser.add_argument('--depth', type=int, default=1, help='Maximum crawl depth')
    parser.add_argument('--debug', action='store_true', help='Enable debug output')
    parser.add_argument('--output-dir', help='Output directory (default: scraped_data/YYYYMMDD_HHMMSS)')
    parser.add_argument('--page-limit', type=int, help='Maximum number of pages to crawl')
    parser.add_argument('--rate-limit', type=float, default=1.0, 
                      help='Minimum delay between requests in seconds')
    parser.add_argument('--no-cache', action='store_true',
                      help='Disable URL caching (process all URLs even if seen before)')
    parser.add_argument('--cache-file', default='url_cache.json',
                      help='File to store URL cache (default: url_cache.json)')
    parser.add_argument('--merge-cache', 
                      help='Merge another cache file into the current cache')
    
    # Knowledge base options
    kb_group = parser.add_argument_group('Knowledge Base Options')
    kb_group.add_argument('--kb-root', default='knowledge_base',
                       help='Root directory for knowledge base')
    kb_group.add_argument('--kb-category', 
                       help='Category for the content (e.g., python/web-scraping)')
    kb_group.add_argument('--kb-title',
                       help='Title for the content (default: extracted from page)')
    kb_group.add_argument('--kb-summary',
                       help='Brief summary of the content')
    kb_group.add_argument('--kb-keywords',
                       help='Comma-separated keywords')
    kb_group.add_argument('--kb-format', choices=['flat', 'hierarchical'], default='hierarchical',
                       help='Knowledge base organization format')
    
    args = parser.parse_args()
    
    # Configure logging
    if args.debug:
        logger.setLevel(logging.DEBUG)
        logger.debug("Debug mode enabled")
        logger.debug(f"Rate limit: {args.rate_limit} seconds")
    
    # Handle cache merge if requested
    if args.merge_cache:
        cache = URLCache(cache_file=args.cache_file)
        merged_count = cache.merge(args.merge_cache)
        logger.info(f"Merged {merged_count} URLs from {args.merge_cache}")
        if args.debug:
            stats = cache.get_stats()
            logger.debug(f"Cache now contains {stats['total_urls']} URLs with {stats['total_visits']} total visits")
        return 0
    
    # Initialize progress tracking
    progress = CrawlProgress(page_limit=args.page_limit)
    progress.start()
    
    # Ensure URL has scheme
    url = ensure_url_scheme(args.url)
    if args.debug:
        logger.debug(f"URL with scheme: {url}")
    
    # Create output directory
    if not args.output_dir:
        timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
        args.output_dir = os.path.join('scraped_data', timestamp)
    os.makedirs(args.output_dir, exist_ok=True)
    
    if args.debug:
        logger.debug(f"Output directory: {args.output_dir}")
    
    try:
        # First try to get the page directly
        async with AsyncWebCrawler(config=BROWSER_CONFIG) as crawler:
            if args.debug:
                logger.debug(f"Fetching {url}")
            
            result = await crawler.arun(url, config=CRAWLER_CONFIG)
            
            if not result.success:
                logger.error(f"Failed to fetch page: {result.error_message}")
                return 1
            
            # Update progress
            progress.update()
            stats = progress.get_stats()
            logger.info(f"Progress: {stats['processed']}/{stats['total'] or '?'} pages, {stats['elapsed']} elapsed")
            
            if args.debug:
                logger.debug(f"Successfully fetched page")
                logger.debug(f"HTML length: {len(result.html or '')}")
                logger.debug(f"Markdown length: {len(result.markdown or '')}")
            
            # Extract links from the page
            links = extract_page_links(result.html, url)
            if args.debug:
                logger.debug(f"Found {len(links)} links on the page:")
                for link in links[:5]:  
                    logger.debug(f"  - {link}")
                if len(links) > 5:
                    logger.debug(f"  ... and {len(links) - 5} more")
            
            # Save the content
            output_file = os.path.join(args.output_dir, 'content.json')
            content = CrawlResult()
            content.url = url
            content.html = result.html
            content.markdown = result.markdown
            content.links = links
            content.success = result.success
            metadata = extract_metadata(result.html)
            content.title = metadata['title']
            content.keywords = metadata['keywords']
            content.last_modified = metadata['last_modified']
            
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump({
                    'url': content.url,
                    'timestamp': datetime.datetime.now().isoformat(),
                    'html': content.html,
                    'markdown': content.markdown,
                    'links': content.links,
                    'title': content.title,
                    'keywords': content.keywords,
                    'last_modified': content.last_modified,
                    'stats': progress.get_stats()  
                }, f, indent=2, ensure_ascii=False)
            
            if args.debug:
                logger.debug(f"Content saved to {output_file}")
            
            # Save readable text
            readable_text_file = os.path.join(args.output_dir, 'readable_text.txt')
            save_readable_text(result.markdown, readable_text_file)
            
            if args.debug:
                logger.debug(f"Readable text saved to {readable_text_file}")
            
            # Save knowledge base entry
            if args.kb_root and args.kb_category:
                content.categories = [args.kb_category]
                if args.kb_title:
                    content.title = args.kb_title
                if args.kb_summary:
                    content.summary = args.kb_summary
                if args.kb_keywords:
                    content.keywords = [k.strip() for k in args.kb_keywords.split(',')]
                
                unified_file = save_unified_knowledge(content, args.output_dir, args.kb_root, args.kb_category)
                if args.debug:
                    logger.debug(f"Unified knowledge file saved to {unified_file}")
            else:
                unified_file = save_unified_knowledge(content, args.output_dir)
            
            if args.debug:
                logger.debug(f"Unified knowledge file saved to {unified_file}")
            
            # Process links
            to_process = [(link, 1) for link in links]
            rate_limiter = RateLimiter(delay_seconds=args.rate_limit)
            url_cache = URLCache(cache_file=args.cache_file, enabled=not args.no_cache)
            
            if args.debug and not args.no_cache:
                stats = url_cache.get_stats()
                logger.debug(f"URL cache loaded: {stats['total_urls']} URLs, {stats['total_visits']} total visits")
            
            while to_process and progress.should_process_more():
                link, depth = to_process.pop(0)
                if url_cache.has_url(link):
                    if args.debug:
                        logger.debug(f"Skipping cached URL: {link}")
                    continue
                url_cache.add_url(link)
                await rate_limiter.wait()
                success, new_links = await process_page(link, depth, args.depth, crawler, progress, args.output_dir, debug=args.debug)
                if success:
                    to_process.extend([(new_link, depth + 1) for new_link in new_links])
            
            return 0
            
    except Exception as e:
        logger.error(f"Error processing page: {e}")
        if args.debug:
            logger.exception("Full traceback:")
        return 1

if __name__ == "__main__":
    asyncio.run(main())
