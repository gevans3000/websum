# Browser & Crawler Config - Crawl4AI Documentation (v0.4.3bx)

## 📚 Document Metadata

```yaml
title: Browser & Crawler Config - Crawl4AI Documentation (v0.4.3bx)
source_url: https://docs.crawl4ai.com/core/browser-crawler-config/
category: python/config
keywords: python, web scraping, configuration, browser, crawler
last_modified: Unknown
type: Technical Documentation
```

## 📋 Quick Summary

Configuration options for browser-based web crawling in Crawl4AI

## 🔧 Technical Context

### Key Technical Terms
- AsyncWebCrawler
- ` turns off certain background features for performance. 
10. **`
- `

## 2. CrawlerRunConfig Essentials
`
- ` , no structured extraction is done (only raw/cleaned HTML + markdown).
3. **`
- `**: - If you want to start with specific cookies or add universal HTTP headers, set them here. - E.g.`
- ` , captures a screenshot or PDF after the page is fully loaded. - The results go to `
- ` , a default is used. - You can also set `
- `**: - Logs additional runtime details. - Overlaps with the browser’s verbosity if also set to`
- `.
8. **`
- `**: - If`
- ` depending on each call’s needs:
`
- ` : Runs the browser in headless mode (invisible browser). - `
- `**: -`
- debug_browser
- base_browser
- proxy_config
- CrawlerRunConfig
- max_session_permit
- `, you can enable intelligent rate limiting:
`
- base_config
- max_retries
- `CrawlerRunConfig`
- run_conf
- `**: - The memory threshold (as a percentage) to monitor. - If exceeded, the crawler will pause or slow down.
12. **`
- display_mode
- `**- A dictionary with fields like:
`
- ` to be set.
10. **`
- ` , enables rate limiting for batch processing. - Requires `
- `.
7. **`
- memory_threshold_percent
- `: Runs the browser in visible mode, which helps with debugging.
3. **`
- debug_config
- `, etc.). - Affects how much information is printed during the crawl.
### Helper Methods
The `
- `
class BrowserConfig:
  def __init__(
    browser_type="chromium",
    headless=True,
    proxy_config=None,
    viewport_width=1080,
    viewport_height=600,
    verbose=True,
    use_persistent_context=False,
    user_data_dir=None,
    cookies=None,
    headers=None,
    user_agent=None,
    text_mode=False,
    light_mode=False,
    extra_args=None,
    # ... other advanced parameters omitted here
  ):
    ...

`
- ` disables images, possibly speeding up text-only crawls. - `
- `
class CrawlerRunConfig:
  def __init__(
    word_count_threshold=200,
    extraction_strategy=None,
    markdown_generator=None,
    cache_mode=None,
    js_code=None,
    wait_for=None,
    screenshot=False,
    pdf=False,
    enable_rate_limiting=False,
    rate_limit_config=None,
    memory_threshold_percent=70.0,
    check_interval=1.0,
    max_session_permit=20,
    display_mode=None,
    verbose=True,
    stream=False, # Enable streaming for arun_many()
    # ... other advanced parameters omitted
  ):
    ...

`
- `. - Defaults to `
- markdown_generator
- ` for randomization (if you want to fight bot detection).
9. **`
- JavaScript
- base_delay
- crawl_conf
- `**: - Where you plug in JSON-based extraction (CSS, LLM, etc.). - If`
- `
# Create a base configuration
base_config = CrawlerRunConfig(
  cache_mode=CacheMode.ENABLED,
  word_count_threshold=200,
  wait_until="networkidle"
)
# Create variations for different use cases
stream_config = base_config.clone(
  stream=True, # Enable streaming mode
  cache_mode=CacheMode.BYPASS
)
debug_config = base_config.clone(
  page_timeout=120000, # Longer timeout for debugging
  verbose=True
)

`
- ` method is particularly useful for creating variations of your crawler configuration:
`
- max_delay
- JSON
- viewport_height
- DefaultMarkdownGenerator
- `, defaults to some level of caching or you can specify `
- `**: - A CSS or JS expression to wait for before extracting content. - Common usage:`
- RateLimitConfig
- user_agent_mode
- wait_for
- user_agent
- ` & `
- wait_until
- `arun()`
- `

## 3. Putting It All Together
In a typical scenario, you define **one** `
- use_persistent_context
- `

The `
- `. - If you need a different engine, specify it here.
2. **`
- `.
9. **`
- ` (base64) or `
- enable_rate_limiting
- `**: - The display mode for progress information (`
- `, `
- browser_conf
- `
from crawl4ai import AsyncWebCrawler, BrowserConfig
browser_conf = BrowserConfig(
  browser_type="firefox",
  headless=False,
  text_mode=True
)
async with AsyncWebCrawler(config=browser_conf) as crawler:
  result = await crawler.arun("https://example.com")
  print(result.markdown[:300])

`
- `, a default approach is used.
4. **`
- `**: - Additional flags for the underlying browser. - E.g.`
- cache_mode
- ` if a proxy is not required. 
4. **`
- user_data_dir
- ` method: - Creates a new instance with all the same settings - Updates only the specified parameters - Leaves the original configuration unchanged - Perfect for creating variations without repeating all parameters
### Rate Limiting & Resource Management
For batch processing with `
- browser_type
- light_mode
- ` in `
- `

This configuration: - Implements intelligent rate limiting per domain - Monitors system resources - Provides detailed progress information - Manages concurrent crawls efficiently
**Minimal Example** :
`
- object
- viewport_width
- CSS
- `**: - The interval (in seconds) to check system resources. - Affects how often memory and CPU usage are monitored.
13. **`
- `.
### Helper Methods
Both configuration classes provide a `
- extra_args
- extraction_strategy
- `**: - A`
- `**: - E.g.,`
- rate_limit_codes
- HTTP
- `

**Minimal Example** :
`
- `**: - The initial window size. - Some sites behave differently with smaller or bigger viewports.
5. **`
- js_code
- `**: - Controls caching behavior (`
- `
# Create a base browser config
base_browser = BrowserConfig(
  browser_type="chromium",
  headless=True,
  text_mode=True
)
# Create a visible browser config for debugging
debug_browser = base_browser.clone(
  headless=False,
  verbose=True
)

`
- `, etc.). - If `
- ` , uses a **persistent** browser profile, storing cookies/local storage across runs. - Typically also set `
- check_interval
- `**: - The maximum number of concurrent crawl sessions. - Helps prevent overwhelming the system.
14. **`
- ` , prints extra logs. - Handy for debugging.
6. **`
- `

- Leave as `
- CacheMode
- `
from crawl4ai import RateLimitConfig
config = CrawlerRunConfig(
  enable_rate_limiting=True,
  rate_limit_config=RateLimitConfig(
    base_delay=(1.0, 3.0),  # Random delay range
    max_delay=60.0,      # Max delay after rate limits
    max_retries=3,      # Retries before giving up
    rate_limit_codes=[429, 503] # Status codes to watch
  ),
  memory_threshold_percent=70.0, # Memory threshold
  check_interval=1.0,      # Resource check interval
  max_session_permit=20,     # Max concurrent crawls
  display_mode="DETAILED"    # Progress display mode
)

`
- `**- Options:`
- extracted_content
- ` method to create modified copies:
`
- text_mode
- `
from crawl4ai import AsyncWebCrawler, CrawlerRunConfig
crawl_conf = CrawlerRunConfig(
  js_code="document.querySelector('button#loadMore')?.click()",
  wait_for="css:.loaded-content",
  screenshot=True,
  enable_rate_limiting=True,
  rate_limit_config=RateLimitConfig(
    base_delay=(1.0, 3.0),
    max_delay=60.0,
    max_retries=3,
    rate_limit_codes=[429, 503]
  ),
  stream=True # Enable streaming
)
async with AsyncWebCrawler() as crawler:
  result = await crawler.arun(url="https://example.com", config=crawl_conf)
  print(result.screenshot[:100]) # Base64-encoded PNG snippet

`
- `
{
  "server": "http://proxy.example.com:8080", 
  "username": "...", 
  "password": "..."
}

`
- ` , controlling how HTML→Markdown conversion is done. - If `
- ` to point to a folder.
7. **`
- class
- stream_config
- ` , `
- word_count_threshold
- ` or `
- arun_many
- `.
5. **`
- `**-`
- `**: - A string or list of JS strings to execute. - Great for “Load More” buttons or user interactions.
6. **`
- `**: - The minimum word count before a block is considered. - If your site has lots of short paragraphs or items, you can lower it.
2. **`
- `
import asyncio
from crawl4ai import AsyncWebCrawler, BrowserConfig, CrawlerRunConfig, CacheMode
from crawl4ai.extraction_strategy import JsonCssExtractionStrategy
async def main():
  # 1) Browser config: headless, bigger viewport, no proxy
  browser_conf = BrowserConfig(
    headless=True,
    viewport_width=1280,
    viewport_height=720
  )
  # 2) Example extraction strategy
  schema = {
    "name": "Articles",
    "baseSelector": "div.article",
    "fields": [
      {"name": "title", "selector": "h2", "type": "text"},
      {"name": "link", "selector": "a", "type": "attribute", "attribute": "href"}
    ]
  }
  extraction = JsonCssExtractionStrategy(schema)
  # 3) Crawler run config: skip cache, use extraction
  run_conf = CrawlerRunConfig(
    extraction_strategy=extraction,
    cache_mode=CacheMode.BYPASS,
    enable_rate_limiting=True,
    rate_limit_config=RateLimitConfig(
      base_delay=(1.0, 3.0),
      max_delay=60.0,
      max_retries=3,
      rate_limit_codes=[429, 503]
    )
  )
  async with AsyncWebCrawler(config=browser_conf) as crawler:
    # 4) Execute the crawl
    result = await crawler.arun(url="https://example.com/news", config=run_conf)
    if result.success:
      print("Extracted content:", result.extracted_content)
    else:
      print("Error:", result.error_message)
if __name__ == "__main__":
  asyncio.run(main())

`
- `**: - Custom User-Agent string. If`
- `

### Key Fields to Note
1. **`
- page_timeout
- error_message
- HTML
- BrowserConfig
- rate_limit_config
- `** & **`
- method
- JsonCssExtractionStrategy
- ` (bytes).
8. **`
- `, or `
- ` object controlling rate limiting behavior. - See below for details.
11. **`
- ` for your crawler session, then create **one or more** `
- `BrowserConfig`

