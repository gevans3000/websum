# WebSum: Smart Web Content Collector and Knowledge Base 

WebSum helps you collect and organize web content into a structured knowledge base. It's like having a smart research assistant that not only saves web pages but also organizes them for both human reading and AI understanding.

## What Does It Do? 

1. **Smart Content Collection**:
   - Takes snapshots of web pages
   - Extracts clean, readable content
   - Preserves code examples and technical details
   - Follows links automatically

2. **Knowledge Base Organization**:
   - Creates categorized folders
   - Generates AI-friendly documentation
   - Preserves technical context and relationships
   - Links related content together

3. **Enhanced Metadata**:
   - Extracts technical terms
   - Identifies programming languages
   - Preserves code examples
   - Maintains cross-references

## Getting Started 

### 1. Install Python
- Download Python from [python.org](https://python.org)
- During installation, check "Add Python to PATH"

### 2. Install WebSum
Open Command Prompt (cmd) and type:
```bash
pip install -r requirements.txt
```

## How to Use 

### Basic Usage
```bash
python websum.py website-address
```
Example:
```bash
python websum.py docs.python.org/tutorial
```

### Creating a Knowledge Base 

#### Basic Knowledge Base Entry
```bash
python websum.py docs.example.com/page --kb-root knowledge_base --kb-category python/tutorials
```
This will:
- Create a knowledge base in the `knowledge_base` directory
- Organize content under the `python/tutorials` category
- Generate an AI-friendly markdown file

#### Add Metadata
```bash
python websum.py docs.example.com/page \
  --kb-root knowledge_base \
  --kb-category python/tutorials \
  --kb-title "Python Lists Tutorial" \
  --kb-summary "Complete guide to Python lists and list operations" \
  --kb-keywords "python,lists,tutorial,programming"
```

### Control What to Download 

#### Depth Control
```bash
python websum.py docs.python.org/tutorial --depth 2
```
- `--depth 2`: Follow links up to 2 clicks deep
- `--depth 1`: Only direct links
- `--depth 0`: Just the specified page

#### Page Limits
```bash
python websum.py docs.python.org/tutorial --page-limit 5
```
- `--page-limit 5`: Stop after 5 pages
- Good for testing or small collections

#### Rate Limiting
```bash
python websum.py docs.python.org/tutorial --rate-limit 2
```
- `--rate-limit 2`: Wait 2 seconds between pages
- Be nice to websites!

### Debug Mode
```bash
python websum.py docs.python.org/tutorial --debug
```
- Shows detailed progress
- Helpful for troubleshooting

## Knowledge Base Structure 

### Directory Organization
```
knowledge_base/
├── python/
│   ├── tutorials/
│   │   └── python_lists_tutorial.md
│   └── advanced/
│       └── python_decorators_guide.md
└── javascript/
    └── basics/
        └── javascript_functions_tutorial.md
```

### File Format
Each `.md` file contains:
1. **Document Metadata**
   - Title and source URL
   - Category and keywords
   - Last modified date

2. **Quick Summary**
   - Overview of the content
   - Main learning points

3. **Technical Context**
   - Programming languages used
   - Key technical terms
   - Required dependencies

4. **Main Content**
   - Clean, formatted text
   - Code examples with language tags
   - Step-by-step instructions
   - Important notes and warnings

5. **Related Resources**
   - Links to related pages
   - References and citations

## Examples 

### Create a Python Tutorial Knowledge Base
```bash
# Download Python tutorial with metadata
python websum.py docs.python.org/tutorial/introduction \
  --kb-root python_tutorials \
  --kb-category basics \
  --kb-title "Introduction to Python" \
  --kb-summary "Getting started with Python programming" \
  --kb-keywords "python,beginner,tutorial" \
  --depth 1 \
  --page-limit 5
```

### Build a Technical Documentation Library
```bash
# Download API documentation
python websum.py api.example.com/docs \
  --kb-root api_docs \
  --kb-category rest_api \
  --kb-title "REST API Reference" \
  --kb-summary "Complete API documentation with examples" \
  --kb-keywords "api,rest,reference" \
  --depth 2 \
  --rate-limit 1
```

## Tips for Success 

### Knowledge Base Organization
1. **Use Clear Categories**:
   - `language/topic` (e.g., `python/basics`)
   - `framework/feature` (e.g., `react/hooks`)
   - `platform/guide` (e.g., `aws/lambda`)

2. **Descriptive Titles**:
   - Include the main topic
   - Mention the type (tutorial, guide, reference)
   - Keep it concise

3. **Helpful Summaries**:
   - What will readers learn?
   - Who is it for?
   - What prerequisites are needed?

### Best Practices 

1. **Be Respectful**:
   - Use `--rate-limit` to avoid overwhelming servers
   - Start with small `--page-limit` values
   - Check website's terms of service

2. **Organize Thoughtfully**:
   - Create logical category hierarchies
   - Use consistent naming
   - Add helpful metadata

3. **Test First**:
   - Start with `--depth 1` and small limits
   - Use `--debug` to see what's happening
   - Verify content quality before large downloads

## Need Help? 

If you encounter issues:
1. Check command syntax carefully
2. Use `--debug` for detailed information
3. Start with minimal options and add more as needed
4. Verify URLs are accessible
5. Check your internet connection

## Safety Tips 

1. **Website Courtesy**:
   - Always use rate limiting
   - Respect robots.txt
   - Don't overload servers

2. **Content Management**:
   - Start with small downloads
   - Check content quality
   - Backup important knowledge bases

3. **System Resources**:
   - Monitor disk space
   - Watch memory usage
   - Use reasonable page limits
