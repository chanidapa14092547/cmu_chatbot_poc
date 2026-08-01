import os
import json
import time
from pathlib import Path
from google import genai
from google.genai import types
from google.genai.errors import APIError
with open(".env", "r") as f:
    for line in f:
        if line.startswith("GEMINI_API_KEYS="):
            API_KEYS_STR = line.strip().split("=", 1)[1].strip('"\'')
            break
    else:
        API_KEYS_STR = None

if not API_KEYS_STR:
    print("Error: GEMINI_API_KEYS not found in .env")
    exit(1)

api_keys = [k.strip() for k in API_KEYS_STR.split(",") if k.strip()]
MODEL_ID = 'gemini-3.5-flash'

PROMPT_TEMPLATE = """
You are an expert University Curriculum Data Extractor. 
I am providing you with:
1. The original PDF curriculum for this major.
2. The current extracted JSON data which contains a list of `major_tracks` and a list of `courses`.

Your task is to refine the `category_or_track` field for ONLY the "Major Elective" courses. 
In the PDF, elective courses are usually grouped by Track/Plan/Field of Study (e.g. "Data analytics using mathematical modeling").
For every course in the JSON that belongs to a specific track, append the exact track name from `major_tracks` to its `category_or_track`.

Example:
If course 204426 is under the "Data analytics using computational modeling" track, its category_or_track should become:
"Field of Specialization / Major / Major Elective Courses / Data analytics using computational modeling"

If a course applies to ALL tracks, leave it as is or append " / All Tracks".
Do not change the structure of the JSON. Do not add or remove courses. Just update the `category_or_track` strings.

Return ONLY the updated valid JSON object. No markdown formatting like ```json.
"""

def main():
    pdf_dir = Path("data/pdf")
    json_dir = Path("data/json_db")
    
    # Find all JSONs in all faculties that have major_tracks
    target_jsons = []
    for root, _, files in os.walk(json_dir):
        faculty = os.path.basename(root)
        for f in files:
            if f.endswith(".json"):
                json_path = os.path.join(root, f)
                with open(json_path, 'r', encoding='utf-8') as jf:
                    try:
                        data = json.load(jf)
                        tracks = data.get("major_tracks", [])
                        if tracks and len(tracks) > 0 and tracks[0].lower() != "none":
                            # Check if already enriched
                            already_enriched = False
                            for c in data.get("courses", []):
                                cat = c.get("category_or_track", "").lower()
                                for t in tracks:
                                    if t.lower() in cat:
                                        already_enriched = True
                                        break
                                if already_enriched: break
                                
                            if not already_enriched:
                                # We found a target!
                                pdf_path = pdf_dir / faculty / f.replace(".json", ".pdf")
                                if pdf_path.exists():
                                    target_jsons.append((Path(json_path), pdf_path))
                    except Exception:
                        pass
                
    print(f"Found {len(target_jsons)} programs across all faculties with major_tracks.")
    
    current_key_idx = 0
    client = genai.Client(api_key=api_keys[current_key_idx])
    
    for json_path, pdf_path in target_jsons:
        if not pdf_path.exists():
            print(f"[SKIP] PDF not found for {json_path.name}")
            continue
            
        print(f"\nProcessing: {json_path.name}")
        
        with open(json_path, 'r', encoding='utf-8') as f:
            current_json_str = f.read()
            
        success = False
        while not success:
            try:
                # Upload PDF
                print("  Uploading PDF...")
                uploaded_file = client.files.upload(file=str(pdf_path))
                
                print("  Generating enriched JSON...")
                response = client.models.generate_content(
                    model=MODEL_ID,
                    contents=[
                        uploaded_file,
                        f"CURRENT JSON DATA:\n{current_json_str}\n\n" + PROMPT_TEMPLATE
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
                    
                parsed_json = json.loads(result_json)
                
                # Save it back
                with open(json_path, 'w', encoding='utf-8') as f:
                    json.dump(parsed_json, f, ensure_ascii=False, indent=2)
                    
                print(f"  [SUCCESS] Enriched JSON saved for {json_path.name}")
                success = True
                
            except APIError as e:
                if "429" in str(e) or "RESOURCE_EXHAUSTED" in str(e):
                    print(f"  [WARN] API Key #{current_key_idx + 1} exhausted.")
                    current_key_idx += 1
                    if current_key_idx < len(api_keys):
                        print(f"  [*] Switching to API Key #{current_key_idx + 1}...")
                        client = genai.Client(api_key=api_keys[current_key_idx])
                        time.sleep(2)
                    else:
                        print("  [ERROR] ALL API KEYS EXHAUSTED!")
                        return
                else:
                    print(f"  [ERROR] API Error: {e}")
                    break
            except Exception as e:
                print(f"  [CRITICAL ERROR] {e}")
                break
                
            time.sleep(10) # rate limit pause

if __name__ == "__main__":
    main()
