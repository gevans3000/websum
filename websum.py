#!/usr/bin/env python3
import sys
import asyncio
import json
import logging
import datetime
import os
from urllib.parse import urljoin
import argparse
from colorama import init, Fore, Style, Back
from halo import Halo
import textwrap
from crawl4ai import AsyncWebCrawler, BrowserConfig, CrawlerRunConfig, CacheMode
from crawl4ai.extraction_strategy import JsonCssExtractionStrategy
from bs4 import BeautifulSoup

# Initialize colorama for Windows support
init()

# Version information
VERSION = "1.0.0"

# Configure logging with colors
class ColoredFormatter(logging.Formatter):
    """Custom formatter with colors"""
    def format(self, record):
        if record.levelno >= logging.ERROR:
            color = Fore.RED
        elif record.levelno >= logging.WARNING:
            color = Fore.YELLOW
        else:
            color = Fore.GREEN
        record.msg = f"{color}{record.msg}{Style.RESET_ALL}"
        return super().format(record)

# Configure logging
logger = logging.getLogger(__name__)
handler = logging.StreamHandler()
handler.setFormatter(ColoredFormatter('%(message)s'))
logger.addHandler(handler)
logger.setLevel(logging.INFO)

# Suppress all other loggers
for log_name in ['crawl4ai', 'urllib3', 'asyncio']:
    logging.getLogger(log_name).setLevel(logging.WARNING)

# Terminal width for formatting
TERM_WIDTH = os.get_terminal_size().columns

def format_status(text, status="", color=Fore.CYAN):
    """Format a status message with proper padding"""
    if status:
        status = f" [{status}]"
    return f"{color}{text}{status}{Style.RESET_ALL}".ljust(TERM_WIDTH)

def format_success(text):
    """Format a success message"""
    check = f"{Fore.GREEN}✓{Style.RESET_ALL}"
    return f"{check} {Fore.GREEN}{text}{Style.RESET_ALL}"

def format_error(text):
    """Format an error message"""
    cross = f"{Fore.RED}✗{Style.RESET_ALL}"
    return f"{cross} {Fore.RED}{text}{Style.RESET_ALL}"

def format_warning(text):
    """Format a warning message"""
    warn = f"{Fore.YELLOW}!{Style.RESET_ALL}"
    return f"{warn} {Fore.YELLOW}{text}{Style.RESET_ALL}"

def print_header(text):
    """Print a section header"""
    print(f"\n{Fore.CYAN}{Style.BRIGHT}{text}{Style.RESET_ALL}")
    print(f"{Fore.CYAN}{'─' * min(len(text), TERM_WIDTH)}{Style.RESET_ALL}")

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
    
    # Temporarily redirect stdout/stderr
    import io
    from contextlib import redirect_stdout, redirect_stderr

    try:
        # Capture all output
        with redirect_stdout(io.StringIO()), redirect_stderr(io.StringIO()):
            async with AsyncWebCrawler(config=BROWSER_CONFIG) as crawler:
                result = await crawler.arun(url, run_config=run_conf)
                if not result.success:
                    if logger.level == logging.DEBUG:
                        logger.error(f"Failed to crawl {url}: {result.error_message}")
                    return None
                
                # Save screenshot for debugging if available
                if result.screenshot and logger.level == logging.DEBUG:
                    os.makedirs("debug", exist_ok=True)
                    with open(f"debug/{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.png", "wb") as f:
                        f.write(result.screenshot)
                
                return result.markdown
    except Exception as e:
        if logger.level == logging.DEBUG:
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

    # Temporarily redirect stdout/stderr
    import io
    from contextlib import redirect_stdout, redirect_stderr

    try:
        # Capture all output
        with redirect_stdout(io.StringIO()), redirect_stderr(io.StringIO()):
            async with AsyncWebCrawler(config=BROWSER_CONFIG) as crawler:
                result = await crawler.arun(url, run_config=run_conf)
                if logger.level == logging.DEBUG:
                    print("Debug - raw HTML:", result.html[:200])
                    print("Debug - extracted_content:", repr(result.extracted_content))
                
                if not result.success:
                    if logger.level == logging.DEBUG:
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
                    if logger.level == logging.DEBUG:
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
        if logger.level == logging.DEBUG:
            logger.exception(f"Error extracting links from {url}: {e}")
        return []

def ensure_url_scheme(url):
    """Ensure URL has a proper scheme"""
    if not url.startswith(('http://', 'https://')):
        url = 'https://' + url.lstrip('/')
    return url

