# WebSum: Website Content Collector 📚

WebSum helps you save website content for offline reading or research. Think of it like a smart camera that can take snapshots of web pages and organize them neatly on your computer.

## What Does It Do? 🤔

1. **Collects Content**: Takes snapshots of web pages you're interested in
2. **Follows Links**: Can automatically visit links on the pages (like clicking through a website)
3. **Saves Everything Neatly**: Creates organized folders with:
   - Clean, readable text files
   - Complete page content (for advanced users)
   - Links found on each page

## Getting Started 🚀

### 1. Install Python
- Download Python from [python.org](https://python.org)
- During installation, check "Add Python to PATH"

### 2. Install WebSum
Open Command Prompt (cmd) and type:
```bash
pip install -r requirements.txt
```

## How to Use 💡

### Basic Usage
Open Command Prompt in the WebSum folder and type:
```bash
python websum.py website-address
```
Example:
```bash
python websum.py docs.python.org/tutorial
```

### Control How Much to Download

#### Depth (How Far to Click)
`--depth 2` means:
- Visit the starting page
- Click links on that page
- Click links on those pages
```bash
python websum.py docs.python.org/tutorial --depth 2
```

#### Page Limit (How Many Pages)
`--page-limit 5` means:
- Stop after downloading 5 pages
```bash
python websum.py docs.python.org/tutorial --page-limit 5
```

#### Be Nice to Websites
`--rate-limit 2` means:
- Wait 2 seconds between downloading pages
```bash
python websum.py docs.python.org/tutorial --rate-limit 2
```

### See What's Happening
Add `--debug` to see detailed progress:
```bash
python websum.py docs.python.org/tutorial --debug
```

## Where to Find Your Downloads 📁

- Look for a folder called `scraped_data`
- Inside, you'll find folders named with dates (like `20250206_124442`)
- Each folder contains:
  - `readable_text.txt`: Easy-to-read content
  - `content.json`: Complete data (for advanced users)

## Examples 📝

### Download a Few Tutorial Pages
```bash
python websum.py docs.python.org/tutorial --depth 1 --page-limit 3
```
This will:
- Start at the tutorial page
- Download up to 3 pages
- Only follow direct links (depth 1)

### Download Documentation Carefully
```bash
python websum.py docs.python.org/tutorial --depth 2 --page-limit 10 --rate-limit 1
```
This will:
- Download up to 10 pages
- Follow links two clicks deep
- Wait 1 second between pages

## Need Help? ❓

If you see error messages or need help:
1. Make sure you typed the website address correctly
2. Try adding `--debug` to see more details
3. Start with small numbers for `--depth` and `--page-limit`

## Safety Tips 🛡️

1. Always be respectful of websites:
   - Use `--rate-limit` to avoid downloading too quickly
   - Start with small `--page-limit` values
2. Some websites might not allow downloading content
3. Be careful with depth values - larger numbers can download many pages!
