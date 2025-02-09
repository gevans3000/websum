"""
Unit tests for markdown processing functionality.
"""
import pytest
import html2text
from bs4 import BeautifulSoup
from websum import (
    process_markdown,
    clean_markdown,
    process_markdown_content,
    CrawlResult,
    WebSumError,
    ProcessingError
)

def test_clean_markdown():
    """Test markdown cleaning functionality."""
    # Test removing extra whitespace
    input_md = "This  has    extra   spaces\n\n\nAnd extra lines"
    expected = "This has extra spaces\n\nAnd extra lines"
    assert clean_markdown(input_md) == expected
    
    # Test handling empty input
    assert clean_markdown("") == ""
    assert clean_markdown(None) == ""
    
    # Test preserving code blocks
    input_md = "```python\ndef test():\n    pass\n```"
    assert clean_markdown(input_md) == input_md

def test_process_markdown_content():
    """Test markdown content processing."""
    # Test code block formatting
    input_md = "```\ndef test():\nreturn True\n```"
    expected = "```python\ndef test():\n    return True\n```"
    assert process_markdown_content(input_md).strip() == expected.strip()
    
    # Test list formatting
    input_md = "* Item 1\n* Item 2\n  * Subitem"
    result = process_markdown_content(input_md)
    assert "* Item 1" in result
    assert "* Item 2" in result
    assert "  * Subitem" in result

def test_process_markdown_with_html():
    """Test full markdown processing pipeline with HTML input."""
    # Sample HTML content
    html = """
    <html>
        <body>
            <h1>Test Page</h1>
            <p>This is a test paragraph.</p>
            <pre><code>def test():
    return True</code></pre>
        </body>
    </html>
    """
    
    # Create a mock crawl result
    result = CrawlResult()
    result.success = True
    result.html = html
    result.markdown = html2text.HTML2Text().handle(html)
    
    # Expected markdown output
    expected = """# Test Page

This is a test paragraph.

```python
def test():
    return True
```"""
    
    # Process the markdown
    processed = process_markdown(result)
    assert processed.strip() == expected.strip()

def test_process_markdown_error_handling():
    """Test error handling in markdown processing."""
    # Test with None result
    with pytest.raises(ProcessingError) as exc_info:
        process_markdown(None)
    assert "Invalid or failed crawl result" in str(exc_info.value)
    
    # Test with failed result
    result = CrawlResult()
    result.success = False
    result.error = "Test error"
    with pytest.raises(ProcessingError) as exc_info:
        process_markdown(result)
    assert "Failed crawl result" in str(exc_info.value)
    
    # Test with empty markdown
    result = CrawlResult()
    result.success = True
    result.markdown = ""
    with pytest.raises(ProcessingError) as exc_info:
        process_markdown(result)
    assert "No markdown content in result" in str(exc_info.value)
