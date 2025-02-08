# Browser & Crawler Config

# 1. **BrowserConfig** – Controlling the Browser
```python
BrowserConfig
``` focuses on **how** the browser is launched and behaves. This includes headless mode, proxies, user agents, and other environment tweaks.
`````python
from crawl4ai import AsyncWebCrawler, BrowserConfig
browser_cfg = BrowserConfig(
  browser_type="chromium",
  headless=True,
  viewport_width=1280,
  viewport_height=720,
  proxy="http://user:pass@proxy:8080",
  user_agent="Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/116.0.0.0 Safari/537.36",
)

```````python

## 1.1 Parameter Highlights
**Parameter** | **Type / Default** | **What It Does**  
---|---|---  
**
```browser_type```python
**| 
```"chromium"```python
 , 
```"firefox"```python
, 
```"webkit"```python
_(default:
```"chromium"```python
)_ | Which browser engine to use. 
```"chromium"```python
 is typical for many sites, 
```"firefox"```python
 or 
```"webkit"```python
 for specialized tests.  
**
```headless```python
**| 
```bool```python
 (default: 
```True```python
) | Headless means no visible UI. 
```False```python
 is handy for debugging.  
**
```viewport_width```python
**| 
```int```python
 (default: 
```1080```python
) | Initial page width (in px). Useful for testing responsive layouts.  
**
```viewport_height```python
**| 
```int```python
 (default: 
```600```python
) | Initial page height (in px).  
**
```proxy```python
**| 
```str```python
 (default: 
```None```python
) | Single-proxy URL if you want all traffic to go through it, e.g. 
```"http://user:pass@proxy:8080"```python
.  
**
```proxy_config```python
**| 
```dict```python
 (default: 
```None```python
) | For advanced or multi-proxy needs, specify details like 
```{"server": "...", "username": "...", ...}```python
.  
**
```use_persistent_context```python
**| 
```bool```python
 (default: 
```False```python
) | If 
```True```python
, uses a **persistent** browser context (keep cookies, sessions across runs). Also sets 
```use_managed_browser=True```python
.  
**
```user_data_dir```python
**| 
```str or None```python
 (default: 
```None```python
) | Directory to store user data (profiles, cookies). Must be set if you want permanent sessions.  
**
```ignore_https_errors```python
**| 
```bool```python
 (default: 
```True```python
) | If 
```True```python
, continues despite invalid certificates (common in dev/staging).  
**
```java_script_enabled```python
**| 
```bool```python
 (default: 
```True```python
) | Disable if you want no JS overhead, or if only static content is needed.  
**
```cookies```python
**| 
```list```python
 (default: 
```[]```python
) | Pre-set cookies, each a dict like 
```{"name": "session", "value": "...", "url": "..."}```python
.  
**
```headers```python
**| 
```dict```python
 (default: 
```{}```python
) | Extra HTTP headers for every request, e.g. 
```{"Accept-Language": "en-US"}```python
.  
**
```user_agent```python
**| 
```str```python
 (default: Chrome-based UA) | Your custom or random user agent. 
```user_agent_mode="random"```python
 can shuffle it.  
**
```light_mode```python
**| 
```bool```python
 (default: 
```False```python
) | Disables some background features for performance gains.  
**
```text_mode```python
**| 
```bool```python
 (default: 
```False```python
) | If 
```True```python
, tries to disable images/other heavy content for speed.  
**
```use_managed_browser```python
**| 
```bool```python
 (default: 
```False```python
) | For advanced “managed” interactions (debugging, CDP usage). Typically set automatically if persistent context is on.  
**
```extra_args```python
**| 
```list```python
 (default: 
```[]```python
) | Additional flags for the underlying browser process, e.g. 
```["--disable-extensions"]```python
.  
**Tips** : - Set 
```headless=False```python
 to visually **debug** how pages load or how interactions proceed. - If you need **authentication** storage or repeated sessions, consider 
```use_persistent_context=True```python
 and specify 
```user_data_dir```python
. - For large pages, you might need a bigger 
```viewport_width```python
 and 
```viewport_height```python
 to handle dynamic content.
# 2. **CrawlerRunConfig** – Controlling Each Crawl
While 
```BrowserConfig```python
 sets up the **environment** , 
```CrawlerRunConfig```python
 details **how** each **crawl operation** should behave: caching, content filtering, link or domain blocking, timeouts, JavaScript code, etc.
```````python
from crawl4ai import AsyncWebCrawler, CrawlerRunConfig
run_cfg = CrawlerRunConfig(
  wait_for="css:.main-content",
  word_count_threshold=15,
  excluded_tags=["nav", "footer"],
  exclude_external_links=True,
  stream=True, # Enable streaming for arun_many()
)

```````python

