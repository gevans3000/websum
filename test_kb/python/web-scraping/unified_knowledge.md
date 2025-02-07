# Simple Crawling - Crawl4AI Documentation (v0.4.3bx)

## 📚 Document Metadata

```yaml
title: Simple Crawling - Crawl4AI Documentation (v0.4.3bx)
source_url: https://docs.crawl4ai.com/core/simple-crawling
category: python/web-scraping
keywords: python, web scraping, crawling, tutorial
last_modified: Unknown
type: Technical Documentation
```

## 📋 Quick Summary

Guide to basic web crawling with Crawl4AI

## 🔧 Technical Context

### Key Technical Terms
- fit_markdown
- `:
`
- `

## Logging and Debugging
Enable verbose logging in `
- `

## Understanding the Response
The `
- ` method returns a `
- `
import asyncio
from crawl4ai import AsyncWebCrawler
from crawl4ai.async_configs import BrowserConfig, CrawlerRunConfig
async def main():
  browser_config = BrowserConfig() # Default browser configuration
  run_config = CrawlerRunConfig()  # Default crawl run configuration
  async with AsyncWebCrawler(config=browser_config) as crawler:
    result = await crawler.arun(
      url="https://example.com",
      config=run_config
    )
    print(result.markdown) # Print clean markdown content
if __name__ == "__main__":
  asyncio.run(main())

`
- word_count_threshold
- BrowserConfig
- cleaned_html
- CacheMode
- `
run_config = CrawlerRunConfig(
  word_count_threshold=10,    # Minimum words per content block
  exclude_external_links=True,  # Remove external links
  remove_overlay_elements=True,  # Remove popups/modals
  process_iframes=True      # Process iframe content
)
result = await crawler.arun(
  url="https://example.com",
  config=run_config
)

`
- status_code
- error_message
- CrawlerRunConfig
- run_config
- `
browser_config = BrowserConfig(verbose=True)
async with AsyncWebCrawler(config=browser_config) as crawler:
  run_config = CrawlerRunConfig()
  result = await crawler.arun(url="https://example.com", config=run_config)

`
- `

## Handling Errors
Always check if the crawl was successful:
`
- `
run_config = CrawlerRunConfig()
result = await crawler.arun(url="https://example.com", config=run_config)
if not result.success:
  print(f"Crawl failed: {result.error_message}")
  print(f"Status code: {result.status_code}")

`
- exclude_external_links
- object
- CrawlResult
- browser_config
- async_configs
- cache_mode
- `

## Complete Example
Here's a more comprehensive example demonstrating common usage patterns:
`
- `BrowserConfig`
- `
result = await crawler.arun(
  url="https://example.com",
  config=CrawlerRunConfig(fit_markdown=True)
)
# Different content formats
print(result.html)     # Raw HTML
print(result.cleaned_html) # Cleaned HTML
print(result.markdown)   # Markdown version
print(result.fit_markdown) # Most relevant content in markdown
# Check success status
print(result.success)   # True if crawl succeeded
print(result.status_code) # HTTP status code (e.g., 200, 404)
# Access extracted media and links
print(result.media)    # Dictionary of found media (images, videos, audio)
print(result.links)    # Dictionary of internal and external links

`
- `

## Adding Basic Options
Customize your crawl using `
- method
- AsyncWebCrawler
- remove_overlay_elements
- `
import asyncio
from crawl4ai import AsyncWebCrawler
from crawl4ai.async_configs import BrowserConfig, CrawlerRunConfig, CacheMode
async def main():
  browser_config = BrowserConfig(verbose=True)
  run_config = CrawlerRunConfig(
    # Content filtering
    word_count_threshold=10,
    excluded_tags=['form', 'header'],
    exclude_external_links=True,
    # Content processing
    process_iframes=True,
    remove_overlay_elements=True,
    # Cache control
    cache_mode=CacheMode.ENABLED # Use cache if available
  )
  async with AsyncWebCrawler(config=browser_config) as crawler:
    result = await crawler.arun(
      url="https://example.com",
      config=run_config
    )
    if result.success:
      # Print clean content
      print("Content:", result.markdown[:500]) # First 500 chars
      # Process images
      for image in result.media["images"]:
        print(f"Found image: {image['src']}")
      # Process links
      for link in result.links["internal"]:
        print(f"Internal link: {link['href']}")
    else:
      print(f"Crawl failed: {result.error_message}")
if __name__ == "__main__":
  asyncio.run(main())

`
- `CrawlerRunConfig`
- HTML
- ` object with several useful properties. Here's a quick overview (see [CrawlResult](https://docs.crawl4ai.com/core/api/crawl-result/>) for complete details):
`
- HTTP
- process_iframes
- excluded_tags

