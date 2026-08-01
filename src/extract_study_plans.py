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

MODELS = [
    'gemini-2.5-flash',
    'gemini-2.0-flash',
    'gemini-1.5-flash',
    'gemini-3.5-flash'
]

PROMPT_TEMPLATE = """
You are an expert University Curriculum Data Extractor.
Read the provided PDF curriculum document. Locate the "Recommended 4-Year Study Plan" (แผนการศึกษา / แผนการลงทะเบียนเรียน / ตัวอย่างแผนการศึกษา).
Extract the list of course codes recommended for each semester from Year 1 to Year 4.

Required JSON Structure:
{
  "year_1_semester_1": ["001101", "206111", "954100"],
  "year_1_semester_2": ["001102", "206112", "954140"],
  "year_2_semester_1": ["001201", "954210"],
  "year_2_semester_2": ["954240"],
  "year_3_semester_1": ["954310"],
  "year_3_semester_2": ["954340"],
  "year_4_semester_1": ["954410"],
  "year_4_semester_2": ["954440"]
}

Rules:
1. Only extract the 6-digit course codes (or course codes with letters like INX 101, 261102).
2. Do NOT include course names or credits in the arrays, JUST the course codes as strings.
3. If a semester has generic electives (like "Free Elective" or "Major Elective"), do not include generic text, only extract actual specific course codes if present.
4. If a semester is not found in the document, leave its array empty [].
5. Return ONLY valid JSON without markdown formatting.
"""

def main():
    pdf_dir = Path("data/pdf")
    json_dir = Path("data/json_db")
    
    all_jsons = list(json_dir.rglob("*.json"))
    unprocessed_jsons = []
    
    for json_path in all_jsons:
        try:
            with open(json_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            if "study_plan" not in data or not data["study_plan"]:
                unprocessed_jsons.append(json_path)
        except Exception as e:
            print(f"Error reading {json_path}: {e}")
            
    print(f"Total JSON files: {len(all_jsons)}")
    print(f"Remaining JSONs needing Study Plan: {len(unprocessed_jsons)}")
    
    if len(unprocessed_jsons) == 0:
        print("All JSONs already have study plans! Exiting.")
        return
        
    print("Running Study Plan Extractor with Multi-Model & Auto-Switching API Keys...")
    
    current_key_idx = 0
    current_model_idx = 0
    client = genai.Client(api_key=api_keys[current_key_idx])
    model_id = MODELS[current_model_idx]
    print(f"Using API Key #{current_key_idx + 1} with Model: {model_id}")
    
    for json_path in unprocessed_jsons:
        rel_path = json_path.relative_to(json_dir)
        pdf_path = pdf_dir / rel_path.with_suffix('.pdf')
        
        if not pdf_path.exists():
            print(f"[SKIP] Corresponding PDF not found for: {json_path.name}")
            continue
            
        print(f"Processing Study Plan for: {pdf_path.name}")
        
        success = False
        while not success:
            try:
                uploaded_file = client.files.upload(file=str(pdf_path))
                
                response = client.models.generate_content(
                    model=model_id,
                    contents=[
                        uploaded_file,
                        PROMPT_TEMPLATE
                    ],
                    config=types.GenerateContentConfig(
                        response_mime_type="application/json",
                    ),
                )
                
                client.files.delete(name=uploaded_file.name)
                
                result_json = response.text.strip()
                if result_json.startswith("```json"):
                    result_json = result_json[7:-3]
                elif result_json.startswith("```"):
                    result_json = result_json[3:-3]
                    
                try:
                    parsed_plan = json.loads(result_json)
                    
                    with open(json_path, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                        
                    data["study_plan"] = parsed_plan
                    
                    with open(json_path, 'w', encoding='utf-8') as f:
                        json.dump(data, f, ensure_ascii=False, indent=2)
                        
                    print(f"[SUCCESS] Updated Study Plan in: {json_path}")
                    success = True
                except json.JSONDecodeError as e:
                    print(f"[WARNING] Invalid JSON generated for {pdf_path.name}: {e}")
                    success = True
                    
            except APIError as e:
                print(f"[WARN] API Error with Model {model_id} on Key #{current_key_idx + 1}: {e}")
                current_model_idx += 1
                if current_model_idx < len(MODELS):
                    model_id = MODELS[current_model_idx]
                    print(f"[*] Switching to fallback Model: {model_id} on Key #{current_key_idx + 1}...")
                    time.sleep(2)
                else:
                    print(f"[WARN] All models exhausted on Key #{current_key_idx + 1}.")
                    current_model_idx = 0
                    model_id = MODELS[current_model_idx]
                    current_key_idx += 1
                    if current_key_idx < len(api_keys):
                        print(f"[*] Auto-switching to API Key #{current_key_idx + 1} with Model: {model_id}...")
                        client = genai.Client(api_key=api_keys[current_key_idx])
                        time.sleep(2)
                    else:
                        print("[ERROR] ALL API KEYS AND MODELS EXHAUSTED! Please try again later.")
                        return
            except Exception as e:
                print(f"[CRITICAL ERROR] Error processing {pdf_path.name}: {e}")
                print("Exiting to prevent quota waste due to local errors.")
                exit(1)
                
            print("Sleeping for 15 seconds to respect rate limits...")
            time.sleep(15)

if __name__ == "__main__":
    main()
