# Overview - Crawl4AI Documentation (v0.4.3bx)

## 📚 Document Metadata

```yaml
title: Overview - Crawl4AI Documentation (v0.4.3bx)
source_url: https://docs.crawl4ai.com/advanced/advanced-features
category: python/advanced
keywords: python, web scraping, advanced, proxy, ssl, authentication
last_modified: Unknown
type: Technical Documentation
```

## 📋 Quick Summary

Advanced features and capabilities of Crawl4AI including proxy, SSL, and authentication

## 🔧 Technical Context

### Key Technical Terms
- `
import os, asyncio
from base64 import b64decode
from crawl4ai import AsyncWebCrawler, CacheMode
async def main():
  async with AsyncWebCrawler() as crawler:
    result = await crawler.arun(
      url="https://en.wikipedia.org/wiki/List_of_common_misconceptions",
      cache_mode=CacheMode.BYPASS,
      pdf=True,
      screenshot=True
    )
    if result.success:
      # Save screenshot
      if result.screenshot:
        with open("wikipedia_screenshot.png", "wb") as f:
          f.write(b64decode(result.screenshot))
      # Save PDF
      if result.pdf:
        with open("wikipedia_page.pdf", "wb") as f:
          f.write(result.pdf)
      print("[OK] PDF & screenshot captured.")
    else:
      print("[ERROR]", result.error_message)
if __name__ == "__main__":
  asyncio.run(main())

`
- storage_dict
- `
`
- HTTP
- wikipedia_page
- `

### 5.2 Exporting & Reusing State
You can sign in once, export the browser context, and reuse it later—without re-entering credentials.
  * **`
- `**: Creates a screenshot (base64-encoded in`
- `**: Exports cookies, localStorage, etc. to a file.
  * Provide `
- ` includes methods (`
- `/`
- `BrowserConfig.proxy_config`
- ` and optional auth credentials. - Many commercial proxies provide an HTTP/HTTPS “gateway” server that you specify in `
- AsyncWebCrawler
- `**expects a dict with`
- `, `
- crawler_cfg
- status_code
- valid_until
- `
import asyncio
from crawl4ai import AsyncWebCrawler, CrawlerRunConfig
async def main():
  # Enable robots.txt checking in config
  config = CrawlerRunConfig(
    check_robots_txt=True # Will check and respect robots.txt rules
  )
  async with AsyncWebCrawler() as crawler:
    result = await crawler.arun(
      "https://example.com",
      config=config
    )
    if not result.success and result.status_code == 403:
      print("Access denied by robots.txt")
if __name__ == "__main__":
  asyncio.run(main())

`
- CrawlerRunConfig
- to_der
- to_json
- `**: Exports the current page as a PDF (base64-encoded in`
- proxy_config
- exist_ok
- `). - If you need advanced user-agent randomization or client hints, see [Identity-Based Crawling (Anti-Bot)](https://docs.crawl4ai.com/advanced/<../identity-based-crawling/>) or use `
- ` - Cache has a default TTL of 7 days - If robots.txt can't be fetched, crawling is allowed - Returns 403 status code if URL is disallowed
## Putting It All Together
Here’s a snippet that combines multiple “advanced” features (proxy, PDF, screenshot, SSL, custom headers, and session reuse) into one run. Normally, you’d tailor each setting to your project’s needs.
`
- my_auth_token
- `
import asyncio
from crawl4ai import AsyncWebCrawler
async def main():
  # Option 1: Set headers at the crawler strategy level
  crawler1 = AsyncWebCrawler(
    # The underlying strategy can accept headers in its constructor
    crawler_strategy=None # We'll override below for clarity
  )
  crawler1.crawler_strategy.update_user_agent("MyCustomUA/1.0")
  crawler1.crawler_strategy.set_custom_headers({
    "Accept-Language": "fr-FR,fr;q=0.9"
  })
  result1 = await crawler1.arun("https://www.example.com")
  print("Example 1 result success:", result1.success)
  # Option 2: Pass headers directly to `
