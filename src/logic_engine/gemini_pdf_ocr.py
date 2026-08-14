import os
import glob
import json
import time
import re
import google.genai as genai
from google.genai import types
from dotenv import load_dotenv

load_dotenv(os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), ".env"))

RAW_DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "raw_data", "DS_extracted", "DS")
CATALOG_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "data", "json_db", "Faculty of Science", "Bachelor of Science Program in Data Science (2567).json")

def get_client():
    api_keys_str = os.environ.get("GEMINI_API_KEYS", "")
    api_keys = api_keys_str.split(',') if api_keys_str else [os.environ.get("GEMINI_API_KEY")]
    return genai.Client(api_key=api_keys[0].strip())

def process_pdfs():
    client = get_client()
    pdf_files = glob.glob(os.path.join(RAW_DATA_DIR, "*.pdf"))
    print(f"Found {len(pdf_files)} PDF files to process with Gemini API...")
    
    if not os.path.exists(CATALOG_PATH):
        print("Catalog not found.")
        return
        
    with open(CATALOG_PATH, 'r', encoding='utf-8') as f:
        catalog = json.load(f)
        
    course_dict = {c["course_code"]: c for c in catalog["courses"]}
    
    prompt = "วิชานี้มี 'เงื่อนไขที่ต้องผ่านก่อน' หรือ 'Prerequisite' ไหม? ถ้ามีให้ตอบเฉพาะรหัสวิชา 6 หลักที่ต้องผ่านก่อนเท่านั้น (เช่น 204101 หรือ 204101 และ 204102) ห้ามตอบคำอธิบายอื่น ถ้าไม่มีเงื่อนไขให้ตอบว่า None เท่านั้น"
    
    count = 0
    for filepath in pdf_files:
        basename = os.path.basename(filepath)
        course_code = basename.replace(".pdf", "").split("-")[0]
        
        if course_code not in course_dict:
            continue
            
        print(f"Processing {course_code}...", end=" ")
        
        try:
            # Upload to Gemini
            gemini_file = client.files.upload(file=filepath)
            
            # Generate content
            response = client.models.generate_content(
                model='gemini-3.5-flash',
                contents=[gemini_file, prompt]
            )
            
            reply = response.text.strip()
            print(f"Reply: {reply}")
            
            # Parse the reply to find course codes
            if "none" not in reply.lower():
                # Extract all 6-digit codes
                codes = re.findall(r'\b\d{6}\b', reply)
                if codes:
                    course_dict[course_code]["prerequisites"] = codes
            
            # Delete file to clean up space
            client.files.delete(name=gemini_file.name)
            
        except Exception as e:
            print(f"Failed: {e}")
            
        count += 1
        # Add a 2 second delay to avoid rate limits on free tier (15 RPM limit sometimes applies)
        time.sleep(3)
            
    with open(CATALOG_PATH, 'w', encoding='utf-8') as f:
        json.dump(catalog, f, ensure_ascii=False, indent=2)
    print(f"Finished processing {count} PDFs. Catalog updated.")

if __name__ == "__main__":
    process_pdfs()