def parse_arguments():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(
        description=f"{Fore.CYAN}WebSum v{VERSION}{Style.RESET_ALL} - A web content summarization tool",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=textwrap.dedent(f"""
            {Fore.GREEN}Examples:{Style.RESET_ALL}
            %(prog)s python.org 3                    # Crawl python.org and 3 subpages
            %(prog)s --debug example.com 5           # Crawl with debug output
            %(prog)s --output-dir ./custom python.org  # Use custom output directory
        """)
    )
    parser.add_argument("url", help="URL to crawl")
    parser.add_argument("max_links", nargs="?", type=int, default=3,
                      help="Maximum number of links to follow (default: 3)")
    parser.add_argument("--debug", action="store_true",
                      help="Enable debug output")
    parser.add_argument("--version", action="version",
                      version=f"%(prog)s {VERSION}")
    parser.add_argument("--output-dir", help="Custom output directory")
    return parser.parse_args()

async def main():
    args = parse_arguments()
    
    # Configure logging based on debug flag
    if args.debug:
        logger.setLevel(logging.DEBUG)
    
    base_url = ensure_url_scheme(args.url)
    max_links = args.max_links

    # Use custom output directory if specified
    if args.output_dir:
        output_base = args.output_dir
    else:
        output_base = "scraped_data"

    try:
        # Clear screen
        os.system('cls' if os.name == 'nt' else 'clear')
        
        # Print welcome message
        print("═" * TERM_WIDTH)
        print(format_status(f"WebSum v{VERSION}", color=Fore.CYAN + Style.BRIGHT))
        print(format_status(f"Starting crawl of: {base_url}", color=Fore.CYAN))
        print("═" * TERM_WIDTH)
        
        # Create spinner for base page crawl
        print_header("Phase 1: Crawling Base Page")
        spinner = Halo(
            text=format_status("Fetching content...", "BASE"),
            spinner='dots',
            color='cyan',
            placement='right'
        )
        
        spinner.start()
        base_markdown = await crawl_markdown(base_url)
        if base_markdown:
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            output_dir = os.path.join(output_base, timestamp)
            os.makedirs(output_dir, exist_ok=True)
            output_path = os.path.join(output_dir, "base_page.md")
            
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(base_markdown)
            spinner.succeed(format_success(f"Base page saved ({len(base_markdown)} bytes)"))
            if args.debug:
                print(f"  └─ {output_path}")
        else:
            spinner.fail(format_error("Failed to crawl base page"))
            sys.exit(1)

        print_header("Phase 2: Link Extraction")
        spinner = Halo(
            text=format_status("Analyzing page...", "LINKS"),
            spinner='dots',
            color='cyan',
            placement='right'
        )
        
        spinner.start()
        links = await extract_links(base_url, max_links=max_links)
        if not links:
            spinner.warn(format_warning("No links found on the base page"))
            return
        spinner.succeed(format_success(f"Found {len(links)} links"))
        if args.debug:
            for i, link in enumerate(links, 1):
                print(f"  └─ {i}. {link}")

        if links:
            print_header(f"Phase 3: Crawling Links ({len(links)} pages)")
            
        for idx, link in enumerate(links, 1):
            status = f"{idx}/{len(links)}"
            spinner = Halo(
                text=format_status(f"Crawling: {link}", status),
                spinner='dots',
                color='cyan',
                placement='right'
            )
            
            spinner.start()
            page_markdown = await crawl_markdown(link)
            if page_markdown:
                filename = f"link_{idx}.md"
                output_path = os.path.join(output_dir, filename)
                with open(output_path, 'w', encoding='utf-8') as f:
                    f.write(page_markdown)
                spinner.succeed(format_success(f"Page {status} saved ({len(page_markdown)} bytes)"))
                if args.debug:
                    print(f"  └─ {output_path}")
            else:
                spinner.fail(format_error(f"Failed to crawl page {status}"))

        # Print summary
        print("\n" + "═" * TERM_WIDTH)
        print(format_success("Crawl completed successfully!"))
        print(f"  └─ Output directory: {output_dir}")
        print("═" * TERM_WIDTH)
        
    except Exception as e:
        print("\n" + "═" * TERM_WIDTH)
        print(format_error(f"Error: {str(e)}"))
        print("═" * TERM_WIDTH)
        if args.debug:
            import traceback
            print("\nDebug traceback:")
            print(traceback.format_exc())
        sys.exit(1)
    finally:
        # Always stop the spinner in case of errors
        if 'spinner' in locals():
            spinner.stop()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.error(f"{Fore.RED}Crawl interrupted by user{Style.RESET_ALL}")
        sys.exit(1)
    except Exception as e:
        logger.error(f"{Fore.RED}Error: {str(e)}{Style.RESET_ALL}")
        if logger.level == logging.DEBUG:
            logger.exception("Detailed error:")
        sys.exit(1)
