import os
import sys
import json
import hashlib

def compress_page(content):
    """Minify content while preserving key information"""
    if not isinstance(content, dict):
        return content
    
    # Keep only essential fields with shortened keys
    return {
        't': content.get('title', '').strip(),          # t = title
        'c': content.get('content', '')[:2000],         # c = content (first 2000 chars)
        'k': list(content.get('keywords', [])[:5]),     # k = keywords
        'u': content.get('url', '')[-50:]               # u = url fragment
    }

def merge_pages(input_dir):
    combined = []
    seen_hashes = set()
    
    for filename in os.listdir(input_dir):
        if not filename.endswith('.json'):
            continue
            
        try:
            with open(os.path.join(input_dir, filename), 'r') as f:
                page = json.load(f)
                compressed = compress_page(page)
                
                # Create content hash for deduplication
                content_hash = hashlib.md5(
                    (compressed['t'] + compressed['c']).encode()
                ).hexdigest()
                
                if content_hash not in seen_hashes:
                    seen_hashes.add(content_hash)
                    combined.append(compressed)
                    
        except Exception as e:
            print(f"Skipping {filename}: {str(e)}")
            continue
    
    # Save with minimal JSON formatting
    output_file = os.path.join(input_dir, 'compressed_knowledge.json')
    with open(output_file, 'w') as f:
        json.dump(combined, f, separators=(',', ':'), ensure_ascii=False)
    
    print(f"Created compressed knowledge base: {len(combined)} pages")
    print(f"Output file: {output_file}")

if __name__ == '__main__':
    if len(sys.argv) != 2:
        print("Usage: python compress_knowledge.py <directory_path>")
        sys.exit(1)
    
    merge_pages(sys.argv[1])