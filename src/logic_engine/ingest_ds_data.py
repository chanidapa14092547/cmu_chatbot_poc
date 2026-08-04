import os
import glob
import json
import re
import sys
sys.path.append("/Users/memee/Library/Python/3.9/lib/python/site-packages")
import PyPDF2

RAW_DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "raw_data", "DS_extracted", "DS")
MOCK_SCHEDULE_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "mock_schedule.json")
CATALOG_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "data", "json_db", "Faculty of Science", "Bachelor of Science Program in Data Science (2567).json")

def get_term_from_date(date_str):
    if not date_str:
        return "Unknown"
    date_str = date_str.upper()
    term1_months = ["AUG", "SEP", "OCT", "NOV", "DEC"]
    term2_months = ["JAN", "FEB", "MAR", "APR", "MAY"]
    for m in term1_months:
        if m in date_str: return "1/2568"
    for m in term2_months:
        if m in date_str: return "2/2568"
    return "Summer"

def parse_xls_files():
    schedule_data = {"1/2568": {}, "2/2568": {}, "1/2569": {}, "Summer": {}, "Unknown": {}}
    xls_files = glob.glob(os.path.join(RAW_DATA_DIR, "*.xls"))
    
    print(f"Found {len(xls_files)} Excel files to process...")
    for filepath in xls_files:
        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
        
        # 1. Deduce term
        term = "Unknown"
        final_match = re.search(r'FINAL Exam.*?(\d{1,2}\s+[A-Z]+\s+\d{4})', content, re.IGNORECASE)
        midterm_match = re.search(r'MIDTERM Exam.*?(\d{1,2}\s+[A-Z]+\s+\d{4})', content, re.IGNORECASE)
        
        if final_match:
            term = get_term_from_date(final_match.group(1))
        elif midterm_match:
            term = get_term_from_date(midterm_match.group(1))
        else:
            basename = os.path.basename(filepath).lower()
            if "-2.xls" in basename: term = "2/2568"
            elif "-3.xls" in basename: term = "1/2569"
            else: term = "1/2568"
            
        if term not in schedule_data:
            term = "Unknown"

        # 2. Extract Course Code
        code_match = re.search(r'>\s*(\d{6})\s*-', content)
        if not code_match: continue
        course_code = code_match.group(1)
        
        # 3. Extract sections using regex
        sections = []
        rows = re.findall(r'<tr.*?>(.*?)</tr>', content, re.IGNORECASE | re.DOTALL)
        for row in rows:
            cols = re.findall(r'<td.*?>(.*?)</td>', row, re.IGNORECASE | re.DOTALL)
            if len(cols) >= 8:
                sec_text = re.sub(r'<[^>]+>', '', cols[3]).strip()
                if re.match(r'^\d{3}$', sec_text):
                    day_text = re.sub(r'<[^>]+>', ' ', cols[6]).strip()
                    time_text = re.sub(r'<[^>]+>', ' ', cols[7]).strip()
                    
                    time_match = re.search(r'(\d{4})\s*-\s*(\d{4})', time_text)
                    if time_match:
                        t_start = time_match.group(1)[:2] + ":" + time_match.group(1)[2:]
                        t_end = time_match.group(2)[:2] + ":" + time_match.group(2)[2:]
                        day = day_text.replace(' ', '').replace('\n', '')
                        
                        sections.append({
                            "sec": sec_text,
                            "day": day,
                            "time_start": t_start,
                            "time_end": t_end
                        })
        
        if course_code not in schedule_data[term]:
            schedule_data[term][course_code] = {"sections": []}
        schedule_data[term][course_code]["sections"].extend(sections)
        
    with open(MOCK_SCHEDULE_PATH, 'w', encoding='utf-8') as f:
        json.dump(schedule_data, f, ensure_ascii=False, indent=2)
    print(f"Schedule data saved to {MOCK_SCHEDULE_PATH}")

def parse_pdf_files():
    pdf_files = glob.glob(os.path.join(RAW_DATA_DIR, "*.pdf"))
    print(f"Found {len(pdf_files)} PDF files to process...")
    
    if not os.path.exists(CATALOG_PATH):
        print("Catalog not found.")
        return
    with open(CATALOG_PATH, 'r', encoding='utf-8') as f:
        catalog = json.load(f)
        
    course_dict = {c["course_code"]: c for c in catalog["courses"]}
    
    for filepath in pdf_files:
        basename = os.path.basename(filepath)
        course_code = basename.replace(".pdf", "").split("-")[0]
        
        if course_code not in course_dict:
            continue
            
        try:
            reader = PyPDF2.PdfReader(filepath)
            text = "".join([page.extract_text() for page in reader.pages])
            
            pre_match = re.search(r'(?:เงื่อนไขที่ต้องผ่านก่อน|Prerequisite)[^\d]*(\d{6}(?:\s*และ\s*\d{6})*)', text, re.IGNORECASE)
            if pre_match:
                course_dict[course_code]["prerequisite"] = pre_match.group(1).strip()
            
        except Exception as e:
            print(f"Failed to read {filepath}: {e}")
            
    with open(CATALOG_PATH, 'w', encoding='utf-8') as f:
        json.dump(catalog, f, ensure_ascii=False, indent=2)
    print(f"Catalog updated with prerequisite info at {CATALOG_PATH}")

if __name__ == "__main__":
    parse_xls_files()
    parse_pdf_files()
