import os
import json

# Configuration
input_dir = r"C:\Users\lovel\source\repos\gevans3000\websum\scraped_data\crawl4ai json all"
output_file = os.path.join(input_dir, "combined_output.json")

def merge_json_files():
    combined_data = []
    
    # List all files in directory
    for filename in os.listdir(input_dir):
        if filename.endswith(".json"):
            file_path = os.path.join(input_dir, filename)
            
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    combined_data.append({
                        "source_file": filename,
                        "content": data
                    })
                print(f"Processed: {filename}")
            except Exception as e:
                print(f"Error processing {filename}: {str(e)}")
    
    # Save combined output
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(combined_data, f, indent=2)
    
    print(f"\nSuccessfully merged {len(combined_data)} files into {output_file}")

if __name__ == "__main__":
    merge_json_files()