## 2.1 Parameter Highlights
We group them by category. 
### A) **Content Processing**
**Parameter** | **Type / Default** | **What It Does**  
---|---|---  
**
```word_count_threshold```python
**| 
```int```python
 (default: ~200) | Skips text blocks below X words. Helps ignore trivial sections.  
**
```extraction_strategy```python
**| 
```ExtractionStrategy```python
 (default: None) | If set, extracts structured data (CSS-based, LLM-based, etc.).  
**
```markdown_generator```python
**| 
```MarkdownGenerationStrategy```python
 (None) | If you want specialized markdown output (citations, filtering, chunking, etc.).  
**
```content_filter```python
**| 
```RelevantContentFilter```python
 (None) | Filters out irrelevant text blocks. E.g., 
```PruningContentFilter```python
 or 
```BM25ContentFilter```python
.  
**
```css_selector```python
**| 
```str```python
 (None) | Retains only the part of the page matching this selector.  
**
```excluded_tags```python
**| 
```list```python
 (None) | Removes entire tags (e.g. 
```["script", "style"]```python
).  
**
```excluded_selector```python
**| 
```str```python
 (None) | Like 
```css_selector```python
 but to exclude. E.g. 
```"#ads, .tracker"```python
.  
**
```only_text```python
**| 
```bool```python
 (False) | If 
```True```python
, tries to extract text-only content.  
**
```prettiify```python
**| 
```bool```python
 (False) | If 
```True```python
, beautifies final HTML (slower, purely cosmetic).  
**
```keep_data_attributes```python
**| 
```bool```python
 (False) | If 
```True```python
, preserve 
```data-*```python
 attributes in cleaned HTML.  
**
```remove_forms```python
**| 
```bool```python
 (False) | If 
```True```python
, remove all 
```<form>```python
 elements.  
### B) **Caching & Session**
**Parameter** | **Type / Default** | **What It Does**  
---|---|---  
**
```cache_mode```python
**| 
```CacheMode or None```python
 | Controls how caching is handled (
```ENABLED```python
, 
```BYPASS```python
, 
```DISABLED```python
, etc.). If 
```None```python
, typically defaults to 
```ENABLED```python
.  
**
```session_id```python
**| 
```str or None```python
 | Assign a unique ID to reuse a single browser session across multiple 
```arun()```python
 calls.  
**
```bypass_cache```python
**| 
```bool```python
 (False) | If 
```True```python
, acts like 
```CacheMode.BYPASS```python
.  
**
```disable_cache```python
**| 
```bool```python
 (False) | If 
```True```python
, acts like 
```CacheMode.DISABLED```python
.  
**
```no_cache_read```python
**| 
```bool```python
 (False) | If 
```True```python
, acts like 
```CacheMode.WRITE_ONLY```python
 (writes cache but never reads).  
**
```no_cache_write```python
**| 
```bool```python
 (False) | If 
```True```python
, acts like 
```CacheMode.READ_ONLY```python
 (reads cache but never writes).  
Use these for controlling whether you read or write from a local content cache. Handy for large batch crawls or repeated site visits.
### C) **Page Navigation & Timing**
**Parameter** | **Type / Default** | **What It Does**  
---|---|---  
**
```wait_until```python
**| 
```str```python
 (domcontentloaded) | Condition for navigation to “complete”. Often 
```"networkidle"```python
 or 
```"domcontentloaded"```python
.  
**
```page_timeout```python
**| 
```int```python
 (60000 ms) | Timeout for page navigation or JS steps. Increase for slow sites.  
**
```wait_for```python
**| 
```str or None```python
 | Wait for a CSS (
```"css:selector"```python
) or JS (
```"js:() => bool"```python
) condition before content extraction.  
**
```wait_for_images```python
**| 
```bool```python
 (False) | Wait for images to load before finishing. Slows down if you only want text.  
**
```delay_before_return_html```python
**| 
```float```python
 (0.1) | Additional pause (seconds) before final HTML is captured. Good for last-second updates.  
**
```check_robots_txt```python
**| 
```bool```python
 (False) | Whether to check and respect robots.txt rules before crawling. If True, caches robots.txt for efficiency.  
**
```mean_delay```python
**and**
```max_range```python
**| 
```float```python
 (0.1, 0.3) | If you call 
```arun_many()```python
, these define random delay intervals between crawls, helping avoid detection or rate limits.  
**
```semaphore_count```python
**| 
```int```python
 (5) | Max concurrency for 
