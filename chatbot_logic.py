import json
import re
import sys

def load_data(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        return json.load(f)

db = load_data('data/json_db/Minors.json')

# Alias maps for better keyword matching
faculty_aliases = {
    "วิศวะ": "คณะวิศวกรรมศาสตร์",
    "วิศวกรรม": "คณะวิศวกรรมศาสตร์",
    "เกษตร": "คณะเกษตรศาสตร์",
    "วิทย์": "คณะวิทยาศาสตร์",
    "วิทยา": "คณะวิทยาศาสตร์",
    "สถาปัตย์": "คณะสถาปัตยกรรมศาสตร์",
    "บัญชี": "คณะบริหารธุรกิจ",
    "บริหาร": "คณะบริหารธุรกิจ",
    "นิติ": "คณะนิติศาสตร์",
    "มนุษย์": "คณะมนุษยศาสตร์",
    "ศิลปวิจิตร": "คณะวิจิตรศิลป์",
    "วิจิตรศิลป์": "คณะวิจิตรศิลป์",
    "เศรษฐศาสตร์": "คณะเศรษฐศาสตร์",
    "อุตสาหกรรม": "คณะอุตสาหกรรมเกษตร",
    "แพทย์": "คณะแพทยศาสตร์",
    "พยาบาล": "คณะพยาบาลศาสตร์",
    "รัฐศาสตร์": "คณะรัฐศาสตร์และรัฐประศาสนศาสตร์",
}

def extract_faculty(text):
    for alias, full_name in faculty_aliases.items():
        if alias in text:
            return full_name
    for fac in db:
        if fac['faculty'].replace("คณะ", "") in text or fac['faculty'] in text:
            return fac['faculty']
    return None

def extract_minor(text):
    for fac in db:
        for prog in fac['programs']:
            for minor in prog['minors']:
                # Clean up the minor name for matching, e.g. "ภาษาอังกฤษ (English)" -> "ภาษาอังกฤษ"
                clean_name = minor['minor_name'].split('(')[0].strip()
                if clean_name in text:
                    return minor, fac['faculty']
                # Handle special case if they use English name
                if '(' in minor['minor_name'] and ')' in minor['minor_name']:
                    eng_name = minor['minor_name'].split('(')[1].split(')')[0].strip().lower()
                    if eng_name in text.lower():
                        return minor, fac['faculty']
    return None, None

def handle_query(query):
    query = query.strip()
    if not query:
        return ""
        
    faculty = extract_faculty(query)
    minor, minor_faculty = extract_minor(query)
    
    # Intent: List Minors in Faculty
    if ("มีอะไรบ้าง" in query or "มีวิชาโทอะไร" in query) and faculty:
        res = f"วิชาโทที่เปิดสอนใน {faculty} มีดังนี้:\n"
        for fac in db:
            if faculty in fac['faculty']:
                for prog in fac['programs']:
                    res += f"[{prog['program_name']}]\n"
                    for m in prog['minors']:
                        res += f"- {m['minor_name']}\n"
        return res
        
    # Intent: Ask about a specific minor
    if minor:
        # Intent: Requirements
        if "เงื่อนไข" in query or "เรียนยังไง" in query or "หน่วยกิต" in query or "บังคับ" not in query and "เลือก" not in query:
            res = f"วิชาโท: {minor['minor_name']} ({minor_faculty})\n"
            res += f"เงื่อนไข:\n{minor['requirements_th']}"
            return res
            
        # Intent: Get courses (บังคับ/เลือก)
        if "วิชาบังคับ" in query or "บังคับ" in query:
            if 'courses_list' in minor:
                res = f"วิชาบังคับของ {minor['minor_name']}:\n"
                found = False
                for group in minor['courses_list']:
                    if "บังคับ" in group['group_name']:
                        res += f"{group['group_name']}:\n"
                        res += ", ".join(group['courses']) + "\n"
                        found = True
                if not found:
                    res += "ไม่มีข้อมูลระบุเจาะจง หรือรหัสวิชาอาจรวมอยู่ในเงื่อนไขหลักครับ\n"
                return res
            else:
                return "ไม่มีข้อมูลรหัสวิชาย่อยสำหรับวิชาโทนี้ครับ"
                
        if "วิชาเลือก" in query or "เลือก" in query:
            if 'courses_list' in minor:
                res = f"วิชาเลือกของ {minor['minor_name']}:\n"
                found = False
                for group in minor['courses_list']:
                    if "เลือก" in group['group_name'] or group['group_name'] == "General":
                        res += f"{group['group_name']}:\n"
                        res += ", ".join(group['courses']) + "\n"
                        found = True
                if not found:
                    res += "ไม่มีข้อมูลระบุเจาะจง หรือรหัสวิชาอาจรวมอยู่ในเงื่อนไขหลักครับ\n"
                return res
            else:
                return "ไม่มีข้อมูลรหัสวิชาย่อยสำหรับวิชาโทนี้ครับ"
                
    return "ขออภัยครับ ไม่พบข้อมูลที่ตรงกับคำถาม กรุณาระบุชื่อคณะหรือชื่อวิชาโทให้ชัดเจน (เช่น 'วิชาโทคณะวิศวะมีอะไรบ้าง' หรือ 'เงื่อนไขวิชาโทบัญชี')"

def main():
    print("========================================")
    print("CMU Minor Chatbot POC (Keyword Matching)")
    print("พิมพ์คำถามที่ต้องการ หรือพิมพ์ 'exit' เพื่อออก")
    print("========================================")
    
    if len(sys.argv) > 1:
        # Direct query mode for testing
        query = " ".join(sys.argv[1:])
        print(f"Q: {query}")
        print("A:\n" + handle_query(query))
        return
        
    while True:
        try:
            query = input("\nQ: ")
            if query.lower() in ['exit', 'quit']:
                break
            response = handle_query(query)
            print("A:")
            print(response)
        except (KeyboardInterrupt, EOFError):
            break

if __name__ == "__main__":
    main()