## 📖 Main Content

### Browser & Crawler Configuration (Quick Overview)

Crawl4AI’s flexibility stems from two key classes:

🔍 Instructions:

• ❗ Important: `BrowserConfig`– Dictates❗ Important: how the browser is launched and behaves (e.g., headless or visible, proxy, user agent). 2. ❗ Important: `CrawlerRunConfig`– Dictates❗ Important: how each ❗ Important: crawl operates (e.g., caching, extraction, timeouts, JavaScript code to run, etc.).

In most examples, you create ❗ Important: one `BrowserConfig` for the entire crawler session, then pass a ❗ Important: fresh or re-used `CrawlerRunConfig` whenever you call `arun()`. This tutorial shows the most commonly used parameters. If you need advanced or rarely used fields, see the [Configuration Parameters](https://docs.crawl4ai.com/core/browser-crawler-config/api/parameters/>).

#### 1. BrowserConfig Essentials


Code Example (text):
```text
class BrowserConfig:
  def __init__(
    browser_type="chromium",
    headless=True,
    proxy_config=None,
    viewport_width=1080,
    viewport_height=600,
    verbose=True,
    use_persistent_context=False,
    user_data_dir=None,
    cookies=None,
    headers=None,
    user_agent=None,
    text_mode=False,
    light_mode=False,
    extra_args=None,
    # ... other advanced parameters omitted here
  ):
    ...
```




##### Key Fields to Note


🔍 Instructions:

• ❗ Important: `browser_type`- Options:`"chromium"` , `"firefox"`, or `"webkit"`. - Defaults to `"chromium"`. - If you need a different engine, specify it here.
• ❗ Important: `headless`-`True` : Runs the browser in headless mode (invisible browser). - `False`: Runs the browser in visible mode, which helps with debugging.
• ❗ Important: `proxy_config`- A dictionary with fields like:


Code Example (text):
```text
{
  "server": "http://proxy.example.com:8080", 
  "username": "...", 
  "password": "..."
}
```




🔍 Instructions:

• Leave as `None` if a proxy is not required. 
• ❗ Important: `viewport_width` & `viewport_height`: - The initial window size. - Some sites behave differently with smaller or bigger viewports.
• ❗ Important: `verbose`: - If`True` , prints extra logs. - Handy for debugging.
• ❗ Important: `use_persistent_context`: - If`True` , uses a ❗ Important: persistent browser profile, storing cookies/local storage across runs. - Typically also set `user_data_dir` to point to a folder.
• ❗ Important: `cookies` & ❗ Important: `headers`: - If you want to start with specific cookies or add universal HTTP headers, set them here. - E.g.`cookies=[{"name": "session", "value": "abc123", "domain": "example.com"}]`.
• ❗ Important: `user_agent`: - Custom User-Agent string. If`None` , a default is used. - You can also set `user_agent_mode="random"` for randomization (if you want to fight bot detection).
• ❗ Important: `text_mode` & ❗ Important: `light_mode`: -`text_mode=True` disables images, possibly speeding up text-only crawls. - `light_mode=True` turns off certain background features for performance. 
• ❗ Important: `extra_args`: - Additional flags for the underlying browser. - E.g.`["--disable-extensions"]`.

##### Helper Methods

Both configuration classes provide a `clone()` method to create modified copies:
```

### Create a base browser config

base_browser = BrowserConfig(
  browser_type="chromium",
  headless=True,
  text_mode=True
)

### Create a visible browser config for debugging

debug_browser = base_browser.clone(
  headless=False,
  verbose=True
)


Code Example (text):
```text
**Minimal Example** :
```


from crawl4ai import AsyncWebCrawler, BrowserConfig
browser_conf = BrowserConfig(
  browser_type="firefox",
  headless=False,
  text_mode=True
)
async with AsyncWebCrawler(config=browser_conf) as crawler:
  result = await crawler.arun("https://example.com")
  print(result.markdown[:300])

```


#### 2. CrawlerRunConfig Essentials


Code Example (text):
```text
class CrawlerRunConfig:
  def __init__(
    word_count_threshold=200,
    extraction_strategy=None,
    markdown_generator=None,
    cache_mode=None,
    js_code=None,
    wait_for=None,
    screenshot=False,
    pdf=False,
    enable_rate_limiting=False,
    rate_limit_config=None,
    memory_threshold_percent=70.0,
    check_interval=1.0,
    max_session_permit=20,
    display_mode=None,
    verbose=True,
    stream=False, # Enable streaming for arun_many()
    # ... other advanced parameters omitted
  ):
    ...
```




##### Key Fields to Note


🔍 Instructions:

• ❗ Important: `word_count_threshold`: - The minimum word count before a block is considered. - If your site has lots of short paragraphs or items, you can lower it.
• ❗ Important: `extraction_strategy`: - Where you plug in JSON-based extraction (CSS, LLM, etc.). - If`None` , no structured extraction is done (only raw/cleaned HTML + markdown).
• ❗ Important: `markdown_generator`: - E.g.,`DefaultMarkdownGenerator(...)` , controlling how HTML→Markdown conversion is done. - If `None`, a default approach is used.
• ❗ Important: `cache_mode`: - Controls caching behavior (`ENABLED` , `BYPASS`, `DISABLED`, etc.). - If `None`, defaults to some level of caching or you can specify `CacheMode.ENABLED`.
• ❗ Important: `js_code`: - A string or list of JS strings to execute. - Great for “Load More” buttons or user interactions.
• ❗ Important: `wait_for`: - A CSS or JS expression to wait for before extracting content. - Common usage:`wait_for="css:.main-loaded"` or `wait_for="js:() => window.loaded === true"`.
• ❗ Important: `screenshot` & ❗ Important: `pdf`: - If`True` , captures a screenshot or PDF after the page is fully loaded. - The results go to `result.screenshot` (base64) or `result.pdf` (bytes).
• ❗ Important: `verbose`: - Logs additional runtime details. - Overlaps with the browser’s verbosity if also set to`True` in `BrowserConfig`.
• ❗ Important: `enable_rate_limiting`: - If`True` , enables rate limiting for batch processing. - Requires `rate_limit_config` to be set.
• ❗ Important: `rate_limit_config`: - A`RateLimitConfig` object controlling rate limiting behavior. - See below for details.
• ❗ Important: `memory_threshold_percent`: - The memory threshold (as a percentage) to monitor. - If exceeded, the crawler will pause or slow down.
• ❗ Important: `check_interval`: - The interval (in seconds) to check system resources. - Affects how often memory and CPU usage are monitored.
• ❗ Important: `max_session_permit`: - The maximum number of concurrent crawl sessions. - Helps prevent overwhelming the system.
• ❗ Important: `display_mode`: - The display mode for progress information (`DETAILED` , `BRIEF`, etc.). - Affects how much information is printed during the crawl.

##### Helper Methods

The `clone()` method is particularly useful for creating variations of your crawler configuration:
```

### Create a base configuration

base_config = CrawlerRunConfig(
  cache_mode=CacheMode.ENABLED,
  word_count_threshold=200,
  wait_until="networkidle"
)

### Create variations for different use cases

stream_config = base_config.clone(
  stream=True, # Enable streaming mode
  cache_mode=CacheMode.BYPASS
)
debug_config = base_config.clone(
  page_timeout=120000, # Longer timeout for debugging
  verbose=True
)

```

The `clone()` method: - Creates a new instance with all the same settings - Updates only the specified parameters - Leaves the original configuration unchanged - Perfect for creating variations without repeating all parameters

##### Rate Limiting & Resource Management

For batch processing with `arun_many()`, you can enable intelligent rate limiting:

Code Example (text):
```text
from crawl4ai import RateLimitConfig
config = CrawlerRunConfig(
  enable_rate_limiting=True,
  rate_limit_config=RateLimitConfig(
    base_delay=(1.0, 3.0),  # Random delay range
    max_delay=60.0,      # Max delay after rate limits
    max_retries=3,      # Retries before giving up
    rate_limit_codes=[429, 503] # Status codes to watch
  ),
  memory_threshold_percent=70.0, # Memory threshold
  check_interval=1.0,      # Resource check interval
  max_session_permit=20,     # Max concurrent crawls
  display_mode="DETAILED"    # Progress display mode
)
```



This configuration: - Implements intelligent rate limiting per domain - Monitors system resources - Provides detailed progress information - Manages concurrent crawls efficiently
❗ Important: Minimal Example :

Code Example (text):
```text
from crawl4ai import AsyncWebCrawler, CrawlerRunConfig
crawl_conf = CrawlerRunConfig(
  js_code="document.querySelector('button#loadMore')?.click()",
  wait_for="css:.loaded-content",
  screenshot=True,
  enable_rate_limiting=True,
  rate_limit_config=RateLimitConfig(
    base_delay=(1.0, 3.0),
    max_delay=60.0,
    max_retries=3,
    rate_limit_codes=[429, 503]
  ),
  stream=True # Enable streaming
)
async with AsyncWebCrawler() as crawler:
  result = await crawler.arun(url="https://example.com", config=crawl_conf)
  print(result.screenshot[:100]) # Base64-encoded PNG snippet
```




#### 3. Putting It All Together

In a typical scenario, you define ❗ Important: one `BrowserConfig` for your crawler session, then create ❗ Important: one or more `CrawlerRunConfig` depending on each call’s needs:

Code Example (text):
```text
import asyncio
from crawl4ai import AsyncWebCrawler, BrowserConfig, CrawlerRunConfig, CacheMode
from crawl4ai.extraction_strategy import JsonCssExtractionStrategy
async def main():
  # 1) Browser config: headless, bigger viewport, no proxy
  browser_conf = BrowserConfig(
    headless=True,
    viewport_width=1280,
    viewport_height=720
  )
  # 2) Example extraction strategy
  schema = {
    "name": "Articles",
    "baseSelector": "div.article",
    "fields": [
      {"name": "title", "selector": "h2", "type": "text"},
      {"name": "link", "selector": "a", "type": "attribute", "attribute": "href"}
    ]
  }
  extraction = JsonCssExtractionStrategy(schema)
  # 3) Crawler run config: skip cache, use extraction
  run_conf = CrawlerRunConfig(
    extraction_strategy=extraction,
    cache_mode=CacheMode.BYPASS,
    enable_rate_limiting=True,
    rate_limit_config=RateLimitConfig(
      base_delay=(1.0, 3.0),
      max_delay=60.0,
      max_retries=3,
      rate_limit_codes=[429, 503]
    )
  )
  async with AsyncWebCrawler(config=browser_conf) as crawler:
    # 4) Execute the crawl
    result = await crawler.arun(url="https://example.com/news", config=run_conf)
    if result.success:
      print("Extracted content:", result.extracted_content)
    else:
      print("Error:", result.error_message)
if __name__ == "__main__":
  asyncio.run(main())
```




#### 4. Next Steps

For a ❗ Important: detailed list of available parameters (including advanced ones), see:

🔍 Instructions:

• [BrowserConfig and CrawlerRunConfig Reference](https://docs.crawl4ai.com/core/browser-crawler-config/api/parameters/>)



You can explore topics like:

🔍 Instructions:

• ❗ Important: Custom Hooks & Auth (Inject JavaScript or handle login forms). 
• ❗ Important: Session Management (Re-use pages, preserve state across multiple calls). 
• ❗ Important: Magic Mode or ❗ Important: Identity-based Crawling (Fight bot detection by simulating user behavior). 
• ❗ Important: Advanced Caching (Fine-tune read/write cache modes). 




#### 5. Conclusion

❗ Important: BrowserConfig and ❗ Important: CrawlerRunConfig give you straightforward ways to define:

🔍 Instructions:

• ❗ Important: Which browser to launch, how it should run, and any proxy or user agent needs. 
• ❗ Important: How each crawl should behave—caching, timeouts, JavaScript code, extraction strategies, etc.



Use them together for ❗ Important: clear, maintainable code, and when you need more specialized behavior, check out the advanced parameters in the [reference docs](https://docs.crawl4ai.com/core/browser-crawler-config/api/parameters/>). Happy crawling!

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
- [https://docs.crawl4ai.com/core/cache-modes](https://docs.crawl4ai.com/core/cache-modes)
- [https://docs.crawl4ai.com/core/content-selection](https://docs.crawl4ai.com/core/content-selection)
- [https://docs.crawl4ai.com/core/crawler-result](https://docs.crawl4ai.com/core/crawler-result)
- [https://docs.crawl4ai.com/core/docker-deploymeny](https://docs.crawl4ai.com/core/docker-deploymeny)
- [https://docs.crawl4ai.com/core/fit-markdown](https://docs.crawl4ai.com/core/fit-markdown)
- [https://docs.crawl4ai.com/core/installation](https://docs.crawl4ai.com/core/installation)
- [https://docs.crawl4ai.com/core/link-media](https://docs.crawl4ai.com/core/link-media)
- [https://docs.crawl4ai.com/core/local-files](https://docs.crawl4ai.com/core/local-files)
- [https://docs.crawl4ai.com/core/markdown-generation](https://docs.crawl4ai.com/core/markdown-generation)
- [https://docs.crawl4ai.com/core/page-interaction](https://docs.crawl4ai.com/core/page-interaction)
- [https://docs.crawl4ai.com/core/quickstart](https://docs.crawl4ai.com/core/quickstart)
- [https://docs.crawl4ai.com/core/simple-crawling](https://docs.crawl4ai.com/core/simple-crawling)
- [https://docs.crawl4ai.com/extraction/chunking](https://docs.crawl4ai.com/extraction/chunking)
- [https://docs.crawl4ai.com/extraction/clustring-strategies](https://docs.crawl4ai.com/extraction/clustring-strategies)
- [https://docs.crawl4ai.com/extraction/llm-strategies](https://docs.crawl4ai.com/extraction/llm-strategies)
- [https://docs.crawl4ai.com/extraction/no-llm-strategies](https://docs.crawl4ai.com/extraction/no-llm-strategies)

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