- check_robots_txt
- JSON
- `
import os, asyncio
from base64 import b64decode
from crawl4ai import AsyncWebCrawler, BrowserConfig, CrawlerRunConfig, CacheMode
async def main():
  # 1. Browser config with proxy + headless
  browser_cfg = BrowserConfig(
    proxy_config={
      "server": "http://proxy.example.com:8080",
      "username": "myuser",
      "password": "mypass",
    },
    headless=True,
  )
  # 2. Crawler config with PDF, screenshot, SSL, custom headers, and ignoring caches
  crawler_cfg = CrawlerRunConfig(
    pdf=True,
    screenshot=True,
    fetch_ssl_certificate=True,
    cache_mode=CacheMode.BYPASS,
    headers={"Accept-Language": "en-US,en;q=0.8"},
    storage_state="my_storage.json", # Reuse session from a previous sign-in
    verbose=True,
  )
  # 3. Crawl
  async with AsyncWebCrawler(config=browser_cfg) as crawler:
    result = await crawler.arun(
      url = "https://secure.example.com/protected", 
      config=crawler_cfg
    )
    if result.success:
      print("[OK] Crawled the secure page. Links found:", len(result.links.get("internal", [])))
      # Save PDF & screenshot
      if result.pdf:
        with open("result.pdf", "wb") as f:
          f.write(b64decode(result.pdf))
      if result.screenshot:
        with open("result.png", "wb") as f:
          f.write(b64decode(result.screenshot))
      # Check SSL cert
      if result.ssl_certificate:
        print("SSL Issuer CN:", result.ssl_certificate.issuer.get("CN", ""))
    else:
      print("[ERROR]", result.error_message)
if __name__ == "__main__":
  asyncio.run(main())

`
- ` on subsequent runs to skip the login step.


**See** : [Detailed session management tutorial](https://docs.crawl4ai.com/advanced/<../session-management/>) or [Explanations → Browser Context & Managed Browser](https://docs.crawl4ai.com/advanced/<../identity-based-crawling/>) for more advanced scenarios (like multi-step logins, or capturing after interactive pages).
## 6. Robots.txt Compliance
Crawl4AI supports respecting robots.txt rules with efficient caching:
`
- `

**Why PDF + Screenshot?** - Large or complex pages can be slow or error-prone with “traditional” full-page screenshots. - Exporting a PDF is more reliable for very long pages. Crawl4AI automatically converts the first PDF page into an image if you request both. 
**Relevant Parameters** - **`
- `. - If your proxy doesn’t need auth, omit `
- ssl_certificate
- set_custom_headers
- `). - **`
- URL
- `

**Key Points** - Robots.txt files are cached locally for efficiency - Cache is stored in `
- `) for saving in various formats (handy for server config, Java keystores, etc.).
## 4. Custom Headers
Sometimes you need to set custom headers (e.g., language preferences, authentication tokens, or specialized user-agent strings). You can do this in multiple ways:
`
- `

**Key Points** - **`
- CacheMode
- `.
## 5. Session Persistence & Local Storage
Crawl4AI can preserve cookies and localStorage so you can continue where you left off—ideal for logging into sites or skipping repeated auth flows.
### 5.1 `
- to_pem
- `.
## 2. Capturing PDFs & Screenshots
Sometimes you need a visual record of a page or a PDF “printout.” Crawl4AI can do both in one pass:
`
- tmp_dir
- my_storage
- BrowserConfig
- `**or advanced hooking can further refine how the crawler captures content.
## 3. Handling SSL Certificates
If you need to verify or export a site’s SSL certificate—for compliance, debugging, or data analysis—Crawl4AI can fetch it during the crawl:
`
- `
import asyncio, os
from crawl4ai import AsyncWebCrawler, CrawlerRunConfig, CacheMode
async def main():
  tmp_dir = os.path.join(os.getcwd(), "tmp")
  os.makedirs(tmp_dir, exist_ok=True)
  config = CrawlerRunConfig(
    fetch_ssl_certificate=True,
    cache_mode=CacheMode.BYPASS
  )
  async with AsyncWebCrawler() as crawler:
    result = await crawler.arun(url="https://example.com", config=config)
    if result.success and result.ssl_certificate:
      cert = result.ssl_certificate
      print("\nCertificate Information:")
      print(f"Issuer (CN): {cert.issuer.get('CN', '')}")
      print(f"Valid until: {cert.valid_until}")
      print(f"Fingerprint: {cert.fingerprint}")
      # Export in multiple formats:
      cert.to_json(os.path.join(tmp_dir, "certificate.json"))
      cert.to_pem(os.path.join(tmp_dir, "certificate.pem"))
      cert.to_der(os.path.join(tmp_dir, "certificate.der"))
      print("\nCertificate exported to JSON/PEM/DER in 'tmp' folder.")
    else:
      print("[ERROR] No certificate or crawl failed.")
if __name__ == "__main__":
  asyncio.run(main())

`
- `
import asyncio
from crawl4ai import AsyncWebCrawler
async def main():
  storage_dict = {
    "cookies": [
      {
        "name": "session",
        "value": "abcd1234",
        "domain": "example.com",
        "path": "/",
        "expires": 1699999999.0,
        "httpOnly": False,
        "secure": False,
        "sameSite": "None"
      }
    ],
    "origins": [
      {
        "origin": "https://example.com",
        "localStorage": [
          {"name": "token", "value": "my_auth_token"}
        ]
      }
    ]
  }
  # Provide the storage state as a dictionary to start "already logged in"
  async with AsyncWebCrawler(
    headless=True,
    storage_state=storage_dict
  ) as crawler:
    result = await crawler.arun("https://example.com/protected")
    if result.success:
      print("Protected page content length:", len(result.html))
    else:
      print("Failed to crawl protected page")
if __name__ == "__main__":
  asyncio.run(main())

`
- `

**Notes** - Some sites may react differently to certain headers (e.g., `
- scan_full_page
- update_user_agent
- `**triggers certificate retrieval. -`
- wikipedia_screenshot
- fetch_ssl_certificate
- robots_cache
- error_message
- browser_cfg
- HTML
- UserAgentGenerator
- cache_mode
- crawler_strategy
- storage_state
- `
import asyncio
from crawl4ai import AsyncWebCrawler, BrowserConfig, CrawlerRunConfig
async def main():
  browser_cfg = BrowserConfig(
    proxy_config={
      "server": "http://proxy.example.com:8080",
      "username": "myuser",
      "password": "mypass",
    },
    headless=True
  )
  crawler_cfg = CrawlerRunConfig(
    verbose=True
  )
  async with AsyncWebCrawler(config=browser_cfg) as crawler:
    result = await crawler.arun(
      url="https://www.whatismyip.com/",
      config=crawler_cfg
    )
    if result.success:
      print("[OK] Page fetched via proxy.")
      print("Page HTML snippet:", result.html[:200])
    else:
      print("[ERROR]", result.error_message)
if __name__ == "__main__":
  asyncio.run(main())

`
- `
  crawler2 = AsyncWebCrawler()
  result2 = await crawler2.arun(
    url="https://www.example.com",
    headers={"Accept-Language": "es-ES,es;q=0.9"}
  )
  print("Example 2 result success:", result2.success)
if __name__ == "__main__":
  asyncio.run(main())

`

