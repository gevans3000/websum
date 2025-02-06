#!/usr/bin/env python3
import os
import sys
import json
import logging
import datetime
import argparse
import asyncio
from urllib.parse import urljoin, urlparse
from crawl4ai import AsyncWebCrawler, BrowserConfig, CrawlerRunConfig, CacheMode

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

async def main():
    parser = argparse.ArgumentParser(
        description=f'WebSum v{VERSION} - Website Content Extractor for LLM Training',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    parser.add_argument('url', help='URL to crawl')
    parser.add_argument('--depth', type=int, default=1, help='Maximum crawl depth')
    parser.add_argument('--debug', action='store_true', help='Enable debug output')
    parser.add_argument('--output-dir', help='Output directory (default: scraped_data/YYYYMMDD_HHMMSS)')
    args = parser.parse_args()
    
    # Configure logging
    if args.debug:
        logger.setLevel(logging.DEBUG)
        logger.debug("Debug mode enabled")
    
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
            
            if args.debug:
                logger.debug(f"Successfully fetched page")
                logger.debug(f"HTML length: {len(result.html or '')}")
                logger.debug(f"Markdown length: {len(result.markdown or '')}")
            
            # Save the content
            output_file = os.path.join(args.output_dir, 'content.json')
            content = {
                'url': url,
                'timestamp': datetime.datetime.now().isoformat(),
                'html': result.html,
                'markdown': result.markdown,
                'links': result.links if hasattr(result, 'links') else None
            }
            
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(content, f, indent=2, ensure_ascii=False)
            
            if args.debug:
                logger.debug(f"Content saved to {output_file}")
            
            return 0
            
    except Exception as e:
        logger.error(f"Error processing page: {e}")
        if args.debug:
            logger.exception("Full traceback:")
        return 1

if __name__ == "__main__":
    asyncio.run(main())
