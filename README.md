# WebSum - Web Scraping Tool

## 📋 Table of Contents
- [✨ Features](#-features)
- [🚀 Installation Guide](#-installation-guide)
- [🛠️ Basic Usage](#️-basic-usage)
- [📂 Output Structure](#-output-structure)
- [❓ FAQ](#-faq)
- [⚠️ Troubleshooting](#️-troubleshooting)

## ✨ Features
- Extract clean markdown from web pages
- Follow up to 3 links automatically
- Save results in organized folders
- Remove headers/footers automatically

## 🚀 Installation Guide

### Prerequisites
1. Install [Python 3.10+](https://www.python.org/downloads/)
   - Check installation: `python --version`
2. (Recommended) Create virtual environment:
   ```bash
   python -m venv venv
   venv\Scripts\activate  # Windows
   source venv/bin/activate  # Mac/Linux
   ```

### Installation Steps
1. Clone repository:
   ```bash
   git clone https://github.com/yourusername/websum.git
   cd websum
   ```
2. Install requirements:
   ```bash
   pip install crawl4ai
   ```

## 🛠️ Basic Usage
```bash
python websum.py [URL] [MAX_LINKS]
```

### Examples
1. Basic usage (3 links):
   ```bash
   python websum.py https://example.com
   ```
2. Get 5 links:
   ```bash
   python websum.py https://example.com 5
   ```
3. Save to custom location:
   ```bash
   python websum.py https://example.com
   # Output saved to 'scraped_data/[timestamp]'
   ```

## 📂 Output Structure
```
scraped_data/
└── 20240205_141543/          # Timestamp
    ├── base_page.md         # Main page content
    ├── link_1.md           # First linked page
    └── link_2.md           # Second linked page
```

## ❓ FAQ
**Q:** How do I know if Python is installed correctly?
> Run `python --version` in your terminal. You should see 3.10 or higher.

**Q:** What if I get permission errors?
> Try running as administrator: Right-click Command Prompt > "Run as administrator"

**Q:** Where can I learn more about web scraping?
> - [Beautiful Soup Documentation](https://www.crummy.com/software/BeautifulSoup/bs4/doc/)
> - [Scrapy Tutorial](https://docs.scrapy.org/en/latest/intro/tutorial.html)

## ⚠️ Troubleshooting
| Error | Solution |
|-------|----------|
| ModuleNotFoundError | Run `pip install -r requirements.txt` |
| Invalid URL | Add http:// prefix (e.g. `http://example.com`) |
| Empty output | Check if website blocks scrapers |

## 🤝 Support
For additional help:
- [Python Virtual Environments Guide](https://docs.python.org/3/tutorial/venv.html)
- [crawl4ai Documentation](https://pypi.org/project/crawl4ai/)

---
📝 License: MIT | ⚠️ Use responsibly | 🕵️ Respect robots.txt
