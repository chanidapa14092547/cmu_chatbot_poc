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

api_keys = [k.strip() for k in API_KEYS_STR.split(",") if k.strip()]
MODEL_ID = 'gemini-3.5-flash'

PROMPT_TEMPLATE = """
Extract the curriculum structure and graduation credit requirements from this PDF and format it strictly as a Markdown document.
Focus on the sections that list the total credits required, general education, core courses, major compulsory, major electives, free electives, and any tracks/plans.
Use headers like ## General Education, ## Major, ## Free Electives.
List the credit amounts and any specific rules (e.g. "at least 15 credits", "must take 204111").
Do NOT include the lists of individual course titles unless they are explicitly required by code (e.g., "บังคับเรียน 206111").
Keep it concise and in Thai or English as presented in the document.

Output ONLY the markdown content.
"""

def generate_missing():
    json_dir = Path("data/json_db")
    cond_dir = Path("data/conditions")
    pdf_dir = Path("data/pdf")
    
    missing = []
    
    for root, _, files in os.walk(json_dir):
        faculty = os.path.basename(root)
        for f in files:
            if f.endswith(".json"):
                md_name = f.replace(".json", ".md")
                md_path = cond_dir / md_name
                if not md_path.exists():
                    json_path = Path(root) / f
                    pdf_name = f.replace(".json", ".pdf")
                    pdf_path = pdf_dir / faculty / pdf_name
                    if pdf_path.exists():
                        missing.append((md_path, pdf_path))
                    else:
                        print(f"PDF missing for {json_path}")
                        
    print(f"Found {len(missing)} missing MD files to generate.")
    
    current_key_idx = 0
    client = genai.Client(api_key=api_keys[current_key_idx])
    
    for md_path, pdf_path in missing:
        print(f"Generating for {md_path.name}...")
        success = False
        while not success:
            try:
                uploaded_file = client.files.upload(file=str(pdf_path))
                response = client.models.generate_content(
                    model=MODEL_ID,
                    contents=[
                        uploaded_file,
                        PROMPT_TEMPLATE
                    ]
                )
                client.files.delete(name=uploaded_file.name)
                
                md_content = response.text.strip()
                if md_content.startswith("```markdown"):
                    md_content = md_content[11:-3].strip()
                elif md_content.startswith("```"):
                    md_content = md_content[3:-3].strip()
                
                # Prepend the title
                title = f"# {md_path.name.replace('.md', '')}\n\n"
                with open(md_path, 'w', encoding='utf-8') as out_f:
                    out_f.write(title + md_content)
                    
                print(f"  [SUCCESS] Saved {md_path.name}")
                success = True
                
            except APIError as e:
                if "429" in str(e) or "RESOURCE_EXHAUSTED" in str(e):
                    current_key_idx += 1
                    if current_key_idx < len(api_keys):
                        print(f"  Switching API Key...")
                        client = genai.Client(api_key=api_keys[current_key_idx])
                        time.sleep(2)
                    else:
                        print("  [ERROR] ALL API KEYS EXHAUSTED!")
                        return
                else:
                    print(f"  [ERROR] {e}")
                    break
            except Exception as e:
                print(f"  [CRITICAL ERROR] {e}")
                break
                
            time.sleep(10)

if __name__ == "__main__":
    generate_missing()
