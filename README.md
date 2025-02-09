# WebSum - Documentation Web Scraper

A powerful Python tool for scraping and processing documentation websites, converting them into well-formatted Markdown files with proper code formatting and structure.

## Table of Contents
- [Installation](#installation)
- [Quick Start](#quick-start)
- [Features](#features)
- [Project Structure](#project-structure)
- [Configuration](#configuration)
- [Detailed Usage Guide](#detailed-usage-guide)
- [Troubleshooting](#troubleshooting)

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/websum.git
cd websum
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

## Quick Start

Basic usage to scrape a single documentation page:
```bash
python websum.py https://docs.example.com/page --output-dir ./docs
```

## Features

- **Modular Architecture**: Clean, organized code structure for better maintainability
- **Configuration Management**: Easy-to-modify YAML configuration file
- **Smart Web Crawling**: Automatically follows documentation links while respecting site structure
- **Markdown Conversion**: Converts HTML content to clean, readable Markdown
- **Code Block Formatting**: Automatically detects and formats code blocks with proper syntax highlighting
- **URL Caching**: Prevents duplicate processing of pages
- **Rate Limiting**: Prevents overwhelming target servers

## Project Structure

The project follows a modular structure for better organization and maintainability:

```
websum/
├── modules/                 # Core modules directory
│   ├── __init__.py         # Package initialization
│   ├── utils.py            # Utility functions
│   └── config.py           # Configuration management
├── config.yaml             # Configuration settings
├── requirements.txt        # Project dependencies
├── websum.py              # Main script
└── README.md              # Documentation
```

### Core Modules

- **utils.py**: Contains utility functions for:
  - Text cleaning and normalization
  - Markdown processing
  - URL handling
  - Code block formatting

- **config.py**: Manages configuration:
  - Loading settings from YAML
  - Providing default configurations
  - Environment variable management

## Configuration

The `config.yaml` file controls various aspects of the scraper:

```yaml
# Output settings
output:
  dir: "./output"           # Default output directory
  cache_file: "url_cache.json"  # URL cache location

# Crawling settings
crawler:
  max_buffer_size: 1000000  # 1MB buffer
  chunk_size: 524288        # 512KB chunks
  stream_mode: true
  page_limit: null          # null for no limit

# Content processing
content:
  word_count_threshold: 10
  exclude_navigation: true
  clean_markdown: true
  process_code_blocks: true

# Rate limiting
rate_limit:
  delay_seconds: 1.0
  max_retries: 3
  backoff_factor: 2.0
```

To modify settings:
1. Copy `config.yaml` to your desired location
2. Edit the values as needed
3. The script will automatically use your custom settings

## Detailed Usage Guide

### Basic Usage

```bash
# Scrape a single page
python websum.py https://docs.example.com/page --test

# Scrape with custom output directory
python websum.py https://docs.example.com/page --output-dir ./my-docs

# Scrape with custom config
python websum.py https://docs.example.com/page --config my-config.yaml
```

### Output Structure

The scraper creates a clean directory structure:
```
output/
├── domain.com/
│   ├── page1.md
│   ├── page2.md
│   └── section/
│       └── page3.md
└── url_cache.json
```

## Troubleshooting

### Common Issues

1. **Missing Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

2. **Configuration Issues**
   - Check if `config.yaml` exists in your working directory
   - Verify YAML syntax is correct
   - Try using default settings by renaming/removing `config.yaml`

3. **Rate Limiting**
   - Adjust `rate_limit.delay_seconds` in `config.yaml`
   - Increase `rate_limit.max_retries` for unstable connections

### Getting Help

If you encounter issues:
1. Check the error message for specific details
2. Verify your configuration settings
3. Try running in test mode with `--test` flag
4. Check the logs for detailed information

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.
