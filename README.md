# WebSum - Web Documentation Summarizer

A powerful tool for crawling, summarizing, and organizing web documentation with support for screenshots and PDFs.

## Features

### Working Features
- Web page crawling and content extraction
- Markdown conversion and formatting
- Full-page screenshot capture
- PDF generation
- Link extraction and processing
- Structured output organization

### In Progress
- Advanced content summarization
- Multi-page crawling optimization
- Enhanced metadata extraction

## Quick Start

### Prerequisites
1. Install Python 3.8 or higher
2. Install required packages:
   ```bash
   pip install -r requirements.txt
   ```
3. Install Playwright browsers:
   ```bash
   playwright install
   ```

### Basic Usage

1. **Simple Page Capture**
   ```bash
   python websum.py https://example.com
   ```

2. **Capture with Screenshots**
   ```bash
   python websum.py https://example.com --media screenshots
   ```

3. **Generate PDF**
   ```bash
   python websum.py https://example.com --media pdf
   ```

4. **Capture Both Screenshot and PDF**
   ```bash
   python websum.py https://example.com --media all
   ```

### Advanced Options

- **Output Directory**: Change where files are saved
  ```bash
  python websum.py https://example.com -o custom_output
  ```

- **Page Limit**: Set maximum pages to crawl
  ```bash
  python websum.py https://example.com --page-limit 5
  ```

- **Debug Mode**: Enable detailed logging
  ```bash
  python websum.py https://example.com --debug
  ```

- **Test Mode**: Process single page only
  ```bash
  python websum.py https://example.com --test
  ```

## Output Structure

```
crawl_output/
├── media/                    # Screenshots and PDFs
│   ├── example.com.png      # Screenshot
│   └── example.com.pdf      # PDF version
├── example.com.md           # Markdown content
└── metadata.json            # Page metadata
```

## Configuration

### Media Options
- `screenshots`: Captures full-page screenshots
- `pdf`: Generates PDF documents
- `all`: Both screenshots and PDFs

### Output Formats
- `standard` (default): Detailed output with headers and sections
- `condensed`: Minimal output focusing on key content

## Tips for Best Results

1. **Media Capture**
   - Ensure enough disk space for screenshots/PDFs
   - Wait for page load completion (--debug shows progress)
   - Screenshots capture the full page by default

2. **Performance**
   - Use `--test` for initial testing
   - Enable `--debug` to monitor progress
   - Start with single pages before batch processing

3. **Common Issues**
   - If screenshots are empty, check page load time
   - For PDF issues, ensure page is fully loaded
   - Use debug mode to identify crawling problems

## Development Guide

### Project Structure
```
websum/
├── websum.py               # Main application
├── modules/               # Core modules
│   ├── config.py         # Configuration handling
│   └── utils.py          # Utility functions
├── tests/                # Test suite
└── config.yaml           # Default configuration
```

### Adding New Features
1. Follow existing code structure in `websum.py`
2. Add configuration in `config.yaml` if needed
3. Include utility functions in `modules/utils.py`
4. Add tests in `tests/` directory

### Testing
```bash
pytest tests/
```

### Debug Mode
Enable verbose logging with `--debug` flag:
```bash
python websum.py https://example.com --debug
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Add your changes
4. Write/update tests
5. Submit a pull request

### Current Focus Areas
- Content summarization improvements
- Multi-page crawling optimization
- Enhanced error handling
- Additional media capture options

## Known Limitations

1. **Media Capture**
   - Large pages may take longer to capture
   - Some dynamic content might not render
   - Memory usage increases with page size

2. **Crawling**
   - Rate limiting on some sites
   - JavaScript-heavy pages may need extra time
   - Some sites block automated access

3. **Output**
   - Large files in media directory
   - PDF formatting may vary by page

## License

MIT License - See LICENSE file for details

## Acknowledgments

- Built with [Crawl4AI](https://github.com/unclecode/crawl4ai)
- Uses [Playwright](https://playwright.dev/) for media capture
- Inspired by documentation management needs

---
For bug reports and feature requests, please open an issue on GitHub.
