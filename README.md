# WebSum: Documentation Scraping Made Easy

## What is This?
WebSum is a tool that helps you save documentation from websites to your computer. Think of it like taking pictures of pages in a book, but for websites! It's especially good at handling modern documentation with special features like code examples and lazy-loaded content.

## Setting Up Your Development Environment

### 1. Install Python
First, you need Python on your computer:
1. Visit [Python's website](https://python.org)
2. Download Python 3.9 or newer
3. During installation:
   - Check "Add Python to PATH"
   - Check "Install pip"
   - Check "Install for all users" (if available)

### 2. Create a Clean Environment
It's best to keep WebSum's tools separate from other Python projects. Here's how:

#### Using venv (Built-in Method)
```bash
# Create a new environment
python -m venv websum-env

# Activate the environment
# On Windows:
websum-env\Scripts\activate
# On macOS/Linux:
source websum-env/bin/activate
```

#### Using conda (Alternative Method)
If you have Anaconda or Miniconda installed:
```bash
# Create a new environment
conda create -n websum python=3.9

# Activate the environment
conda activate websum
```

### 3. Get the Code
1. Download the project:
   ```bash
   # Using command line
   git clone https://your-repository-url/websum.git
   cd websum
   ```
   Or download and extract the ZIP file from the project page.

2. Install required tools:
   ```bash
   pip install -r requirements.txt
   ```

### 4. Test Your Setup
Make sure everything works:
```bash
# Try a simple test
python websum.py --test https://docs.python.org/3/tutorial/

# If you see files in the crawl4ai_output folder, it worked!
```

## Using WebSum

### Basic Usage (Quick Start)
```bash
# Save a single page
python websum.py --test https://website.com/docs/page

# Save multiple pages
python websum.py --test https://website.com/docs/page1 https://website.com/docs/page2

# Save to a specific folder
python websum.py --test --output-dir my_docs https://website.com/docs/page
```

### Advanced Features

#### 1. Handling Modern Documentation
For sites with special features:
```bash
# For pages that load content as you scroll
python websum.py --test --scan-full yes https://website.com/docs/page

# For pages that take longer to load
python websum.py --test --timeout 120 https://website.com/docs/page
```

#### 2. Customizing Output
```bash
# Save with custom title
python websum.py --test --title "My Documentation" https://website.com/docs/page

# Include extra metadata
python websum.py --test --add-metadata yes https://website.com/docs/page
```

#### 3. Debugging Issues
```bash
# Get more information about what's happening
python websum.py --test --debug https://website.com/docs/page
```

## Understanding Your Results

### Output Files
When WebSum saves a page, it creates:

1. **Content File** (`*.md`)
   ```markdown
   # Page Title
   URL: https://website.com/docs/page
   Extracted: 2025-02-07T15:58:11
   
   [Main content here]
   ```

2. **Information File** (`*.json`)
   ```json
   {
     "url": "https://website.com/docs/page",
     "title": "Page Title",
     "timestamp": "2025-02-07T15:58:11",
     "word_count": 1234,
     "links": ["..."]
   }
   ```

### File Organization
```
crawl4ai_output/
├── Page_Title.md         # Human-readable content
├── Page_Title.json       # Technical information
└── images/              # (If images are saved)
    └── image1.png
```

## Tips for Success

### 1. Best Practices
- Always use a clean Python environment for each session
- Start with `--test` mode for new sites
- Use `--debug` when something doesn't work
- Keep your Python and tools updated

### 2. Common Issues and Solutions

#### Page Not Saving Correctly?
1. Check if the page is public (try opening in a private browser window)
2. Try increasing timeout:
   ```bash
   python websum.py --test --timeout 180 https://website.com/docs/page
   ```
3. Enable full page scanning:
   ```bash
   python websum.py --test --scan-full yes https://website.com/docs/page
   ```

#### Missing Content?
1. Check if content requires JavaScript:
   ```bash
   python websum.py --test --wait-for-js yes https://website.com/docs/page
   ```
2. Try different content selectors:
   ```bash
   python websum.py --test --selector ".main-content" https://website.com/docs/page
   ```

### 3. Maintaining Your Environment
```bash
# Update your tools
pip install --upgrade -r requirements.txt

# Check Python version
python --version

# Deactivate environment when done
deactivate  # (or 'conda deactivate' for conda)
```

## Technical Details

### Features
- Modern web crawler engine (Crawl4AI)
- Handles JavaScript-heavy sites
- Preserves code formatting
- Automatic retry on failures
- Structured data output
- Smart content detection
- Full-text search ready

### Configuration Options
```python
# Example configuration for complex sites
config = {
    "wait_until": "networkidle",  # Wait for page to fully load
    "scan_full_page": True,       # Handle infinite scroll
    "word_count_threshold": 3,    # Catch small code snippets
    "process_iframes": True,      # Handle embedded content
    "remove_overlay_elements": True  # Remove popups
}
```

## Need Help?

### Quick Troubleshooting
1. Is your environment activated?
2. Are you in the right directory?
3. Did you install all requirements?
4. Can you access the page in a browser?

### Getting Support
- Check the issues page for similar problems
- Include `--debug` output when reporting problems
- Share your Python version and operating system

## License and Usage

This project is free to use and share. Please:
- Check each website's terms of service
- Respect rate limits and robots.txt
- Give credit when sharing modifications
- Use responsibly and ethically

---

Remember: Always check a website's terms of service before scraping. Some sites may not allow automated access or content reproduction.