## 📖 Main Content

### Overview of Some Important Advanced Features

(Proxy, PDF, Screenshot, SSL, Headers, & Storage State)
Crawl4AI offers multiple power-user features that go beyond simple crawling. This tutorial covers:

🔍 Instructions:

• ❗ Important: Proxy Usage 2. ❗ Important: Capturing PDFs & Screenshots 3. ❗ Important: Handling SSL Certificates 4. ❗ Important: Custom Headers 5. ❗ Important: Session Persistence & Local Storage 6. ❗ Important: Robots.txt Compliance

> ❗ Important: Prerequisites - You have a basic grasp of [AsyncWebCrawler Basics](https://docs.crawl4ai.com/advanced/core/simple-crawling/>) - You know how to run or configure your Python environment with Playwright installed

#### 1. Proxy Usage

If you need to route your crawl traffic through a proxy—whether for IP rotation, geo-testing, or privacy—Crawl4AI supports it via `BrowserConfig.proxy_config`.

Code Example (text):
```text
import asyncio
from crawl4ai import AsyncWebCrawler, BrowserConfig, CrawlerRunConfig
async def main():
  browser_cfg = BrowserConfig(
    proxy_config={
      "server": "http://proxy.example.com:8080",
      "username": "myuser",
      "password": "mypass",
    },
    headless=True
  )
  crawler_cfg = CrawlerRunConfig(
    verbose=True
  )
  async with AsyncWebCrawler(config=browser_cfg) as crawler:
    result = await crawler.arun(
      url="https://www.whatismyip.com/",
      config=crawler_cfg
    )
    if result.success:
      print("[OK] Page fetched via proxy.")
      print("Page HTML snippet:", result.html[:200])
    else:
      print("[ERROR]", result.error_message)
if __name__ == "__main__":
  asyncio.run(main())
```



❗ Important: Key Points - ❗ Important: `proxy_config`expects a dict with`server` and optional auth credentials. - Many commercial proxies provide an HTTP/HTTPS “gateway” server that you specify in `server`. - If your proxy doesn’t need auth, omit `username`/`password`.

#### 2. Capturing PDFs & Screenshots

Sometimes you need a visual record of a page or a PDF “printout.” Crawl4AI can do both in one pass:

Code Example (text):
```text
import os, asyncio
from base64 import b64decode
from crawl4ai import AsyncWebCrawler, CacheMode
async def main():
  async with AsyncWebCrawler() as crawler:
    result = await crawler.arun(
      url="https://en.wikipedia.org/wiki/List_of_common_misconceptions",
      cache_mode=CacheMode.BYPASS,
      pdf=True,
      screenshot=True
    )
    if result.success:
      # Save screenshot
      if result.screenshot:
        with open("wikipedia_screenshot.png", "wb") as f:
          f.write(b64decode(result.screenshot))
      # Save PDF
      if result.pdf:
        with open("wikipedia_page.pdf", "wb") as f:
          f.write(result.pdf)
      print("[OK] PDF & screenshot captured.")
    else:
      print("[ERROR]", result.error_message)
if __name__ == "__main__":
  asyncio.run(main())
```



❗ Important: Why PDF + Screenshot? - Large or complex pages can be slow or error-prone with “traditional” full-page screenshots. - Exporting a PDF is more reliable for very long pages. Crawl4AI automatically converts the first PDF page into an image if you request both. 
❗ Important: Relevant Parameters - ❗ Important: `pdf=True`: Exports the current page as a PDF (base64-encoded in`result.pdf`). - ❗ Important: `screenshot=True`: Creates a screenshot (base64-encoded in`result.screenshot`). - ❗ Important: `scan_full_page`or advanced hooking can further refine how the crawler captures content.

#### 3. Handling SSL Certificates

If you need to verify or export a site’s SSL certificate—for compliance, debugging, or data analysis—Crawl4AI can fetch it during the crawl:

Code Example (text):
```text
import asyncio, os
from crawl4ai import AsyncWebCrawler, CrawlerRunConfig, CacheMode
async def main():
  tmp_dir = os.path.join(os.getcwd(), "tmp")
  os.makedirs(tmp_dir, exist_ok=True)
  config = CrawlerRunConfig(
    fetch_ssl_certificate=True,
    cache_mode=CacheMode.BYPASS
  )
  async with AsyncWebCrawler() as crawler:
    result = await crawler.arun(url="https://example.com", config=config)
    if result.success and result.ssl_certificate:
      cert = result.ssl_certificate
      print("\nCertificate Information:")
      print(f"Issuer (CN): {cert.issuer.get('CN', '')}")
      print(f"Valid until: {cert.valid_until}")
      print(f"Fingerprint: {cert.fingerprint}")
      # Export in multiple formats:
      cert.to_json(os.path.join(tmp_dir, "certificate.json"))
      cert.to_pem(os.path.join(tmp_dir, "certificate.pem"))
      cert.to_der(os.path.join(tmp_dir, "certificate.der"))
      print("\nCertificate exported to JSON/PEM/DER in 'tmp' folder.")
    else:
      print("[ERROR] No certificate or crawl failed.")
if __name__ == "__main__":
  asyncio.run(main())
```



❗ Important: Key Points - ❗ Important: `fetch_ssl_certificate=True`triggers certificate retrieval. -`result.ssl_certificate` includes methods (`to_json`, `to_pem`, `to_der`) for saving in various formats (handy for server config, Java keystores, etc.).

#### 4. Custom Headers

Sometimes you need to set custom headers (e.g., language preferences, authentication tokens, or specialized user-agent strings). You can do this in multiple ways:

Code Example (text):
```text
import asyncio
from crawl4ai import AsyncWebCrawler
async def main():
  # Option 1: Set headers at the crawler strategy level
  crawler1 = AsyncWebCrawler(
    # The underlying strategy can accept headers in its constructor
    crawler_strategy=None # We'll override below for clarity
  )
  crawler1.crawler_strategy.update_user_agent("MyCustomUA/1.0")
  crawler1.crawler_strategy.set_custom_headers({
    "Accept-Language": "fr-FR,fr;q=0.9"
  })
  result1 = await crawler1.arun("https://www.example.com")
  print("Example 1 result success:", result1.success)
  # Option 2: Pass headers directly to `arun()`
  crawler2 = AsyncWebCrawler()
  result2 = await crawler2.arun(
    url="https://www.example.com",
    headers={"Accept-Language": "es-ES,es;q=0.9"}
  )
  print("Example 2 result success:", result2.success)
if __name__ == "__main__":
  asyncio.run(main())
```



❗ Important: Notes - Some sites may react differently to certain headers (e.g., `Accept-Language`). - If you need advanced user-agent randomization or client hints, see [Identity-Based Crawling (Anti-Bot)](https://docs.crawl4ai.com/advanced/<../identity-based-crawling/>) or use `UserAgentGenerator`.

#### 5. Session Persistence & Local Storage

Crawl4AI can preserve cookies and localStorage so you can continue where you left off—ideal for logging into sites or skipping repeated auth flows.

##### 5.1 `storage_state`


Code Example (text):
```text
import asyncio
from crawl4ai import AsyncWebCrawler
async def main():
  storage_dict = {
    "cookies": [
      {
        "name": "session",
        "value": "abcd1234",
        "domain": "example.com",
        "path": "/",
        "expires": 1699999999.0,
        "httpOnly": False,
        "secure": False,
        "sameSite": "None"
      }
    ],
    "origins": [
      {
        "origin": "https://example.com",
        "localStorage": [
          {"name": "token", "value": "my_auth_token"}
        ]
      }
    ]
  }
  # Provide the storage state as a dictionary to start "already logged in"
  async with AsyncWebCrawler(
    headless=True,
    storage_state=storage_dict
  ) as crawler:
    result = await crawler.arun("https://example.com/protected")
    if result.success:
      print("Protected page content length:", len(result.html))
    else:
      print("Failed to crawl protected page")
if __name__ == "__main__":
  asyncio.run(main())
```




##### 5.2 Exporting & Reusing State

You can sign in once, export the browser context, and reuse it later—without re-entering credentials.

🔍 Instructions:

• ❗ Important: `await context.storage_state(path="my_storage.json")`: Exports cookies, localStorage, etc. to a file.
• Provide `storage_state="my_storage.json"` on subsequent runs to skip the login step.



❗ Important: See : [Detailed session management tutorial](https://docs.crawl4ai.com/advanced/<../session-management/>) or [Explanations → Browser Context & Managed Browser](https://docs.crawl4ai.com/advanced/<../identity-based-crawling/>) for more advanced scenarios (like multi-step logins, or capturing after interactive pages).

#### 6. Robots.txt Compliance

Crawl4AI supports respecting robots.txt rules with efficient caching:

Code Example (text):
```text
import asyncio
from crawl4ai import AsyncWebCrawler, CrawlerRunConfig
async def main():
  # Enable robots.txt checking in config
  config = CrawlerRunConfig(
    check_robots_txt=True # Will check and respect robots.txt rules
  )
  async with AsyncWebCrawler() as crawler:
    result = await crawler.arun(
      "https://example.com",
      config=config
    )
    if not result.success and result.status_code == 403:
      print("Access denied by robots.txt")
if __name__ == "__main__":
  asyncio.run(main())
```



❗ Important: Key Points - Robots.txt files are cached locally for efficiency - Cache is stored in `~/.crawl4ai/robots/robots_cache.db` - Cache has a default TTL of 7 days - If robots.txt can't be fetched, crawling is allowed - Returns 403 status code if URL is disallowed

#### Putting It All Together

Here’s a snippet that combines multiple “advanced” features (proxy, PDF, screenshot, SSL, custom headers, and session reuse) into one run. Normally, you’d tailor each setting to your project’s needs.

Code Example (text):
```text
import os, asyncio
from base64 import b64decode
from crawl4ai import AsyncWebCrawler, BrowserConfig, CrawlerRunConfig, CacheMode
async def main():
  # 1. Browser config with proxy + headless
  browser_cfg = BrowserConfig(
    proxy_config={
      "server": "http://proxy.example.com:8080",
      "username": "myuser",
      "password": "mypass",
    },
    headless=True,
  )
  # 2. Crawler config with PDF, screenshot, SSL, custom headers, and ignoring caches
  crawler_cfg = CrawlerRunConfig(
    pdf=True,
    screenshot=True,
    fetch_ssl_certificate=True,
    cache_mode=CacheMode.BYPASS,
    headers={"Accept-Language": "en-US,en;q=0.8"},
    storage_state="my_storage.json", # Reuse session from a previous sign-in
    verbose=True,
  )
  # 3. Crawl
  async with AsyncWebCrawler(config=browser_cfg) as crawler:
    result = await crawler.arun(
      url = "https://secure.example.com/protected", 
      config=crawler_cfg
    )
    if result.success:
      print("[OK] Crawled the secure page. Links found:", len(result.links.get("internal", [])))
      # Save PDF & screenshot
      if result.pdf:
        with open("result.pdf", "wb") as f:
          f.write(b64decode(result.pdf))
      if result.screenshot:
        with open("result.png", "wb") as f:
          f.write(b64decode(result.screenshot))
      # Check SSL cert
      if result.ssl_certificate:
        print("SSL Issuer CN:", result.ssl_certificate.issuer.get("CN", ""))
    else:
      print("[ERROR]", result.error_message)
if __name__ == "__main__":
  asyncio.run(main())
```




#### Conclusion & Next Steps

You’ve now explored several ❗ Important: advanced features:

🔍 Instructions:

• ❗ Important: Proxy Usage
• ❗ Important: PDF & Screenshot capturing for large or critical pages 
• ❗ Important: SSL Certificate retrieval & exporting 
• ❗ Important: Custom Headers for language or specialized requests 
• ❗ Important: Session Persistence via storage state
• ❗ Important: Robots.txt Compliance



With these power tools, you can build robust scraping workflows that mimic real user behavior, handle secure sites, capture detailed snapshots, and manage sessions across multiple runs—streamlining your entire data collection pipeline.
❗ Important: Last Updated : 2025-01-01

####### Search

xClose
Type to start searching


## 🔗 Related Resources

- [https://docs.crawl4ai.com](https://docs.crawl4ai.com)
- [https://docs.crawl4ai.com/api/arun](https://docs.crawl4ai.com/api/arun)
- [https://docs.crawl4ai.com/api/arun_many](https://docs.crawl4ai.com/api/arun_many)
- [https://docs.crawl4ai.com/api/async-webcrawler](https://docs.crawl4ai.com/api/async-webcrawler)
- [https://docs.crawl4ai.com/api/crawl-result](https://docs.crawl4ai.com/api/crawl-result)
- [https://docs.crawl4ai.com/api/parameters](https://docs.crawl4ai.com/api/parameters)
- [https://docs.crawl4ai.com/api/strategies](https://docs.crawl4ai.com/api/strategies)
- [https://docs.crawl4ai.com/blog](https://docs.crawl4ai.com/blog)
- [https://docs.crawl4ai.com/core/browser-crawler-config](https://docs.crawl4ai.com/core/browser-crawler-config)
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
- [https://docs.crawl4ai.com/crawl-dispatcher](https://docs.crawl4ai.com/crawl-dispatcher)
- [https://docs.crawl4ai.com/extraction/chunking](https://docs.crawl4ai.com/extraction/chunking)
- [https://docs.crawl4ai.com/extraction/clustring-strategies](https://docs.crawl4ai.com/extraction/clustring-strategies)
- [https://docs.crawl4ai.com/extraction/llm-strategies](https://docs.crawl4ai.com/extraction/llm-strategies)
- [https://docs.crawl4ai.com/extraction/no-llm-strategies](https://docs.crawl4ai.com/extraction/no-llm-strategies)
- [https://docs.crawl4ai.com/file-downloading](https://docs.crawl4ai.com/file-downloading)
- [https://docs.crawl4ai.com/hooks-auth](https://docs.crawl4ai.com/hooks-auth)
- [https://docs.crawl4ai.com/identity-based-crawling](https://docs.crawl4ai.com/identity-based-crawling)
- [https://docs.crawl4ai.com/lazy-loading](https://docs.crawl4ai.com/lazy-loading)
- [https://docs.crawl4ai.com/multi-url-crawling](https://docs.crawl4ai.com/multi-url-crawling)
- [https://docs.crawl4ai.com/proxy-security](https://docs.crawl4ai.com/proxy-security)
- [https://docs.crawl4ai.com/session-management](https://docs.crawl4ai.com/session-management)
- [https://docs.crawl4ai.com/ssl-certificate](https://docs.crawl4ai.com/ssl-certificate)

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
