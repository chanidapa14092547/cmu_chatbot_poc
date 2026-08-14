import os
import glob
import re
import json

def extract_course_schedule(directory):
    files = glob.glob(os.path.join(directory, "*.xls"))
    schedule_data = []

    for filepath in files:
        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()

        course_match = re.search(r'>\s*(\d{6})\s*-', content)
        if not course_match:
            filename = os.path.basename(filepath)
            course_code = filename.split('-')[0].replace('.xls', '')
        else:
            course_code = course_match.group(1)

        rows = re.findall(r'<tr>(.*?)</tr>', content, re.DOTALL)
        
        for row in rows[3:]:
            row_text = row.replace('</td>', '|||')
            row_text = re.sub(r'<[^>]+>', ' ', row_text)
            row_text = row_text.replace('&nbsp;', ' ')
            
            cells = [re.sub(r'\s+', ' ', c).strip() for c in row_text.split('|||')]
            
            if len(cells) < 11:
                continue
                
            title = cells[2]
            lec_sec = cells[3]
            lab_sec = cells[4]
            lec_cred = cells[5]
            lab_cred = cells[6]
            day = cells[7]
            time = cells[8].replace('- ', '-').strip()
            room = cells[9]
            lecturer = cells[10]
            
            if not lec_sec or lec_sec == '000':
                continue
                
            schedule_data.append({
                "course_code": course_code,
                "course_name": title,
                "section": lec_sec,
                "day": day,
                "time": time,
                "room": room,
                "lecturer": lecturer
            })

    return schedule_data

def main():
    if not os.path.exists("data/json_db"):
        os.makedirs("data/json_db")
        
    schedule = extract_course_schedule("DS")
    out_path = "data/json_db/schedule_2567.json"
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(schedule, f, ensure_ascii=False, indent=4)
    print(f"✅ Extracted {len(schedule)} sections and saved to {out_path}.")

if __name__ == "__main__":
    main()
