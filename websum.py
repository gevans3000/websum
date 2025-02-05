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

# JavaScript snippet to remove header and footer from the page
JS_REMOVE_HEADER_FOOTER = (
    "if(document.querySelector('header')) { document.querySelector('header').remove(); } "
    "if(document.querySelector('footer')) { document.querySelector('footer').remove(); }"
)

def ensure_url_scheme(url):
    """
    Ensures the URL starts with a valid scheme.
    If not, 'http://' is prepended.
    """
    if not url.startswith(('http://', 'https://', 'file://', 'raw:')):
        url = 'http://' + url
    return url

async def crawl_markdown(url, js_code):
    """
    Crawl the given URL with injected JS code to remove header/footer,
    and return the page's Markdown content.
    """
    run_conf = CrawlerRunConfig(
        cache_mode=CacheMode.BYPASS,
        js_code=[js_code]
    )
    try:
        async with AsyncWebCrawler() as crawler:
            result = await crawler.arun(url, config=run_conf)
            if not result.success:
                logger.error(f"Crawl failed for {url}: {result.error_message}")
                return None
            return result.markdown
    except Exception as e:
        logger.exception(f"Exception while crawling {url}: {e}")
        return None

async def extract_links(url, js_code, max_links=3):
    """
    Extract up to max_links from the given URL using a CSS extraction strategy.
    Returns a list of link URLs.
    """
    schema = {
        "name": "Links",
        "baseSelector": "a",
        "fields": [
            {"name": "href", "selector": "", "type": "attribute", "attribute": "href"}
        ]
    }
    extraction = JsonCssExtractionStrategy(schema)
    run_conf = CrawlerRunConfig(
        cache_mode=CacheMode.BYPASS,
        js_code=[js_code],
        extraction_strategy=extraction
    )
    try:
        async with AsyncWebCrawler() as crawler:
            result = await crawler.arun(url, config=run_conf)
            if not result.success:
                logger.error(f"Extraction failed for {url}: {result.error_message}")
                return []
            links_data = json.loads(result.extracted_content)
    except Exception as e:
        logger.exception(f"Exception during link extraction from {url}: {e}")
        return []

    links = []
    if isinstance(links_data, list):
        for item in links_data:
            if isinstance(item, dict) and "href" in item:
                href = item["href"]
                if href and href not in links:
                    links.append(href)
                    if len(links) >= max_links:
                        break
    return links

async def main():
    if len(sys.argv) < 2:
        print("Usage: python script.py <URL> [max_links]")
        sys.exit(1)
    base_url = sys.argv[1]
    # Ensure the URL has a valid scheme
    base_url = ensure_url_scheme(base_url)
    max_links = int(sys.argv[2]) if len(sys.argv) > 2 else 3

    logger.info(f"Crawling base page: {base_url}")
    base_markdown = await crawl_markdown(base_url, JS_REMOVE_HEADER_FOOTER)
    if base_markdown:
        # Create output directory
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        output_dir = f"scraped_data/{timestamp}"
        os.makedirs(output_dir, exist_ok=True)
        output_path = os.path.join(output_dir, "base_page.md")
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(base_markdown)
        logger.info(f"Saved base page markdown to {output_path}")
    else:
        logger.error("Failed to retrieve base page markdown.")
        sys.exit(1)

    logger.info("Extracting links from the base page...")
    links = await extract_links(base_url, JS_REMOVE_HEADER_FOOTER, max_links=max_links)
    if not links:
        logger.info("No links found on the base page.")
        return

    for idx, link in enumerate(links, start=1):
        # Convert relative links to absolute URLs if necessary
        full_url = urljoin(base_url, link) if link.startswith("/") or not link.startswith("http") else link
        logger.info(f"Crawling link {idx}: {full_url}")
        page_markdown = await crawl_markdown(full_url, JS_REMOVE_HEADER_FOOTER)
        if page_markdown:
            filename = f"link_{idx}.md".replace('/', '_')
            output_path = os.path.join(output_dir, filename)
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(page_markdown)
            logger.info(f"Saved link {idx} markdown to {output_path}")
        else:
            logger.error(f"Failed to crawl link: {full_url}")

if __name__ == "__main__":
    asyncio.run(main())
