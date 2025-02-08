# arun_many()

# ```python
arun_many(...)
``` Reference
> **Note** : This function is very similar to ```python
arun()
```[](https://docs.crawl4ai.com/api/<../arun/>) but focused on **concurrent** or **batch** crawling. If you’re unfamiliar with ```python
arun()
``` usage, please read that doc first, then review this for differences.
## Function Signature
`````python
async def arun_many(
  urls: Union[List[str], List[Any]],
  config: Optional[CrawlerRunConfig] = None,
  dispatcher: Optional[BaseDispatcher] = None,
  ...
) -> Union[List[CrawlResult], AsyncGenerator[CrawlResult, None]]:
  """
  Crawl multiple URLs concurrently or in batches.
  :param urls: A list of URLs (or tasks) to crawl.
  :param config: (Optional) A default 
```CrawlerRunConfig```python
 applying to each crawl.
  :param dispatcher: (Optional) A concurrency controller (e.g. MemoryAdaptiveDispatcher).
  ...
  :return: Either a list of 
```CrawlResult```python
 objects, or an async generator if streaming is enabled.
  """

```````python

## Differences from 
```arun()```python
1. **Multiple URLs** : 
  * Instead of crawling a single URL, you pass a list of them (strings or tasks). 
  * The function returns either a **list** of 
```CrawlResult```python
 or an **async generator** if streaming is enabled.

2. **Concurrency & Dispatchers**: 
  * **
```dispatcher```python
**param allows advanced concurrency control.
  * If omitted, a default dispatcher (like 
```MemoryAdaptiveDispatcher```python
) is used internally. 
  * Dispatchers handle concurrency, rate limiting, and memory-based adaptive throttling (see [Multi-URL Crawling](https://docs.crawl4ai.com/api/advanced/multi-url-crawling/>)).

3. **Streaming Support** : 
  * Enable streaming by setting 
```stream=True```python
 in your 
```CrawlerRunConfig```python
.
  * When streaming, use 
```async for```python
 to process results as they become available.
  * Ideal for processing large numbers of URLs without waiting for all to complete.

4. **Parallel** Execution**: 
  * 
```arun_many()```python
 can run multiple requests concurrently under the hood. 
  * Each 
```CrawlResult```python
 might also include a **
```dispatch_result```python
**with concurrency details (like memory usage, start/end times).

### Basic Example (Batch Mode)
```````python
# Minimal usage: The default dispatcher will be used
results = await crawler.arun_many(
  urls=["https://site1.com", "https://site2.com"],
  config=CrawlerRunConfig(stream=False) # Default behavior
)
for res in results:
  if res.success:
    print(res.url, "crawled OK!")
  else:
    print("Failed:", res.url, "-", res.error_message)

```````python

### Streaming Example
```````python
config = CrawlerRunConfig(
  stream=True, # Enable streaming mode
  cache_mode=CacheMode.BYPASS
)
# Process results as they complete
async for result in await crawler.arun_many(
  urls=["https://site1.com", "https://site2.com", "https://site3.com"],
  config=config
):
  if result.success:
    print(f"Just completed: {result.url}")
    # Process each result immediately
    process_result(result)

```````python

### With a Custom Dispatcher
```````python
dispatcher = MemoryAdaptiveDispatcher(
  memory_threshold_percent=70.0,
  max_session_permit=10
)
results = await crawler.arun_many(
  urls=["https://site1.com", "https://site2.com", "https://site3.com"],
  config=my_run_config,
  dispatcher=dispatcher
)

```````python

**Key Points** : - Each URL is processed by the same or separate sessions, depending on the dispatcher’s strategy. - 
```dispatch_result```python
 in each 
```CrawlResult```python
 (if using concurrency) can hold memory and timing info. - If you need to handle authentication or session IDs, pass them in each individual task or within your run config.
### Return Value
Either a **list** of 
```CrawlResult```python
[](https://docs.crawl4ai.com/api/<../crawl-result/>) objects, or an **async generator** if streaming is enabled. You can iterate to check 
```result.success```python
 or read each item’s 
```extracted_content```python
, 
```markdown```python
, or 
```dispatch_result```python
.
## Dispatcher Reference
  * **
```MemoryAdaptiveDispatcher```python
**: Dynamically manages concurrency based on system memory usage.
  * **
```SemaphoreDispatcher```python
**: Fixed concurrency limit, simpler but less adaptive.

For advanced usage or custom settings, see [Multi-URL Crawling with Dispatchers](https://docs.crawl4ai.com/api/advanced/multi-url-crawling/>).
## Common Pitfalls
1. **Large Lists** : If you pass thousands of URLs, be mindful of memory or rate-limits. A dispatcher can help. 
2. **Session Reuse** : If you need specialized logins or persistent contexts, ensure your dispatcher or tasks handle sessions accordingly. 
3. **Error Handling** : Each 
```CrawlResult```python
 might fail for different reasons—always check 
```result.success```python
 or the 
```error_message```python
 before proceeding.
## Conclusion
Use 
```arun_many()```python
 when you want to **crawl multiple URLs** simultaneously or in controlled parallel tasks. If you need advanced concurrency features (like memory-based adaptive throttling or complex rate-limiting), provide a **dispatcher**. Each result is a standard 
```CrawlResult```python
, possibly augmented with concurrency stats (
```dispatch_result`) for deeper inspection. For more details on concurrency logic and dispatchers, see the [Advanced Multi-URL Crawling](https://docs.crawl4ai.com/api/advanced/multi-url-crawling/>) docs.
##### Search
xClose
Type to start searching
