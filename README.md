# WebSum

A powerful web content extraction and summarization tool that crawls documentation pages and saves them in a structured knowledge base format.

## Features

- **Smart Web Crawling**: Uses Crawl4AI for efficient and accurate content extraction
- **Markdown Processing**: Advanced markdown formatting with proper code block handling, list formatting, and link cleanup
- **Media Support**: Captures screenshots and PDFs of documentation pages
- **Test Mode**: Preview extracted content without saving to verify processing
- **Duplicate Prevention**: Built-in protection against double crawling of URLs
- **Structured Output**: Organizes content in a knowledge base format optimized for both humans and LLMs

## Installation

```bash
pip install -r requirements.txt
```

## Usage

### Basic Usage

```bash
python websum.py URL [URL...] --output path/to/output
```

### Test Mode

Preview content extraction without saving files:

```bash
python websum.py URL --test
```

### Media Options

Capture screenshots or PDFs:

```bash
python websum.py URL --media screenshots  # Capture screenshots
python websum.py URL --media pdf          # Generate PDFs
python websum.py URL --media all          # Both screenshots and PDFs
```

### Output Format Options

```bash
python websum.py URL --format standard    # Detailed output with full structure
python websum.py URL --format condensed   # Brief overview with key points
```

### Debug Mode

Enable detailed logging:

```bash
python websum.py URL --debug
```

## Configuration

The tool uses environment variables for performance optimization:

- `CRAWL4AI_MAX_BUFFER_SIZE`: 1MB buffer for memory efficiency
- `CRAWL4AI_CHUNK_SIZE`: 512KB chunks for streaming
- `CRAWL4AI_STREAM_MODE`: Enabled by default for large pages

## Output Structure

### Knowledge Base Format

Files are saved with the following structure:
```
output/
  ├── domain.com/
  │   ├── page-title.md           # Main content
  │   ├── page-title.png          # Screenshot (if enabled)
  │   └── page-title.pdf          # PDF (if enabled)
  └── metadata.json               # Crawl metadata
```

### Markdown Processing

The tool handles various markdown elements:
- Code blocks with language detection
- Headers with proper spacing
- Ordered and unordered lists
- Links with clean formatting
- Bold and italic text
- Images with alt text

## Error Handling

- Automatic retry for failed requests
- Rate limiting to prevent server overload
- Memory usage monitoring
- Detailed error logging in debug mode

## Dependencies

- Python 3.7+
- Crawl4AI 0.4.248+
- Playwright for browser automation
- BeautifulSoup4 for HTML processing
- Other dependencies listed in requirements.txt

## Known Limitations

- JavaScript-heavy pages may require additional wait time
- Some dynamic content may not be captured
- PDF generation may vary based on page layout

## Contributing

1. Fork the repository
2. Create a feature branch
3. Submit a pull request

## License

MIT License - see LICENSE file for details
