import os
import json
import time
from pathlib import Path
from dotenv import load_dotenv
from google import genai
from google.genai import types
from google.genai.errors import APIError

load_dotenv()
API_KEYS_STR = os.getenv("GEMINI_API_KEYS")

if not API_KEYS_STR:
    print("Error: GEMINI_API_KEYS not found in .env")
    exit(1)

api_keys = [k.strip() for k in API_KEYS_STR.split(",") if k.strip()]
if not api_keys:
    print("Error: No valid API keys found in GEMINI_API_KEYS")
    exit(1)

MODEL_ID = 'gemini-3.5-flash' # Upgrading back to the smart model!

PROMPT_TEMPLATE = """
You are an expert University Curriculum Data Extractor. 
Extract the curriculum structure and course details from the provided text.
Format the output EXACTLY as a valid JSON object, with no markdown formatting or extra text.

Required JSON Structure:
{
  "program_name": "Bachelor of Science Program in Data Science (or relevant name)",
  "major_tracks": ["Computer Science", "Mathematics", "Statistics"], // List any specialized tracks/majors students can choose. If none, output ["None"].
  "courses": [
    {
      "course_code": "001101",
      "course_name_en": "Fundamental English 1",
      "course_name_th": "ภาษาอังกฤษพื้นฐาน 1", 
      "credits": "3",
      "category_or_track": "General Education / Core / Computer Science Track", // Specify which category or major track this course belongs to
      "prerequisites": ["None"] // or list of course codes
    }
  ]
}

Extract all courses mentioned in the curriculum text.
If no prerequisites are mentioned, put ["None"].
Return ONLY the JSON object.

Text to process:
{text}
"""

def main():
    text_dir = Path("data/raw_text")
    json_dir = Path("data/json_db")
    
    if not text_dir.exists():
        print(f"Error: Directory {text_dir} does not exist.")
        return
        
    txt_files = list(text_dir.rglob("*.txt"))
    
    unprocessed_files = []
    for txt_path in txt_files:
        rel_path = txt_path.relative_to(text_dir)
        json_path = json_dir / rel_path.with_suffix('.json')
        if not json_path.exists():
            unprocessed_files.append(txt_path)
            
    print(f"Total files: {len(txt_files)}")
    print(f"Remaining unprocessed: {len(unprocessed_files)}")
    
    if len(unprocessed_files) == 0:
        print("All text files processed!")
        return
        
    print("Running in PRODUCTION MODE (Processing all text files) with Auto-Switching API Keys...")
    
    current_key_idx = 0
    client = genai.Client(api_key=api_keys[current_key_idx])
    print(f"Using API Key #{current_key_idx + 1}")
    
    for txt_path in unprocessed_files:
        rel_path = txt_path.relative_to(text_dir)
        out_file_path = json_dir / rel_path.with_suffix('.json')
        out_file_path.parent.mkdir(parents=True, exist_ok=True)
        
        print(f"Processing: {txt_path.name}")
        
        with open(txt_path, 'r', encoding='utf-8') as f:
            content = f.read()
            
        success = False
        while not success:
            try:
                response = client.models.generate_content(
                    model=MODEL_ID,
                    contents=PROMPT_TEMPLATE.replace("{text}", content),
                    config=types.GenerateContentConfig(
                        response_mime_type="application/json",
                    ),
                )
                
                result_json = response.text.strip()
                
                if result_json.startswith("```json"):
                    result_json = result_json[7:-3]
                elif result_json.startswith("```"):
                    result_json = result_json[3:-3]
                    
                try:
                    parsed_json = json.loads(result_json)
                    with open(out_file_path, 'w', encoding='utf-8') as f:
                        json.dump(parsed_json, f, ensure_ascii=False, indent=2)
                    print(f"[SUCCESS] Saved to: {out_file_path}")
                    success = True
                except json.JSONDecodeError as e:
                    print(f"[WARNING] Invalid JSON generated for {txt_path.name}: {e}")
                    # Save raw text for debugging
                    debug_path = out_file_path.with_suffix('.debug.txt')
                    with open(debug_path, 'w', encoding='utf-8') as f:
                        f.write(result_json)
                    print(f"          Saved raw output to {debug_path}")
                    success = True # Stop retrying on formatting errors
                    
                print("Sleeping for 4 seconds to respect rate limits...")
                time.sleep(4)
                
            except APIError as e:
                # If we hit quota or rate limit, switch key
                if "429" in str(e) or "RESOURCE_EXHAUSTED" in str(e):
                    print(f"[WARN] API Key #{current_key_idx + 1} exhausted.")
                    current_key_idx += 1
                    if current_key_idx < len(api_keys):
                        print(f"[*] Auto-switching to API Key #{current_key_idx + 1}...")
                        client = genai.Client(api_key=api_keys[current_key_idx])
                        time.sleep(2) # brief pause before retry
                    else:
                        print("[ERROR] ALL API KEYS EXHAUSTED! Please provide more keys.")
                        return
                else:
                    print(f"[ERROR] API Error processing {txt_path.name}: {e}")
                    break
            except Exception as e:
                print(f"[CRITICAL ERROR] Error processing {txt_path.name}: {e}")
                print("Exiting to prevent quota waste due to local errors.")
                exit(1)

if __name__ == "__main__":
    main()
