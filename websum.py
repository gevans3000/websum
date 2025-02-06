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
    content = {
        'url': url,
        'timestamp': datetime.datetime.now().isoformat(),
        'html': result.html,
        'markdown': result.markdown,
        'links': links,
        'depth': depth,
        'stats': progress.get_stats()
    }
    
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(content, f, indent=2, ensure_ascii=False)
    
    if debug:
        logger.debug(f"Content saved to {output_path}")
    
    # Save readable text
    text_path = os.path.splitext(output_path)[0] + '.txt'
    save_readable_text(result.markdown, text_path)
    
    if debug:
        logger.debug(f"Readable text saved to {text_path}")
    
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
    parser.add_argument('--include-links', action='store_true', help='Include links in readable text output')
    parser.add_argument('--include-sections', action='store_true', help='Add section breaks in readable text output')
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
                for link in links[:5]:  # Show first 5 links
                    logger.debug(f"  - {link}")
                if len(links) > 5:
                    logger.debug(f"  ... and {len(links) - 5} more")
            
            # Save the content
            output_file = os.path.join(args.output_dir, 'content.json')
            content = {
                'url': url,
                'timestamp': datetime.datetime.now().isoformat(),
                'html': result.html,
                'markdown': result.markdown,
                'links': links,
                'stats': progress.get_stats()  # Include progress stats in output
            }
            
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(content, f, indent=2, ensure_ascii=False)
            
            if args.debug:
                logger.debug(f"Content saved to {output_file}")
            
            # Save readable text
            readable_text_file = os.path.join(args.output_dir, 'readable_text.txt')
            save_readable_text(result.markdown, readable_text_file, include_links=args.include_links, include_sections=args.include_sections)
            
            if args.debug:
                logger.debug(f"Readable text saved to {readable_text_file}")
            
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
