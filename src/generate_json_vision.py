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

MODEL_ID = 'gemini-2.5-flash'

PROMPT_TEMPLATE = """
You are an expert University Curriculum Data Extractor. 
Read the provided scanned PDF document (which contains the curriculum).
Extract the curriculum structure and course details from the document.
Format the output EXACTLY as a valid JSON object, with no markdown formatting or extra text.

Required JSON Structure:
{
  "program_name": "Name of the Program (e.g. Bachelor of Fine Arts Program in ...)",
  "major_tracks": ["Track 1", "Track 2"], // List any specialized tracks/majors students can choose. If none, output ["None"].
  "courses": [
    {
      "course_code": "001101",
      "course_name_en": "Fundamental English 1",
      "course_name_th": "ภาษาอังกฤษพื้นฐาน 1", 
      "credits": "3",
      "category_or_track": "General Education / Core / etc.", 
      "prerequisites": ["None"] // or list of course codes
    }
  ]
}

Extract all courses mentioned in the curriculum text.
If no prerequisites are mentioned, put ["None"].
Return ONLY the JSON object. Do not include markdown formatting like ```json.
"""

def main():
    pdf_dir = Path("data/pdf")
    json_dir = Path("data/json_db")
    
    all_pdfs = list(pdf_dir.rglob("*.pdf"))
    
    unprocessed_pdfs = []
    for pdf_path in all_pdfs:
        rel_path = pdf_path.relative_to(pdf_dir)
        json_path = json_dir / rel_path.with_suffix('.json')
        if not json_path.exists():
            unprocessed_pdfs.append(pdf_path)
            
    print(f"Total PDFs: {len(all_pdfs)}")
    print(f"Remaining unprocessed PDFs (Scanned files): {len(unprocessed_pdfs)}")
    
    if len(unprocessed_pdfs) == 0:
        print("All PDFs have been processed! Exiting.")
        return
        
    print("Running in PRODUCTION MODE (Processing all remaining scanned PDFs) with Auto-Switching API Keys...")
    
    current_key_idx = 0
    client = genai.Client(api_key=api_keys[current_key_idx])
    print(f"Using API Key #{current_key_idx + 1}")
    
    for pdf_path in unprocessed_pdfs:
        rel_path = pdf_path.relative_to(pdf_dir)
        out_file_path = json_dir / rel_path.with_suffix('.json')
        out_file_path.parent.mkdir(parents=True, exist_ok=True)
        
        print(f"Processing: {pdf_path.name}")
        
        success = False
        while not success:
            try:
                # Upload the file to Gemini API
                uploaded_file = client.files.upload(file=str(pdf_path))
                
                response = client.models.generate_content(
                    model=MODEL_ID,
                    contents=[
                        uploaded_file,
                        PROMPT_TEMPLATE
                    ],
                    config=types.GenerateContentConfig(
                        response_mime_type="application/json",
                    ),
                )
                
                # Delete the file after processing
                client.files.delete(name=uploaded_file.name)
                
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
                    print(f"[WARNING] Invalid JSON generated for {pdf_path.name}: {e}")
                    debug_path = out_file_path.with_suffix('.debug.txt')
                    with open(debug_path, 'w', encoding='utf-8') as f:
                        f.write(result_json)
                    print(f"          Saved raw output to {debug_path}")
                    success = True
                    
            except APIError as e:
                # If we hit quota or rate limit, switch key
                if "429" in str(e) or "RESOURCE_EXHAUSTED" in str(e):
                    print(f"[WARN] API Key #{current_key_idx + 1} exhausted.")
                    current_key_idx += 1
                    if current_key_idx < len(api_keys):
                        print(f"[*] Auto-switching to API Key #{current_key_idx + 1}...")
                        client = genai.Client(api_key=api_keys[current_key_idx])
                        time.sleep(2)
                    else:
                        print("[ERROR] ALL API KEYS EXHAUSTED! Please provide more keys.")
                        return
                else:
                    print(f"[ERROR] API Error processing {pdf_path.name}: {e}")
                    break
            except Exception as e:
                print(f"[CRITICAL ERROR] Error processing {pdf_path.name}: {e}")
                print("Exiting to prevent quota waste due to local errors.")
                exit(1)
                
            print("Sleeping for 15 seconds to respect rate limits...")
            time.sleep(15)

if __name__ == "__main__":
    main()
