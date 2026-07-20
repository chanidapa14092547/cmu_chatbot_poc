import os
import json
import time
from pathlib import Path
from dotenv import load_dotenv
from google import genai
from google.genai import types
from google.genai.errors import APIError

load_dotenv()

API_KEYS = [k.strip() for k in os.getenv("GEMINI_API_KEYS", "").split(",") if k.strip()]
current_key_idx = 0
client = genai.Client(api_key=API_KEYS[current_key_idx])

MODEL_ID = 'gemini-2.5-flash'

prompt = """You are a JSON repair expert.
The user will provide an invalid JSON string (usually containing unescaped quotes inside string values, missing commas, or truncated arrays).
Your task is to fix ALL syntax errors and return the EXACT same data as a perfectly valid, structurally sound JSON object.
Do NOT change the keys or the data schema. Just fix the formatting."""

data_dir = Path("data/json_db")
debug_files = list(data_dir.rglob("*.debug.txt"))
print(f"Found {len(debug_files)} debug files to fix.")

for debug_path in debug_files:
    json_path = debug_path.with_suffix("").with_suffix(".json")
    if json_path.exists():
        print(f"Skipping {debug_path.name} (JSON already exists)")
        continue

    print(f"Fixing: {debug_path.name}")
    raw_text = debug_path.read_text(encoding="utf-8")
    
    success = False
    while not success:
        try:
            response = client.models.generate_content(
                model=MODEL_ID,
                contents=[prompt, raw_text],
                config=types.GenerateContentConfig(
                    response_mime_type="application/json",
                    temperature=0.1
                )
            )
            fixed_json_str = response.text
            
            # Verify it parses
            parsed_data = json.loads(fixed_json_str)
            
            # Save
            json_path.write_text(json.dumps(parsed_data, indent=2, ensure_ascii=False), encoding="utf-8")
            print(f"[SUCCESS] Fixed and saved to {json_path.name}")
            success = True
            
        except APIError as e:
            if "429" in str(e) or "RESOURCE_EXHAUSTED" in str(e):
                current_key_idx += 1
                if current_key_idx >= len(API_KEYS):
                    print("[ERROR] ALL API KEYS EXHAUSTED!")
                    exit(1)
                print(f"[*] Switching to API Key #{current_key_idx + 1}")
                client = genai.Client(api_key=API_KEYS[current_key_idx])
                time.sleep(2)
            else:
                print(f"[*] Server error (503), retrying in 5s... ({e})")
                time.sleep(5)
        except Exception as e:
            print(f"[ERROR] Failed to parse fixed JSON for {debug_path.name}: {e}")
            # Sometimes the model still fails, we just skip
            break
        
        time.sleep(4) # Respect rate limits

print("Done fixing debug files.")
