"""
Basic test for WebSum functionality.
Tests the core documentation extraction features.
"""

import pytest
from bs4 import BeautifulSoup
import html2text
from websum import process_markdown, format_code_block

def test_basic_markdown_processing():
    """Test basic markdown processing functionality."""
    # Sample HTML content
    html = """
    <html>
        <body>
            <h1>Test Documentation</h1>
            <p>This is a test paragraph.</p>
            <pre><code class="language-python">
def hello():
    print("Hello, World!")
            </code></pre>
        </body>
    </html>
    """
    
    # Create a BeautifulSoup object
    soup = BeautifulSoup(html, 'html.parser')
    
    # Convert HTML to markdown
    h = html2text.HTML2Text()
    h.body_width = 0  # Don't wrap text
    markdown = h.handle(str(soup))
    
    # Create a mock result object with the soup
    class MockResult:
        def __init__(self, soup, markdown):
            self.soup = soup
            self.success = True
            self.url = "http://test.com"
            self.error = None
            self.html = str(soup)
            self.markdown = markdown
            self.links = []
            self.title = "Test Documentation"
            self.summary = None
            self.keywords = []
            self.categories = []
            self.last_modified = None
            self.content = str(soup)
    
    mock_result = MockResult(soup, markdown)
    
    try:
        # Process the content
        result = process_markdown(mock_result)
        
        # Verify the results
        print("\nTest Results:")
        print("-" * 80)
        print(result)
        print("-" * 80)
        
        # Basic assertions
        assert result is not None, "Result should not be None"
        if result:
            assert "Test Documentation" in result, "Title should be in result"
            assert "This is a test paragraph" in result, "Paragraph should be in result"
            assert "def hello()" in result, "Code should be in result"
            assert "print(" in result, "Code should be in result"
    except Exception as e:
        print(f"\nError processing markdown: {str(e)}")
        print("Mock result attributes:")
        for attr in dir(mock_result):
            if not attr.startswith('__'):
                print(f"{attr}: {getattr(mock_result, attr)}")
        raise

def test_code_block_formatting():
    """Test code block formatting."""
    # Sample code block
    code = """
    def test_function():
        print("Hello")
        return True
    """
    
    # Format the code block
    result = format_code_block(code)
    
    print("\nFormatted Code Block:")
    print("-" * 80)
    print(result)
    print("-" * 80)
    
    # Verify formatting
    assert "def test_function()" in result
    assert "print(" in result
    assert "```" in result
    assert result.strip().startswith("```")
    assert result.strip().endswith("```")

def test_empty_code_block():
    """Test handling of empty code blocks."""
    result = format_code_block("")
    assert result.strip().startswith("```")
    assert result.strip().endswith("```")
    assert len(result.strip().split("\n")) >= 3  # At least opening, empty line, and closing

def test_whitespace_code_block():
    """Test handling of whitespace-only code blocks."""
    result = format_code_block("   \n  \n    ")
    assert result.strip().startswith("```")
    assert result.strip().endswith("```")
    assert len(result.strip().split("\n")) >= 3  # At least opening, empty line, and closing

if __name__ == "__main__":
    pytest.main(["-v", __file__])