```arun_many()```python
. Increase if you have resources for parallel crawls.  
### D) **Page Interaction**
**Parameter** | **Type / Default** | **What It Does**  
---|---|---  
**
```js_code```python
**| 
```str or list[str]```python
 (None) | JavaScript to run after load. E.g. 
```"document.querySelector('button')?.click();"```python
.  
**
```js_only```python
**| 
```bool```python
 (False) | If 
```True```python
, indicates we’re reusing an existing session and only applying JS. No full reload.  
**
```ignore_body_visibility```python
**| 
```bool```python
 (True) | Skip checking if 
```<body>```python
 is visible. Usually best to keep 
```True```python
.  
**
```scan_full_page```python
**| 
```bool```python
 (False) | If 
```True```python
, auto-scroll the page to load dynamic content (infinite scroll).  
**
```scroll_delay```python
**| 
```float```python
 (0.2) | Delay between scroll steps if 
```scan_full_page=True```python
.  
**
```process_iframes```python
**| 
```bool```python
 (False) | Inlines iframe content for single-page extraction.  
**
```remove_overlay_elements```python
**| 
```bool```python
 (False) | Removes potential modals/popups blocking the main content.  
**
```simulate_user```python
**| 
```bool```python
 (False) | Simulate user interactions (mouse movements) to avoid bot detection.  
**
```override_navigator```python
**| 
```bool```python
 (False) | Override 
```navigator```python
 properties in JS for stealth.  
**
```magic```python
**| 
```bool```python
 (False) | Automatic handling of popups/consent banners. Experimental.  
**
```adjust_viewport_to_content```python
**| 
```bool```python
 (False) | Resizes viewport to match page content height.  
If your page is a single-page app with repeated JS updates, set 
```js_only=True```python
 in subsequent calls, plus a 
```session_id```python
 for reusing the same tab.
### E) **Media Handling**
**Parameter** | **Type / Default** | **What It Does**  
---|---|---  
**
```screenshot```python
**| 
```bool```python
 (False) | Capture a screenshot (base64) in 
```result.screenshot```python
.  
**
```screenshot_wait_for```python
**| 
```float or None```python
 | Extra wait time before the screenshot.  
**
```screenshot_height_threshold```python
**| 
```int```python
 (~20000) | If the page is taller than this, alternate screenshot strategies are used.  
**
```pdf```python
**| 
```bool```python
 (False) | If 
```True```python
, returns a PDF in 
```result.pdf```python
.  
**
```image_description_min_word_threshold```python
**| 
```int```python
 (~50) | Minimum words for an image’s alt text or description to be considered valid.  
**
```image_score_threshold```python
**| 
```int```python
 (~3) | Filter out low-scoring images. The crawler scores images by relevance (size, context, etc.).  
**
```exclude_external_images```python
**| 
```bool```python
 (False) | Exclude images from other domains.  
### F) **Link/Domain Handling**
**Parameter** | **Type / Default** | **What It Does**  
---|---|---  
**
```exclude_social_media_domains```python
**| 
```list```python
 (e.g. Facebook/Twitter) | A default list can be extended. Any link to these domains is removed from final output.  
**
```exclude_external_links```python
**| 
```bool```python
 (False) | Removes all links pointing outside the current domain.  
**
```exclude_social_media_links```python
**| 
```bool```python
 (False) | Strips links specifically to social sites (like Facebook or Twitter).  
**
```exclude_domains```python
**| 
```list```python
 ([]) | Provide a custom list of domains to exclude (like 
```["ads.com", "trackers.io"]```python
).  
Use these for link-level content filtering (often to keep crawls “internal” or to remove spammy domains).
### G) **Rate Limiting & Resource Management**
**Parameter** | **Type / Default** | **What It Does**  
---|---|---  
**
```enable_rate_limiting```python
**| 
```bool```python
 (default: 
```False```python
) | Enable intelligent rate limiting for multiple URLs  
**
```rate_limit_config```python
**| 
```RateLimitConfig```python
 (default: 
```None```python
) | Configuration for rate limiting behavior  
The 
```RateLimitConfig```python
 class has these fields:
**Field** | **Type / Default** | **What It Does**  
---|---|---  
**
```base_delay```python
**| 
```Tuple[float, float]```python
 (1.0, 3.0) | Random delay range between requests to the same domain  
**
```max_delay```python
**| 
```float```python
 (60.0) | Maximum delay after rate limit detection  
**
```max_retries```python
**| 
```int```python
 (3) | Number of retries before giving up on rate-limited requests  
