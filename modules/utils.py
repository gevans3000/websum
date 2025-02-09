"""Utility functions for text processing and URL handling."""
import re
from urllib.parse import urlparse

def clean_text(text):
    """Clean text by removing special characters and normalizing whitespace"""
    # Remove markdown links
    text = re.sub(r'\[([^\]]+)\]\([^\)]+\)', r'\1', text)
    
    # Remove special characters and normalize whitespace
    text = re.sub(r'[=\-\*•◦○●]+', '', text)  # Remove decorative characters
    text = re.sub(r'\s+', ' ', text)  # Normalize spaces and tabs
    text = text.strip()
    
    # Fix common encoding issues
    text = text.replace('â€™', "'")
    text = text.replace('â€"', "-")
    text = text.replace('â€œ', '"')
    text = text.replace('â€', '"')
    text = text.replace('â€¢', '•')
    
    return text

def is_navigation_text(text):
    """Check if text appears to be navigation or boilerplate content"""
    nav_patterns = [
        r'home|search|blog|changelog|quick\s+start|installation|deployment',
        r'previous|next|menu|navigation',
        r'copyright|terms|privacy|contact'
    ]
    return any(re.search(pattern, text.lower()) for pattern in nav_patterns)

def ensure_url_scheme(url):
    """Ensure URL has a proper scheme"""
    if not url.startswith(('http://', 'https://')):
        url = 'https://' + url.lstrip('/')
    return url

def clean_markdown(text):
    """Clean and format markdown text."""
    if not text:
        return ""
    
    # Remove extra newlines
    text = re.sub(r'\n{3,}', '\n\n', text)
    
    # Fix code block formatting
    text = re.sub(r'`` ```', '```', text)
    text = re.sub(r'``` `', '```', text)
    
    # Fix bold formatting
    text = re.sub(r'\*\*\s+```', '**```', text)
    text = re.sub(r'```\s+\*\*', '```**', text)
    
    # Fix list formatting
    text = re.sub(r'(\d+)\.\s+\*\*', r'\1. **', text)
    
    return text.strip()

def process_code(code_text):
    """Process and format code blocks."""
    code = code_text.strip()
    lang = "python" if any(keyword in code for keyword in ["import", "def", "class", "async"]) else ""
    return f"\n```{lang}\n{code}\n```\n"

def process_markdown_content(content):
    """Process markdown content with proper formatting."""
    if not content:
        return ""
    
    # Clean up markdown formatting
    content = clean_markdown(content)
    
    # Fix code block formatting
    def format_code(match):
        return process_code(match.group(1))
    
    content = re.sub(r'```(.*?)```', format_code, content, flags=re.DOTALL)
    return content
