# WebSum - Documentation Web Scraper

A powerful Python tool for scraping and processing documentation websites, converting them into well-formatted Markdown files with proper code formatting and structure. WebSum is designed to help developers and technical writers maintain local copies of documentation while preserving readability and structure.

## Table of Contents
- [Installation](#installation)
- [Quick Start](#quick-start)
- [Features](#features)
- [Project Structure](#project-structure)
- [Development Guide](#development-guide)
- [Configuration](#configuration)
- [Detailed Usage Guide](#detailed-usage-guide)
- [Contributing](#contributing)
- [Troubleshooting](#troubleshooting)

## Installation

1. Ensure you have Python 3.8+ installed. You can check your version:
```bash
python --version
```

2. Clone the repository:
```bash
git clone https://github.com/gevans3000/websum.git
cd websum
```

3. Create a virtual environment (recommended):
```bash
# Windows
python -m venv venv
.\venv\Scripts\activate

# Linux/Mac
python -m venv venv
source venv/bin/activate
```

4. Install dependencies:
```bash
pip install -r requirements.txt
```

5. Install browser requirements (one-time setup):
```bash
python -m playwright install chromium
```

## Quick Start

Basic usage to scrape a single documentation page:
```bash
python websum.py https://docs.example.com/page --output-dir ./docs
```

For multiple pages with custom configuration:
```bash
python websum.py https://docs.example.com/page1 https://docs.example.com/page2 \
  --output-dir ./docs \
  --format condensed \
  --page-limit 10
```

## Features

- **Intelligent Crawling**: 
  - Smart link following based on documentation structure
  - Respects rate limits and robots.txt
  - Handles dynamic content and JavaScript-rendered pages
  - Caches processed URLs to prevent duplicates

- **Content Processing**:
  - Converts HTML to clean, semantic Markdown
  - Preserves document structure and hierarchy
  - Intelligent code block formatting with language detection
  - Maintains tables and lists formatting
  - Extracts metadata and categories

- **Performance Optimized**:
  - Streaming processing for large pages
  - Configurable memory management
  - Efficient caching system
  - Rate limiting to prevent server overload

- **Developer Friendly**:
  - Clear, documented code structure
  - Configurable via YAML
  - Extensive error handling and logging
  - Comprehensive test suite

- **Optional Features**:
  - Media export (screenshots and PDFs)
  - Content filtering and cleaning
  - URL caching for faster reruns
  - Debug mode with enhanced logging
  - Resume support for interrupted crawls

## Project Structure

The project follows a modular structure for better organization and maintainability:

```
websum/
├── tests/                  # Test suite
│   ├── unit/              # Unit tests for individual components
│   ├── conftest.py        # Pytest configuration and fixtures
│   └── README.md          # Testing documentation
├── config.yaml            # Main configuration file
├── requirements.txt       # Python package dependencies
├── websum.py             # Main entry point and core logic
└── README.md             # Project documentation
```

### Key Components

- **websum.py**: Core functionality including:
  - URL crawling and content extraction
  - Markdown processing and formatting
  - Error handling and logging
  - Code block language detection
  - Content cleaning and normalization

- **tests/**: Comprehensive test suite:
  - Unit tests for core functions
  - Integration tests for end-to-end flows
  - Test fixtures and utilities
  - Testing documentation

## Development Guide

### Setting Up Development Environment

1. Fork and clone the repository
2. Create a virtual environment and install dependencies
3. Install development dependencies:
```bash
pip install -r requirements-dev.txt  # Includes testing packages
```

### Running Tests

Run the full test suite:
```bash
python -m pytest
```

Run specific test files:
```bash
python -m pytest tests/unit/test_markdown.py
```

Run with coverage:
```bash
python -m pytest --cov=websum tests/
```

### Code Style

- Follow PEP 8 guidelines
- Use meaningful variable names
- Add docstrings for functions and classes
- Keep functions focused and modular
- Add comments for complex logic

### Making Changes

1. Create a new branch for your changes
2. Write tests for new functionality
3. Ensure all tests pass
4. Update documentation as needed
5. Submit a pull request

## Configuration

The `config.yaml` file controls various aspects of the scraper:

```yaml
# Output settings
output:
  dir: "./output"           # Base directory for all output
  cache_file: "url_cache.json"  # Tracks processed URLs

# Crawling settings
crawler:
  max_buffer_size: 1000000  # Memory buffer size (1MB)
  chunk_size: 524288        # Streaming chunk size (512KB)
  stream_mode: true         # Enable streaming for large pages
  page_limit: null          # Max pages (null = unlimited)

# Content processing
content:
  word_count_threshold: 10  # Min words per content block
  exclude_navigation: true  # Skip navigation elements
  clean_markdown: true      # Clean up markdown output
  process_code_blocks: true # Format code with syntax

# Rate limiting
rate_limit:
  delay_seconds: 1.0        # Delay between requests
  max_retries: 3           # Failed request retries
  backoff_factor: 2.0      # Exponential backoff multiplier
```

## Detailed Usage Guide

### Basic Usage

1. **Single Page Processing**:
   ```bash
   python websum.py https://docs.example.com/page
   ```

2. **Multiple Pages**:
   ```bash
   python websum.py https://docs.example.com/page1 https://docs.example.com/page2
   ```

3. **Custom Output Directory**:
   ```bash
   python websum.py https://docs.example.com/page --output-dir ./custom_docs
   ```

### Output Format Options

Choose between standard or condensed output:
```bash
# Standard format (default) - detailed output with metadata
python websum.py URL --format standard

# Condensed format - markdown only, no metadata
python websum.py URL --format condensed
```

### Optional Features

1. **Media Export**
```bash
# Export PDF along with markdown
python websum.py URL --media pdf

# Capture screenshots of pages
python websum.py URL --media screenshots

# Export both PDF and screenshots
python websum.py URL --media all
```

2. **Content Filtering**
```bash
# Set minimum word count for content blocks
python websum.py URL --filter "min_words=20"

# Exclude specific HTML tags
python websum.py URL --filter "exclude_tags=nav,footer"

# Combine multiple filters
python websum.py URL --filter "min_words=20,exclude_tags=nav,footer"
```

3. **Caching**
```bash
# Enable caching for faster reruns
python websum.py URL --cache enable

# Clear existing cache
python websum.py URL --cache clear

# Set custom cache location
python websum.py URL --cache enable --cache-dir ./custom_cache
```

4. **Debug Mode**
```bash
# Enable detailed logging
python websum.py URL --debug

# Specify log file location
python websum.py URL --debug --log-file ./debug.log
```

5. **Resume Support**
```bash
# Enable auto-save of progress
python websum.py URL --resume enable

# Resume from last saved state
python websum.py URL --resume continue

# Clear saved state and start fresh
python websum.py URL --resume clear
```

### Combining Options

You can combine multiple options:
```bash
python websum.py URL \
  --format condensed \
  --media pdf \
  --filter "min_words=20,exclude_tags=nav" \
  --cache enable \
  --resume enable
```

## Contributing

We welcome contributions! Here's how you can help:

1. **Report Issues**
   - Use the GitHub issue tracker
   - Include detailed steps to reproduce
   - Attach relevant logs and configuration

2. **Submit Pull Requests**
   - Fork the repository
   - Create a feature branch
   - Add tests for new functionality
   - Update documentation
   - Submit a pull request

3. **Improve Documentation**
   - Fix typos or unclear instructions
   - Add examples and use cases
   - Update API documentation

## Troubleshooting

### Common Issues

1. **Browser Installation**:
   - Error: "Browser not found"
   - Solution: Run `python -m playwright install chromium`
   - Note: May need admin privileges on some systems

2. **Memory Usage**:
   - Issue: High memory consumption
   - Solution: Adjust `max_buffer_size` in config.yaml
   - Tip: Start with smaller values and increase as needed

3. **Rate Limiting**:
   - Issue: Server blocking requests
   - Solution: Increase `delay_seconds` in config.yaml
   - Tip: Check the site's robots.txt for guidance

4. **Test Failures**:
   - Issue: Pytest errors or failures
   - Solution: Ensure all dependencies are installed
   - Tip: Check Python version compatibility

### Getting Help

- Check the [issues page](https://github.com/yourusername/websum/issues)
- Review the configuration guide above
- Ensure all dependencies are installed correctly
- Check the logs for detailed error messages
- Join our community discussions

### Debug Mode

Enable debug logging for more detailed output:
```bash
python websum.py https://docs.example.com/page --debug
```

This will show:
- Detailed error messages
- Request/response information
- Processing steps
- Memory usage statistics
