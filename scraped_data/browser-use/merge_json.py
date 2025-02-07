import os
import sys
import json
import re

def extract_instructions(content):
    """Extract only installation and usage instructions from content"""
    instructions = {}
    text = json.dumps(content) if isinstance(content, dict) else str(content)
    
    # Installation instructions pattern
    install_match = re.search(
        r'(installation|setup|getting started)[^\n]*\n(.*?)(?=\n\S+:|$)',
        text, 
        re.IGNORECASE | re.DOTALL
    )
    if install_match:
        instructions['installation'] = clean_text(install_match.group(2))
    
    # Usage instructions pattern
    usage_match = re.search(
        r'(usage|basic usage|quick start|how to use)[^\n]*\n(.*?)(?=\n\S+:|$)',
        text,
        re.IGNORECASE | re.DOTALL
    )
    if usage_match:
        instructions['usage'] = clean_text(usage_match.group(2))
    
    return instructions

def clean_text(text):
    """Remove formatting and redundant content"""
    text = re.sub(r'\s+', ' ', text)          # Remove extra whitespace
    text = re.sub(r'\[.*?\]\(.*?\)', '', text) # Remove markdown links
    text = re.sub(r'http\S+', '', text)        # Remove URLs
    text = re.sub(r'[#\-*>`]', '', text)       # Remove markdown syntax
    return text.strip()

def process_directory(input_dir):
    training_data = []
    seen_content = set()
    
    for filename in os.listdir(input_dir):
        if filename.endswith(".json"):
            file_path = os.path.join(input_dir, filename)
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = json.load(f)
                    instructions = extract_instructions(content)
                    
                    if instructions:
                        # Create unique content identifier
                        content_hash = hash(json.dumps(instructions, sort_keys=True))
                        if content_hash not in seen_content:
                            seen_content.add(content_hash)
                            training_data.append({
                                "source": filename,
                                "instructions": instructions
                            })
                            
            except Exception as e:
                print(f"Skipping {filename}: {str(e)}")
    
    output_path = os.path.join(input_dir, "llm_instructions.json")
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(training_data, f, indent=2)
    
    print(f"Created focused training data with {len(training_data)} instruction sets")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python extract_instructions.py <directory_path>")
        sys.exit(1)
    
    process_directory(sys.argv[1])