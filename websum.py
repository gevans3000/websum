#!/usr/bin/env python3
import sys
import asyncio
import json
import logging
import datetime
import os
from urllib.parse import urljoin
from crawl4ai import AsyncWebCrawler, BrowserConfig, CrawlerRunConfig, CacheMode
from crawl4ai.extraction_strategy import JsonCssExtractionStrategy

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Browser configuration with proper settings
BROWSER_CONFIG = BrowserConfig(
    headless=False,  # Show browser for debugging
    viewport_width=1920,
    viewport_height=1080
)

# JavaScript for handling dynamic content
JS_CODE = """
// Wait for page to be fully loaded
await new Promise(r => setTimeout(r, 2000));

// Handle lazy loading by scrolling
for (let i = 0; i < 3; i++) {
    window.scrollTo(0, document.body.scrollHeight);
    await new Promise(r => setTimeout(r, 1000));
}

// Fix relative URLs
const links = document.getElementsByTagName('a');
for (let link of links) {
    if (link.href.startsWith('//')) {
        link.href = 'https:' + link.href;
    }
}

// Remove unwanted elements that might interfere
const selectors = ['header', 'footer', 'nav', '.cookie-banner', '#popup'];
selectors.forEach(selector => {
    const elements = document.querySelectorAll(selector);
    elements.forEach(el => el.remove());
});
"""

async def crawl_markdown(url):
    """Crawl the given URL and return markdown content"""
    run_conf = CrawlerRunConfig(
        cache_mode=CacheMode.BYPASS,
        js_code=[JS_CODE],
        screenshot=True,  # Capture screenshot for debugging
        wait_for="networkidle",
        word_count_threshold=10
    )
    
    try:
        async with AsyncWebCrawler(config=BROWSER_CONFIG) as crawler:
            result = await crawler.arun(url, run_config=run_conf)
            if not result.success:
                logger.error(f"Failed to crawl {url}: {result.error_message}")
                return None
            
            # Save screenshot for debugging if available
            if result.screenshot:
                os.makedirs("debug", exist_ok=True)
                with open(f"debug/{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.png", "wb") as f:
                    f.write(result.screenshot)
            
            return result.markdown
    except Exception as e:
        logger.exception(f"Error crawling {url}: {e}")
        return None

async def extract_links(url, max_links=3):
    """Extract links using a more robust strategy"""
    schema = {
        "type": "array",
        "items": {
            "type": "object",
            "properties": {
                "href": {"type": "string"}
            }
        },
        "selector": "a",
        "fields": [
            {
                "name": "href",
                "type": "attribute",
                "attribute": "href"
            }
        ]
    }
    
    extraction = JsonCssExtractionStrategy(schema)
    run_conf = CrawlerRunConfig(
        cache_mode=CacheMode.BYPASS,
        js_code=[JS_CODE],
        extraction_strategy=extraction,
        wait_for="networkidle",
        word_count_threshold=10
    )

    try:
        async with AsyncWebCrawler(config=BROWSER_CONFIG) as crawler:
            result = await crawler.arun(url, run_config=run_conf)
            print("Debug - raw HTML:", result.html[:200])  # Debug print
            print("Debug - extracted_content:", repr(result.extracted_content))
            
            if not result.success:
                logger.error(f"Failed to extract links from {url}: {result.error_message}")
                return []
            
            # Try to parse the extracted content
            try:
                if result.extracted_content:
                    extracted = json.loads(result.extracted_content)
                    links = []
                    if isinstance(extracted, list):
                        for item in extracted:
                            if isinstance(item, dict) and 'href' in item:
                                href = item['href']
                                if href and href.startswith(('http://', 'https://')):
                                    links.append(href)
                                    if len(links) >= max_links:
                                        break
                    return links
            except json.JSONDecodeError:
                logger.warning("Failed to parse JSON, falling back to HTML extraction")
            
            # Fallback: extract links directly from HTML
            from bs4 import BeautifulSoup
            soup = BeautifulSoup(result.html, 'html.parser')
            links = []
            for a in soup.find_all('a', href=True):
                href = a['href']
                if href.startswith('//'):
                    href = 'https:' + href
                elif href.startswith('/'):
                    href = urljoin(url, href)
                if href.startswith(('http://', 'https://')):
                    links.append(href)
                    if len(links) >= max_links:
                        break
            return links
            
    except Exception as e:
        logger.exception(f"Error extracting links from {url}: {e}")
        return []

def ensure_url_scheme(url):
    """Ensure URL has a proper scheme"""
    if not url.startswith(('http://', 'https://')):
        url = 'https://' + url.lstrip('/')
    return url

async def main():
    if len(sys.argv) < 2:
        print("Usage: python script.py <URL> [max_links]")
        sys.exit(1)

    base_url = ensure_url_scheme(sys.argv[1])
    max_links = int(sys.argv[2]) if len(sys.argv) > 2 else 3

    logger.info(f"Crawling base page: {base_url}")
    base_markdown = await crawl_markdown(base_url)
    if base_markdown:
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        output_dir = f"scraped_data/{timestamp}"
        os.makedirs(output_dir, exist_ok=True)
        output_path = os.path.join(output_dir, "base_page.md")
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(base_markdown)
        logger.info(f"Saved base page markdown to {output_path}")
    else:
        logger.error("Failed to crawl base page")
        sys.exit(1)

    logger.info("Extracting links from the base page...")
    links = await extract_links(base_url, max_links=max_links)
    if not links:
        logger.info("No links found on the base page.")
        return

    for idx, link in enumerate(links, 1):
        logger.info(f"Crawling link {idx}: {link}")
        page_markdown = await crawl_markdown(link)
        if page_markdown:
            filename = f"link_{idx}.md"
            output_path = os.path.join(output_dir, filename)
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(page_markdown)
            logger.info(f"Saved link {idx} to {output_path}")
        else:
            logger.error(f"Failed to crawl link {idx}: {link}")

if __name__ == "__main__":
    asyncio.run(main())
