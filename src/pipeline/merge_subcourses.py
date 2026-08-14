import json

with open('/Users/memee/.gemini/antigravity/scratch/cmu_chatbot_poc/data/json_db/Minors.json', 'r', encoding='utf-8') as f:
    minors_db = json.load(f)

with open('/Users/memee/.gemini/antigravity/scratch/cmu_chatbot_poc/parsed_raw.json', 'r', encoding='utf-8') as f:
    raw_courses = json.load(f)

# Helper function to find a minor in minors_db
def find_minor(faculty_name_hint, minor_name_hint):
    minor_name_hint_clean = minor_name_hint.split('ยกเว้น')[0].split('(')[0].strip()
    
    # Custom overrides
    if "คณะนิติศาสตร์" in faculty_name_hint:
        return "กฎหมาย (Law)" # Law has only one minor, mapping LAGE, LAW, LAWS to it
    
    if "วิชาโทศิลปะการประกอบอาหาร" in minor_name_hint_clean:
        return "วิชาโทศิลปะการประกอบอาหาร (Culinary Arts)"
        
    if "ศิลปะการถ่ายภาพ" in minor_name_hint_clean:
        return "ศิลปการถ่ายภาพ (Photographic Art) [ปิดสอน ตั้งแต่ 1/2567 เป็นต้นไป]"
        
    if "จิตรกรรรมไทย" in minor_name_hint_clean:
        return "จิตรกรรมไทย (Thai Painting)"
        
    if "ประวัติศาสตร์สิลปะ" in minor_name_hint_clean:
        return "ประวัติศาสตร์ศิลปะ (Arts History)"
        
    if "ศิลปะภาพพิมพ์" in minor_name_hint_clean:
        return "ศิลปภาพพิมพ์ (Printmaking)"
        
    for fac in minors_db:
        if fac['faculty'] in faculty_name_hint or faculty_name_hint in fac['faculty']:
            for prog in fac['programs']:
                for m in prog['minors']:
                    db_minor_name = m['minor_name']
                    if minor_name_hint_clean.lower() in db_minor_name.lower():
                        return db_minor_name
                    # Try removing words
                    if minor_name_hint_clean.replace('วิชาโท', '').strip() in db_minor_name.lower():
                        return db_minor_name
    return None

# Merge process
for raw in raw_courses:
    faculty_context = raw['faculty_context']
    program_context = raw.get('program_context', "วิชาโทที่เปิดสอนสำหรับนักศึกษาทั่วไป")
    original_minor = raw['minor']['original_minor_name']
    
    matched_minor_name = find_minor(faculty_context, original_minor)
    
    if not matched_minor_name:
        print(f"Warning: Could not match minor '{original_minor}' in '{faculty_context}'")
        continue
        
    # Inject into minors_db
    matched = False
    for fac in minors_db:
        if fac['faculty'] in faculty_context or faculty_context in fac['faculty']:
            for prog in fac['programs']:
                for m in prog['minors']:
                    if m['minor_name'] == matched_minor_name:
                        matched = True
                        if 'courses_list' not in m:
                            m['courses_list'] = []
                            
                        # If it's Law, treat original_minor_name as a group
                        if "คณะนิติศาสตร์" in faculty_context:
                            new_group = {
                                "group_name": original_minor,
                                "courses": []
                            }
                            for g in raw['minor']['courses_list']:
                                new_group["courses"].extend(g["courses"])
                            m['courses_list'].append(new_group)
                        else:
                            m['courses_list'].extend(raw['minor']['courses_list'])
                            
    if not matched:
        print(f"Warning: Minor '{matched_minor_name}' matched but not injected for some reason in '{faculty_context}'.")

with open('/Users/memee/.gemini/antigravity/scratch/cmu_chatbot_poc/data/json_db/Minors.json', 'w', encoding='utf-8') as f:
    json.dump(minors_db, f, ensure_ascii=False, indent=2)

print("Merge completed successfully.")
