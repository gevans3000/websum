# WebSum Documentation Crawler

A powerful web crawler designed for extracting and processing documentation from websites. Built with Python and Crawl4AI, it provides flexible content extraction, markdown conversion, and media capture capabilities.

## 🚀 Quick Start

### Installation

1. Clone the repository:
```bash
git clone https://github.com/gevans3000/websum.git
cd websum
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

### Basic Usage

1. Simple documentation scraping:
```bash
python websum.py https://docs.example.com/page
```

2. Test mode (preview without saving):
```bash
python websum.py https://docs.example.com/page --test --debug
```

3. Capture with screenshots:
```bash
python websum.py https://docs.example.com/page --media screenshots --debug
```

## 📚 Detailed Usage Examples

### 1. Documentation Sites

#### Python Documentation
```bash
# Scrape Python tutorial with screenshots
python websum.py https://docs.python.org/3/tutorial/introduction.html \
  --media screenshots \
  --output-dir python_docs \
  --debug

# Scrape multiple pages
python websum.py \
  https://docs.python.org/3/tutorial/introduction.html \
  https://docs.python.org/3/tutorial/controlflow.html \
  --output-dir python_docs
```

#### Technical Documentation
```bash
# Crawl4AI documentation (known to work well)
python websum.py https://docs.crawl4ai.com/core/browser-crawler-config/ --debug

# MDN Web Docs
python websum.py https://developer.mozilla.org/en-US/docs/Web/JavaScript/Guide \
  --output-dir mdn_docs \
  --format condensed
```

### 2. Media Handling

#### Screenshot Capture
```bash
# High-quality screenshots
python websum.py https://docs.example.com/page \
  --media screenshots \
  --output-dir docs_with_images

# PDF generation (if supported)
python websum.py https://docs.example.com/page \
  --media pdf \
  --output-dir docs_with_pdfs
```

#### Media Download Options
```bash
# Download all media types
python websum.py https://docs.example.com/page --media all

# Selective media download (configured in config.yaml)
media:
  download_images: true
  download_pdfs: true
  download_code: true
  download_docs: true
  save_screenshots: true
  file_types:
    images: [.png, .jpg, .jpeg]
    documents: [.pdf, .doc, .docx]
    code: [.py, .js, .java]
```

### 3. Output Formatting

#### Standard Format
```bash
# Detailed output with full structure
python websum.py https://docs.example.com/page \
  --format standard \
  --output-dir full_docs
```

#### Condensed Format
```bash
# Concise output for quick reference
python websum.py https://docs.example.com/page \
  --format condensed \
  --output-dir quick_docs
```

## 🛠️ Developer Guide

### Project Structure
```
websum/
├── websum.py              # Main crawler implementation
├── config.yaml            # Configuration settings
├── modules/              # Helper modules
│   ├── utils.py         # Utility functions
│   └── config.py        # Configuration handling
├── tests/               # Test suite
└── output/              # Default output directory
```

### Key Components

1. **CrawlResult Class**
   - Stores crawl results and metadata
   - Handles content processing
   - Example extension:
   ```python
   class CrawlResult:
       def __init__(self):
           self.url = None
           self.success = False
           self.error = None
           self.html = None
           self.markdown = None
           # Add custom fields as needed
   ```

2. **Configuration Management**
   - Uses YAML for flexible settings
   - Supports environment variables
   - Example custom config:
   ```yaml
   # Custom crawler settings
   crawler:
     custom_headers:
       User-Agent: "Your Custom User Agent"
     cookies:
       session: "your-session-cookie"
   ```

### Adding New Features

1. **New Media Type Support**
   ```python
   # In websum.py
   async def extract_media_files(result):
       # Add new media type
       if media_type == "new_type":
           # Implementation
           pass
   ```

2. **Custom Content Processing**
   ```python
   # In modules/utils.py
   def process_custom_content(content):
       # Your processing logic
       return processed_content
   ```

3. **New Command Line Options**
   ```python
   # In websum.py
   parser.add_argument('--new-option',
                      help='Description of new option')
   ```

## 🔧 Advanced Configuration

### Rate Limiting
```yaml
rate_limit:
  delay_seconds: 2.0          # Base delay between requests
  per_domain_delay: 3.0       # Domain-specific delay
  max_requests_per_minute: 20 # Rate limit
  cool_down_period: 30        # Cooling period if rate limit hit
  max_retries: 3             # Retry attempts
  backoff_factor: 2.0        # Exponential backoff multiplier
```

### Content Processing
```yaml
content:
  word_count_threshold: 50    # Minimum content length
  exclude_navigation: true    # Skip nav elements
  clean_markdown: true       # Clean output
  process_code_blocks: true  # Format code
```

### Memory Management
```yaml
crawler:
  max_buffer_size: 1000000   # 1MB buffer
  chunk_size: 524288        # 512KB chunks
  stream_mode: true         # Enable streaming
  max_concurrent: 1         # Concurrent downloads
```

## 🚨 Troubleshooting Guide

### Common Issues

1. **SSL Certificate Errors**
   ```python
   # Temporary fix in code
   import ssl
   ssl._create_default_https_context = ssl._create_unverified_context
   ```

2. **Memory Usage**
   ```yaml
   # Optimize memory in config.yaml
   crawler:
     stream_mode: true
     max_concurrent: 1
     chunk_size: 262144  # Reduce to 256KB
   ```

3. **Rate Limiting**
   ```yaml
   # Aggressive rate limiting
   rate_limit:
     delay_seconds: 5.0
     max_requests_per_minute: 10
   ```

### Debug Mode
```bash
# Full debug output
python websum.py URL --debug --test

# Save debug log
python websum.py URL --debug 2>&1 | tee debug.log
```

## 📊 Performance Optimization

### Best Practices

1. **Memory Efficiency**
   - Enable streaming for large pages
   - Limit concurrent downloads
   - Use appropriate buffer sizes

2. **Network Optimization**
   - Implement proper rate limiting
   - Use caching when possible
   - Handle timeouts gracefully

3. **Content Processing**
   - Filter unnecessary content
   - Optimize markdown generation
   - Handle media efficiently

### Example Configurations

1. **High Performance**
```yaml
crawler:
  max_concurrent: 2
  stream_mode: true
  timeout_seconds: 30
```

2. **Memory Conscious**
```yaml
crawler:
  max_concurrent: 1
  chunk_size: 262144
  max_buffer_size: 524288
```

3. **Polite Crawling**
```yaml
rate_limit:
  delay_seconds: 3.0
  per_domain_delay: 5.0
  max_requests_per_minute: 10
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

### Code Style
- Follow PEP 8 guidelines
- Use meaningful variable names
- Add docstrings for functions
- Comment complex logic

### Testing
```bash
# Run test suite
python -m pytest tests/

# Run specific test
python -m pytest tests/test_crawler.py
```

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.
