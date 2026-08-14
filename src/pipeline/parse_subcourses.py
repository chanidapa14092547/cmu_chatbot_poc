import json
import re

def parse_text_file(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        lines = f.readlines()
        
    data = []
    curr_faculty = None
    curr_program = "วิชาโทที่เปิดสอนสำหรับนักศึกษาทั่วไป"
    curr_minor = None
    curr_group = None
    
    for line in lines:
        line = line.rstrip('\n')
        stripped = line.strip()
        if not stripped: continue
        
        # Check if faculty (Starts with "คณะ" or "วิทยาลัย")
        if (stripped.startswith("คณะ") or stripped.startswith("วิทยาลัย")) and not stripped.startswith("-") and not stripped.startswith("o") and not stripped.startswith("•") and not re.match(r'^\d+\.', stripped):
            curr_faculty = stripped
            curr_program = "วิชาโทที่เปิดสอนสำหรับนักศึกษาทั่วไป"
            curr_minor = None
            curr_group = None
            continue
            
        if stripped.startswith("วิชาโททีเปิดสอน") or stripped.startswith("วิชาโทที่เปิดสอน") or stripped.startswith("วิชาโทสำหรับ"):
            curr_program = stripped
            curr_minor = None
            curr_group = None
            continue
            
        # Check if minor (Starts with number e.g. "1. ")
        m_minor = re.match(r'^\d+\.\s*(.+)', stripped)
        if m_minor and not line.startswith((' ', '\t', '-')):
            curr_minor = {
                "original_minor_name": m_minor.group(1).strip(),
                "courses_list": []
            }
            if curr_faculty:
                data.append({
                    "faculty_context": curr_faculty,
                    "program_context": curr_program,
                    "minor": curr_minor
                })
            curr_group = None
            continue
            
        # Check if group (Starts with "- ")
        if stripped.startswith("-"):
            group_name = stripped[1:].strip()
            # If it looks like a course code and has no words
            if re.match(r'^[\w\d\s,]+$', group_name) and not "วิชา" in group_name and not "กลุ่ม" in group_name:
                if not curr_group or curr_group["group_name"] != "General":
                    curr_group = {"group_name": "General", "courses": []}
                    if curr_minor:
                        curr_minor["courses_list"].append(curr_group)
                curr_group["courses"].append(group_name)
            else:
                curr_group = {"group_name": group_name, "courses": []}
                if curr_minor:
                    curr_minor["courses_list"].append(curr_group)
            continue
            
        # Check if course inside group (Starts with "o " or "• ")
        if stripped.startswith("o ") or stripped.startswith("• "):
            course = stripped[2:].strip()
            if not curr_group:
                curr_group = {"group_name": "General", "courses": []}
                if curr_minor:
                    curr_minor["courses_list"].append(curr_group)
            curr_group["courses"].append(course)

    return data

d1 = parse_text_file('/Users/memee/.gemini/antigravity/scratch/cmu_chatbot_poc/details1_utf8.txt')
d2 = parse_text_file('/Users/memee/.gemini/antigravity/scratch/cmu_chatbot_poc/details2_utf8.txt')

with open('/Users/memee/.gemini/antigravity/scratch/cmu_chatbot_poc/parsed_raw.json', 'w', encoding='utf-8') as f:
    json.dump(d1 + d2, f, ensure_ascii=False, indent=2)

print("Parsed raw courses data successfully.")