## 📖 Main Content

### Simple Crawling

This guide covers the basics of web crawling with Crawl4AI. You'll learn how to set up a crawler, make your first request, and understand the response.

#### Basic Usage

Set up a simple crawl using `BrowserConfig` and `CrawlerRunConfig`:

Code Example (text):
```text
import asyncio
from crawl4ai import AsyncWebCrawler
from crawl4ai.async_configs import BrowserConfig, CrawlerRunConfig
async def main():
  browser_config = BrowserConfig() # Default browser configuration
  run_config = CrawlerRunConfig()  # Default crawl run configuration
  async with AsyncWebCrawler(config=browser_config) as crawler:
    result = await crawler.arun(
      url="https://example.com",
      config=run_config
    )
    print(result.markdown) # Print clean markdown content
if __name__ == "__main__":
  asyncio.run(main())
```




#### Understanding the Response

The `arun()` method returns a `CrawlResult` object with several useful properties. Here's a quick overview (see [CrawlResult](https://docs.crawl4ai.com/core/api/crawl-result/>) for complete details):
```
result = await crawler.arun(
  url="https://example.com",
  config=CrawlerRunConfig(fit_markdown=True)
)

### Different content formats

print(result.html)     # Raw HTML
print(result.cleaned_html) # Cleaned HTML
print(result.markdown)   # Markdown version
print(result.fit_markdown) # Most relevant content in markdown

### Check success status

print(result.success)   # True if crawl succeeded
print(result.status_code) # HTTP status code (e.g., 200, 404)

### Access extracted media and links

print(result.media)    # Dictionary of found media (images, videos, audio)
print(result.links)    # Dictionary of internal and external links

```


#### Adding Basic Options

Customize your crawl using `CrawlerRunConfig`:

Code Example (text):
```text
run_config = CrawlerRunConfig(
  word_count_threshold=10,    # Minimum words per content block
  exclude_external_links=True,  # Remove external links
  remove_overlay_elements=True,  # Remove popups/modals
  process_iframes=True      # Process iframe content
)
result = await crawler.arun(
  url="https://example.com",
  config=run_config
)
```




#### Handling Errors

Always check if the crawl was successful:

Code Example (text):
```text
run_config = CrawlerRunConfig()
result = await crawler.arun(url="https://example.com", config=run_config)
if not result.success:
  print(f"Crawl failed: {result.error_message}")
  print(f"Status code: {result.status_code}")
```




#### Logging and Debugging

Enable verbose logging in `BrowserConfig`:

Code Example (text):
```text
browser_config = BrowserConfig(verbose=True)
async with AsyncWebCrawler(config=browser_config) as crawler:
  run_config = CrawlerRunConfig()
  result = await crawler.arun(url="https://example.com", config=run_config)
```




#### Complete Example

Here's a more comprehensive example demonstrating common usage patterns:

Code Example (text):
```text
import asyncio
from crawl4ai import AsyncWebCrawler
from crawl4ai.async_configs import BrowserConfig, CrawlerRunConfig, CacheMode
async def main():
  browser_config = BrowserConfig(verbose=True)
  run_config = CrawlerRunConfig(
    # Content filtering
    word_count_threshold=10,
    excluded_tags=['form', 'header'],
    exclude_external_links=True,
    # Content processing
    process_iframes=True,
    remove_overlay_elements=True,
    # Cache control
    cache_mode=CacheMode.ENABLED # Use cache if available
  )
  async with AsyncWebCrawler(config=browser_config) as crawler:
    result = await crawler.arun(
      url="https://example.com",
      config=run_config
    )
    if result.success:
      # Print clean content
      print("Content:", result.markdown[:500]) # First 500 chars
      # Process images
      for image in result.media["images"]:
        print(f"Found image: {image['src']}")
      # Process links
      for link in result.links["internal"]:
        print(f"Internal link: {link['href']}")
    else:
      print(f"Crawl failed: {result.error_message}")
if __name__ == "__main__":
  asyncio.run(main())
```




####### Search

xClose
Type to start searching


## 🔗 Related Resources

