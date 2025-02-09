"""
Global pytest configuration and fixtures.
"""
import os
import pytest
import shutil
from pathlib import Path

@pytest.fixture(scope="session")
def test_output_dir(request):
    """Create and manage test output directory."""
    output_dir = Path("tests/test_data/output")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    def cleanup():
        if output_dir.exists():
            shutil.rmtree(output_dir)
    
    request.addfinalizer(cleanup)
    return output_dir

@pytest.fixture(scope="session")
def sample_html():
    """Sample HTML content for testing."""
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Test Documentation</title>
        <meta name="last-modified" content="2025-02-09">
    </head>
    <body>
        <main>
            <h1>Test Page</h1>
            <p>This is a test paragraph with some <code>inline code</code>.</p>
            <pre><code>
            def test_function():
                return "Hello, World!"
            </code></pre>
        </main>
    </body>
    </html>
    """

@pytest.fixture(scope="session")
def expected_markdown():
    """Expected markdown output for sample HTML."""
    return """# Test Page

This is a test paragraph with some `inline code`.

```python
def test_function():
    return "Hello, World!"
```
"""

@pytest.fixture(autouse=True)
def setup_logging(request):
    """Configure logging for tests."""
    import logging.config
    
    # Ensure test log directory exists
    log_dir = Path("tests/test_data/logs")
    log_dir.mkdir(parents=True, exist_ok=True)
    
    # Configure test logging
    logging.config.dictConfig({
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "detailed": {
                "format": "%(asctime)s | %(levelname)s | %(name)s | %(module)s:%(lineno)d | %(message)s",
                "datefmt": "%Y-%m-%d %H:%M:%S"
            }
        },
        "handlers": {
            "test_log": {
                "class": "logging.FileHandler",
                "filename": str(log_dir / "test.log"),
                "formatter": "detailed",
                "level": "DEBUG"
            }
        },
        "loggers": {
            "websum": {
                "level": "DEBUG",
                "handlers": ["test_log"]
            }
        }
    })
    
    def cleanup():
        # Cleanup logs after tests
        if request.node.testsfailed == 0 and log_dir.exists():
            shutil.rmtree(log_dir)
    
    request.addfinalizer(cleanup)