**
```rate_limit_codes```python
**| 
```List[int]```python
 ([429, 503]) | HTTP status codes that trigger rate limiting behavior  
**Parameter** | **Type / Default** | **What It Does**  
---|---|---  
**
```memory_threshold_percent```python
**| 
```float```python
 (70.0) | Maximum memory usage before pausing new crawls  
**
```check_interval```python
**| 
```float```python
 (1.0) | How often to check system resources (in seconds)  
**
```max_session_permit```python
**| 
```int```python
 (20) | Maximum number of concurrent crawl sessions  
**
```display_mode```python
**| 
```str```python
 (
```None```python
, "DETAILED", "AGGREGATED") | How to display progress information  
### H) **Debug & Logging**
**Parameter** | **Type / Default** | **What It Does**  
---|---|---  
**
```verbose```python
**| 
```bool```python
 (True) | Prints logs detailing each step of crawling, interactions, or errors.  
**
```log_console```python
**| 
```bool```python
 (False) | Logs the page’s JavaScript console output if you want deeper JS debugging.  
## 2.2 Helper Methods
Both 
```BrowserConfig```python
 and 
```CrawlerRunConfig```python
 provide a 
```clone()```python
 method to create modified copies:
```````python
# Create a base configuration
base_config = CrawlerRunConfig(
  cache_mode=CacheMode.ENABLED,
  word_count_threshold=200
)
# Create variations using clone()
stream_config = base_config.clone(stream=True)
no_cache_config = base_config.clone(
  cache_mode=CacheMode.BYPASS,
  stream=True
)

```````python

The 
```clone()```python
 method is particularly useful when you need slightly different configurations for different use cases, without modifying the original config.
## 2.3 Example Usage
```````python
import asyncio
from crawl4ai import AsyncWebCrawler, BrowserConfig, CrawlerRunConfig, CacheMode, RateLimitConfig
async def main():
  # Configure the browser
  browser_cfg = BrowserConfig(
    headless=False,
    viewport_width=1280,
    viewport_height=720,
    proxy="http://user:pass@myproxy:8080",
    text_mode=True
  )
  # Configure the run
  run_cfg = CrawlerRunConfig(
    cache_mode=CacheMode.BYPASS,
    session_id="my_session",
    css_selector="main.article",
    excluded_tags=["script", "style"],
    exclude_external_links=True,
    wait_for="css:.article-loaded",
    screenshot=True,
    enable_rate_limiting=True,
    rate_limit_config=RateLimitConfig(
      base_delay=(1.0, 3.0),
      max_delay=60.0,
      max_retries=3,
      rate_limit_codes=[429, 503]
    ),
    memory_threshold_percent=70.0,
    check_interval=1.0,
    max_session_permit=20,
    display_mode="DETAILED",
    stream=True
  )
  async with AsyncWebCrawler(config=browser_cfg) as crawler:
    result = await crawler.arun(
      url="https://example.com/news",
      config=run_cfg
    )
    if result.success:
      print("Final cleaned_html length:", len(result.cleaned_html))
      if result.screenshot:
        print("Screenshot captured (base64, length):", len(result.screenshot))
    else:
      print("Crawl failed:", result.error_message)
if __name__ == "__main__":
  asyncio.run(main())
## 2.4 Compliance & Ethics
| **Parameter**     | **Type / Default**   | **What It Does**                                                  |
|-----------------------|-------------------------|----------------------------------------------------------------------------------------------------------------------|
| **
```check_robots_txt```python
**| 
```bool```python
 (False)     | When True, checks and respects robots.txt rules before crawling. Uses efficient caching with SQLite backend.     |
| **
```user_agent```python
**   | 
```str```python
 (None)      | User agent string to identify your crawler. Used for robots.txt checking when enabled.                |
```````python
python
run_config = CrawlerRunConfig(
  check_robots_txt=True, # Enable robots.txt compliance
  user_agent="MyBot/1.0" # Identify your crawler
)

```````python

## 3. Putting It All Together
  * **Use** 
```BrowserConfig```python
 for **global** browser settings: engine, headless, proxy, user agent. 
  * **Use** 
```CrawlerRunConfig```python
 for each crawl’s **context** : how to filter content, handle caching, wait for dynamic elements, or run JS. 
  * **Pass** both configs to 
```AsyncWebCrawler```python
 (the 
```BrowserConfig```python
) and then to 
```arun()```python
 (the 
```CrawlerRunConfig```python
). 

```````python
# Create a modified copy with the clone() method
stream_cfg = run_cfg.clone(
  stream=True,
  cache_mode=CacheMode.BYPASS
)

`````
##### Search
xClose
Type to start searching
