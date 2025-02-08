# WebSum - Documentation Web Scraper

A powerful Python tool for scraping and processing documentation websites, converting them into well-formatted Markdown files with proper code formatting and structure.

## Table of Contents
- [Installation](#installation)
- [Quick Start](#quick-start)
- [Features](#features)
- [Detailed Usage Guide](#detailed-usage-guide)
  - [Basic Usage](#basic-usage)
  - [Single Page Mode](#single-page-mode)
  - [Multi-Page Crawling](#multi-page-crawling)
  - [Output Formats](#output-formats)
  - [Cache Management](#cache-management)
- [Configuration Options](#configuration-options)
- [Examples](#examples)
- [Troubleshooting](#troubleshooting)
- [Best Practices](#best-practices)

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/websum.git
cd websum
```

2. Install dependencies:
```bash
pip install crawl4ai
playwright install  # Required for browser automation
```

## Quick Start

Basic usage to scrape a single documentation page:
```bash
python websum.py https://docs.example.com/page --output-dir ./docs
```

## Features

- **Smart Web Crawling**: Automatically follows documentation links while respecting site structure
- **Markdown Conversion**: Converts HTML content to clean, readable Markdown
- **Code Block Formatting**: Automatically detects and formats code blocks with proper syntax highlighting
- **Structured Output**: Organizes content into a logical directory structure
- **Metadata Extraction**: Captures titles, categories, and other relevant metadata
- **URL Caching**: Prevents duplicate processing of pages
- **Rate Limiting**: Prevents overwhelming target servers
- **Test Mode**: Single-page testing capability

## Detailed Usage Guide

### Basic Usage

The simplest way to use WebSum is to provide a URL and an output directory:

```bash
python websum.py https://docs.example.com/start --output-dir ./output
```

This will:
1. Scrape the specified page
2. Convert it to Markdown
3. Save it in the output directory with proper formatting

### Single Page Mode

To process just one page without following any links, use the `--test` flag:

```bash
python websum.py https://docs.example.com/page --output-dir ./output --test
```

This is useful for:
- Testing the scraper on a single page
- Extracting specific pages without crawling the entire site
- Debugging extraction issues

### Multi-Page Crawling

By default, WebSum will crawl linked pages up to the specified limit:

```bash
# Crawl up to 10 pages
python websum.py https://docs.example.com/start --output-dir ./output --limit 10

# Crawl without limit
python websum.py https://docs.example.com/start --output-dir ./output --limit 0
```

The crawler will:
- Follow links that appear to be documentation pages
- Skip navigation and boilerplate content
- Respect rate limits to avoid overwhelming servers
- Cache processed URLs to avoid duplicates

### Output Formats

#### Standard Format
```bash
python websum.py https://docs.example.com/page --output-dir ./output
```
Creates:
- `{title}.md`: Main content in Markdown format
- `{title}.json`: Metadata and additional information

#### Condensed Format
```bash
python websum.py https://docs.example.com/page --output-dir ./output --format condensed
```
Creates a more concise output focusing on key information.

### Cache Management

WebSum maintains a cache of processed URLs to prevent duplicate processing:

```bash
# Clear the cache
rm url_cache.json

# Merge caches from different runs
python websum.py --merge-cache other_cache.json
```

## Configuration Options

All available command-line options:

```bash
python websum.py [URL] [OPTIONS]

Options:
  --output-dir DIR    Directory to save output files (default: ./output)
  --test             Process single page without following links
  --limit N          Maximum number of pages to process (0 for unlimited)
  --format TYPE      Output format: standard or condensed
  --cache FILE       Specify custom cache file location
  --no-cache         Disable URL caching
  --rate-limit N     Seconds between requests (default: 1.0)
```

## Examples

### 1. Basic Documentation Scraping
```bash
# Scrape Python documentation
python websum.py https://docs.python.org/3/library/asyncio.html --output-dir ./python_docs
```

### 2. Technical Documentation with Code Examples
```bash
# Scrape with code block formatting
python websum.py https://docs.crawl4ai.com/core/docker-deploymeny/ --output-dir ./tech_docs
```

### 3. Multi-Page Tutorial Series
```bash
# Crawl entire tutorial section with limit
python websum.py https://tutorial.example.com/start --output-dir ./tutorial --limit 20
```

### 4. API Documentation
```bash
# Scrape API docs with condensed format
python websum.py https://api.example.com/docs --output-dir ./api_docs --format condensed
```

## Troubleshooting

### Common Issues

1. **NameError or ImportError**
   ```bash
   pip install -r requirements.txt
   playwright install
   ```

2. **Rate Limiting Errors**
   ```bash
   # Increase delay between requests
   python websum.py URL --rate-limit 2.0
   ```

3. **Memory Issues with Large Sites**
   ```bash
   # Limit the number of pages
   python websum.py URL --limit 50
   ```

### Debug Mode
```bash
# Enable verbose logging
python -u websum.py URL --output-dir ./output
```

## Best Practices

1. **Start Small**
   - Use `--test` flag for initial testing
   - Process a few pages before large crawls
   - Check output quality before bulk processing

2. **Respect Servers**
   - Use reasonable rate limits
   - Don't crawl entire sites unnecessarily
   - Check robots.txt compliance

3. **Organize Output**
   - Use descriptive output directories
   - Keep separate directories for different sources
   - Regular cache cleanup

4. **Maintenance**
   - Update dependencies regularly
   - Clear cache periodically
   - Monitor disk space usage

## Output Structure

```
output/
├── page_title/
│   ├── content.md       # Main content
│   ├── metadata.json    # Page metadata
│   └── assets/          # Images and resources
├── another_page/
│   └── ...
└── url_cache.json       # URL processing cache
```

Each processed page will have:
- Clean, formatted Markdown content
- Properly formatted code blocks
- Extracted metadata
- Preserved structure and hierarchy
- Cached URL information

---

For more information or to report issues, please visit the [GitHub repository](https://github.com/yourusername/websum).