- [https://docs.crawl4ai.com](https://docs.crawl4ai.com)
- [https://docs.crawl4ai.com/advanced/advanced-features](https://docs.crawl4ai.com/advanced/advanced-features)
- [https://docs.crawl4ai.com/advanced/crawl-dispatcher](https://docs.crawl4ai.com/advanced/crawl-dispatcher)
- [https://docs.crawl4ai.com/advanced/file-downloading](https://docs.crawl4ai.com/advanced/file-downloading)
- [https://docs.crawl4ai.com/advanced/hooks-auth](https://docs.crawl4ai.com/advanced/hooks-auth)
- [https://docs.crawl4ai.com/advanced/identity-based-crawling](https://docs.crawl4ai.com/advanced/identity-based-crawling)
- [https://docs.crawl4ai.com/advanced/lazy-loading](https://docs.crawl4ai.com/advanced/lazy-loading)
- [https://docs.crawl4ai.com/advanced/multi-url-crawling](https://docs.crawl4ai.com/advanced/multi-url-crawling)
- [https://docs.crawl4ai.com/advanced/proxy-security](https://docs.crawl4ai.com/advanced/proxy-security)
- [https://docs.crawl4ai.com/advanced/session-management](https://docs.crawl4ai.com/advanced/session-management)
- [https://docs.crawl4ai.com/advanced/ssl-certificate](https://docs.crawl4ai.com/advanced/ssl-certificate)
- [https://docs.crawl4ai.com/api/arun](https://docs.crawl4ai.com/api/arun)
- [https://docs.crawl4ai.com/api/arun_many](https://docs.crawl4ai.com/api/arun_many)
- [https://docs.crawl4ai.com/api/async-webcrawler](https://docs.crawl4ai.com/api/async-webcrawler)
- [https://docs.crawl4ai.com/api/crawl-result](https://docs.crawl4ai.com/api/crawl-result)
- [https://docs.crawl4ai.com/api/parameters](https://docs.crawl4ai.com/api/parameters)
- [https://docs.crawl4ai.com/api/strategies](https://docs.crawl4ai.com/api/strategies)
- [https://docs.crawl4ai.com/blog](https://docs.crawl4ai.com/blog)
- [https://docs.crawl4ai.com/browser-crawler-config](https://docs.crawl4ai.com/browser-crawler-config)
- [https://docs.crawl4ai.com/cache-modes](https://docs.crawl4ai.com/cache-modes)
- [https://docs.crawl4ai.com/content-selection](https://docs.crawl4ai.com/content-selection)
- [https://docs.crawl4ai.com/crawler-result](https://docs.crawl4ai.com/crawler-result)
- [https://docs.crawl4ai.com/docker-deploymeny](https://docs.crawl4ai.com/docker-deploymeny)
- [https://docs.crawl4ai.com/extraction/chunking](https://docs.crawl4ai.com/extraction/chunking)
- [https://docs.crawl4ai.com/extraction/clustring-strategies](https://docs.crawl4ai.com/extraction/clustring-strategies)
- [https://docs.crawl4ai.com/extraction/llm-strategies](https://docs.crawl4ai.com/extraction/llm-strategies)
- [https://docs.crawl4ai.com/extraction/no-llm-strategies](https://docs.crawl4ai.com/extraction/no-llm-strategies)
- [https://docs.crawl4ai.com/fit-markdown](https://docs.crawl4ai.com/fit-markdown)
- [https://docs.crawl4ai.com/installation](https://docs.crawl4ai.com/installation)
- [https://docs.crawl4ai.com/link-media](https://docs.crawl4ai.com/link-media)
- [https://docs.crawl4ai.com/local-files](https://docs.crawl4ai.com/local-files)
- [https://docs.crawl4ai.com/markdown-generation](https://docs.crawl4ai.com/markdown-generation)
- [https://docs.crawl4ai.com/page-interaction](https://docs.crawl4ai.com/page-interaction)
- [https://docs.crawl4ai.com/quickstart](https://docs.crawl4ai.com/quickstart)

## 🤖 LLM Training Notes

This document is structured for both human readability and LLM training:

1. 📚 **Metadata Section**: Contains document classification and context
2. 📋 **Quick Summary**: High-level overview of the content
3. 🔧 **Technical Context**: Programming languages and key terms
4. 📖 **Main Content**: Organized with:
   - Clear section headers
   - Code examples with language tags
   - Step-by-step instructions
   - Important points and notes clearly marked
5. 🔗 **Related Resources**: Links to additional information

Special markers used:
- ❗ Important: Critical information
- 💡 Note: Additional context
- 🔍 Instructions: Step-by-step procedures
- ```language: Code blocks with language specification
