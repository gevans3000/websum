"""
Comprehensive test suite for WebSum.
Tests cover core functionality, edge cases, and integration scenarios.
"""

import pytest
import os
import aiohttp
import yaml
from bs4 import BeautifulSoup
from pathlib import Path
from unittest.mock import Mock, patch
from websum import (
    get_default_config,
    extract_documentation,
    process_markdown,
    format_code_block,
    format_text_content,
    CrawlProgress,
    RateLimiter,
    URLCache
)

# Test Data
SAMPLE_HTML = """
<html>
    <head><title>Test Doc</title></head>
    <body>
        <main>
            <h1>Test Documentation</h1>
            <p>Sample text content.</p>
            <pre><code class="language-python">
def test_function():
    return "Hello"
            </code></pre>
        </main>
        <nav>Navigation content</nav>
    </body>
</html>
"""

SAMPLE_CONFIG = {
    'output': {
        'dir': './test_output',
        'cache_file': 'test_cache.json'
    },
    'crawler': {
        'max_buffer_size': 1000000,
        'chunk_size': 524288,
        'stream_mode': True,
        'page_limit': 5
    }
}

@pytest.fixture
def setup_test_env():
    """Set up test environment with temporary directories and files."""
    test_dir = Path("./test_output")
    test_dir.mkdir(exist_ok=True)
    yield test_dir
    # Cleanup
    for file in test_dir.glob("*"):
        file.unlink()
    test_dir.rmdir()

class TestConfiguration:
    """Test configuration loading and validation."""
    
    def test_default_config(self):
        """Test default configuration values."""
        config = get_default_config()
        assert config is not None
        assert 'output' in config
        assert 'crawler' in config
        assert 'content' in config
        assert 'rate_limit' in config

    def test_custom_config_loading(self):
        """Test loading custom configuration."""
        with open('test_config.yaml', 'w') as f:
            yaml.dump(SAMPLE_CONFIG, f)
        # Test loading custom config
        # Add your config loading test here
        os.remove('test_config.yaml')

    def test_config_validation(self):
        """Test configuration validation."""
        # Test invalid configurations
        invalid_configs = [
            {'crawler': {'max_buffer_size': -1}},
            {'rate_limit': {'delay_seconds': 0}},
            {'content': {'word_count_threshold': 'invalid'}}
        ]
        for config in invalid_configs:
            with pytest.raises(ValueError):
                # Add your config validation test here
                pass

class TestContentProcessing:
    """Test content processing and formatting."""

    def test_markdown_conversion(self):
        """Test HTML to Markdown conversion."""
        soup = BeautifulSoup(SAMPLE_HTML, 'html.parser')
        result = process_markdown(soup)
        assert "# Test Documentation" in result
        assert "```python" in result
        assert "def test_function():" in result

    def test_code_block_formatting(self):
        """Test code block detection and formatting."""
        code_block = '''
        def test():
            print("hello")
        '''
        formatted = format_code_block(code_block, "python")
        assert "def test():" in formatted
        assert "print(" in formatted

    def test_text_content_formatting(self):
        """Test text content cleaning and formatting."""
        text = "  Multiple     spaces   and\nlines\n"
        formatted = format_text_content(text)
        assert "Multiple spaces and" in formatted
        assert "\n" in formatted

class TestCrawling:
    """Test web crawling functionality."""

    @pytest.mark.asyncio
    async def test_page_extraction(self):
        """Test extracting content from a web page."""
        async with aiohttp.ClientSession() as session:
            with patch('aiohttp.ClientSession.get') as mock_get:
                mock_get.return_value.__aenter__.return_value.text = \
                    Mock(return_value=SAMPLE_HTML)
                result = await extract_documentation("http://test.com")
                assert result is not None
                assert "Test Documentation" in result.content

    def test_rate_limiting(self):
        """Test rate limiting functionality."""
        limiter = RateLimiter(delay_seconds=0.1)
        # Test rate limiting
        start_time = time.time()
        for _ in range(3):
            limiter.wait()
        duration = time.time() - start_time
        assert duration >= 0.2

    def test_url_caching(self):
        """Test URL caching mechanism."""
        cache = URLCache("test_cache.json")
        url = "http://test.com"
        assert not cache.is_cached(url)
        cache.add_url(url)
        assert cache.is_cached(url)

class TestErrorHandling:
    """Test error handling and recovery."""

    @pytest.mark.asyncio
    async def test_network_errors(self):
        """Test handling of network errors."""
        with patch('aiohttp.ClientSession.get') as mock_get:
            mock_get.side_effect = aiohttp.ClientError
            with pytest.raises(aiohttp.ClientError):
                await extract_documentation("http://nonexistent.com")

    def test_invalid_html(self):
        """Test handling of invalid HTML."""
        invalid_html = "<invalid><html>"
        soup = BeautifulSoup(invalid_html, 'html.parser')
        result = process_markdown(soup)
        assert result is not None  # Should handle invalid HTML gracefully

class TestIntegration:
    """Integration tests for the complete workflow."""

    @pytest.mark.asyncio
    async def test_complete_workflow(self, setup_test_env):
        """Test the complete documentation extraction workflow."""
        test_url = "http://test.com/docs"
        with patch('aiohttp.ClientSession.get') as mock_get:
            mock_get.return_value.__aenter__.return_value.text = \
                Mock(return_value=SAMPLE_HTML)
            result = await extract_documentation(test_url)
            assert result is not None
            assert result.success
            assert os.path.exists(result.output_file)

    def test_multiple_pages(self, setup_test_env):
        """Test processing multiple pages."""
        urls = [
            "http://test.com/page1",
            "http://test.com/page2"
        ]
        # Test multiple page processing
        # Add your multiple page test here

class TestPerformance:
    """Performance tests."""

    def test_memory_usage(self):
        """Test memory usage during processing."""
        import memory_profiler
        
        @memory_profiler.profile
        def process_large_content():
            large_html = SAMPLE_HTML * 1000
            soup = BeautifulSoup(large_html, 'html.parser')
            return process_markdown(soup)
        
        result = process_large_content()
        assert result is not None

    @pytest.mark.asyncio
    async def test_processing_speed(self):
        """Test processing speed for various content sizes."""
        sizes = [1, 10, 100]  # KB sizes
        times = []
        
        for size in sizes:
            content = SAMPLE_HTML * size
            start_time = time.time()
            soup = BeautifulSoup(content, 'html.parser')
            result = process_markdown(soup)
            times.append(time.time() - start_time)
            
        # Verify processing time scales reasonably
        assert times[-1] < times[0] * len(sizes) * 2  # Should scale sub-linearly

def run_all_tests():
    """Run all tests and generate a coverage report."""
    pytest.main(['--cov=websum', '--cov-report=html', 'tests/'])

if __name__ == '__main__':
    run_all_tests()
