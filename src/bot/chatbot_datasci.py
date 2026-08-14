import json
import re
import sys

def load_data(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        return json.load(f)

print("Loading Data Science Curriculum (2567) and Minors Database...")
major_db = load_data('data/json_db/Faculty of Science/Bachelor of Science Program in Data Science (2567).json')
minor_db = load_data('data/json_db/Minors.json')

# ================= CORE FUNCTIONS =================

def get_course_info(course_code):
    for c in major_db['courses']:
        if c['course_code'] == course_code:
            return c
    return None

def get_major_basic():
    courses = []
    for c in major_db['courses']:
        if "Basic Courses" in c['category_or_track'] or "Basic Science" in c['category_or_track']:
            courses.append(f"{c['course_code']} {c['course_name_th']} ({c.get('course_name_en', '')})")
    return "รายชื่อวิชาบังคับพื้นฐานสำหรับ Data Science (Basic Courses):\n" + "\n".join(courses)

def get_major_compulsory():
    courses = []
    for c in major_db['courses']:
        if "Field of Specialization / Major / Compulsory Courses" in c['category_or_track']:
            courses.append(f"{c['course_code']} {c['course_name_th']} ({c.get('course_name_en', '')})")
    return "สำหรับนักศึกษา Data Science (2567) วิชาเอกบังคับมีดังนี้ครับ:\n" + "\n".join(courses)

def get_major_electives():
    groups = {
        "กลุ่ม Data analytics using computational modeling (เน้นคอมพิวเตอร์)": [],
        "กลุ่ม Data analytics using mathematical modeling (เน้นคณิตศาสตร์)": [],
        "กลุ่ม Statistical data analytics (เน้นสถิติ)": [],
        "กลุ่มอื่นๆ (ทั่วไป)": []
    }
    for c in major_db['courses']:
        if "Major Elective Courses" in c['category_or_track']:
            track = c['category_or_track']
            info = f"{c['course_code']} {c['course_name_th']} ({c.get('course_name_en', '')})"
            assigned = False
            if "computational modeling" in track:
                groups["กลุ่ม Data analytics using computational modeling (เน้นคอมพิวเตอร์)"].append(info)
                assigned = True
            if "mathematical modeling" in track:
                groups["กลุ่ม Data analytics using mathematical modeling (เน้นคณิตศาสตร์)"].append(info)
                assigned = True
            if "Statistical data analytics" in track:
                groups["กลุ่ม Statistical data analytics (เน้นสถิติ)"].append(info)
                assigned = True
            if not assigned:
                groups["กลุ่มอื่นๆ (ทั่วไป)"].append(info)
                
    res = "สำหรับนักศึกษา Data Science (2567) วิชาเอกเลือก (Major Elective) แบ่งตามกลุ่มมีดังนี้ครับ:\n\n"
    for g, courses in groups.items():
        if courses:
            res += f"[{g}]\n"
            for course in courses:
                res += f"- {course}\n"
            res += "\n"
    return res.strip()

def get_course_prereq(course_code):
    c = get_course_info(course_code)
    if c:
        prereqs = c.get('prerequisites', [])
        raw = c.get('condition_raw', 'None')
        if not prereqs or prereqs == ["None"]:
            return f"วิชา {course_code} {c['course_name_en']} ไม่มีวิชาบังคับก่อน (Prerequisite) ครับ สามารถลงเรียนได้เลย"
        else:
            return f"วิชา {course_code} {c['course_name_en']} ต้องผ่านวิชาดังต่อไปนี้ก่อน:\n- {', '.join(prereqs)}\n(เงื่อนไขเต็ม: {raw})"
    return f"ขออภัย ไม่พบข้อมูลวิชา {course_code} ในหลักสูตร Data Science (2567)"

def check_if_compulsory(course_code):
    c = get_course_info(course_code)
    if c:
        if "Compulsory" in c['category_or_track'] or "Basic Courses" in c['category_or_track']:
            return f"ใช่ครับ วิชา {course_code} {c['course_name_en']} เป็นวิชาบังคับ (หมวด: {c['category_or_track'].split('/')[-1].strip()})"
        else:
            return f"ไม่ใช่ครับ วิชา {course_code} {c['course_name_en']} ไม่ใช่วิชาเอกบังคับ (หมวด: {c['category_or_track'].split('/')[-1].strip()})"
    return f"ไม่พบข้อมูลวิชา {course_code}"

# ================= NEW FUNCTIONS (GE, MINOR, STUDY PLAN, CREDITS) =================

def get_ge_courses(group_keyword):
    courses = []
    for c in major_db['courses']:
        if "General Education" in c['category_or_track']:
            if not group_keyword or group_keyword.lower() in c['category_or_track'].lower():
                courses.append(f"{c['course_code']} {c['course_name_th']} ({c.get('course_name_en', '')}) - {c['category_or_track'].split('/')[-1].strip()}")
    
    if not courses:
        return f"ไม่พบวิชา GE ในกลุ่ม '{group_keyword}' ครับ"
        
    title = f"กลุ่ม {group_keyword}" if group_keyword else "ทั้งหมด"
    return f"วิชาศึกษาทั่วไป (GE) {title} มีดังนี้ครับ:\n" + "\n".join(courses)

def get_minors_by_faculty(faculty_keyword):
    minors = []
    fac_name = ""
    for fac in minor_db:
        if faculty_keyword in fac['faculty']:
            fac_name = fac['faculty']
            for prog in fac['programs']:
                for m in prog['minors']:
                    minors.append(f"- {m['minor_name']}")
    if minors:
        return f"วิชาโทที่เปิดสอนใน{fac_name} มีดังนี้ครับ:\n" + "\n".join(minors)
    return f"ไม่พบข้อมูลวิชาโทของคณะที่เกี่ยวกับ '{faculty_keyword}' ครับ"

def check_minor_restriction(minor_keyword):
    for fac in minor_db:
        for prog in fac['programs']:
            for m in prog['minors']:
                clean_name = m['minor_name'].split('(')[0].strip()
                if minor_keyword.lower() in clean_name.lower():
                    reqs = m['requirements_th']
                    if "ยกเว้น" in reqs and "วิทยา" in reqs:
                        return f"วิชาโท: {m['minor_name']} ({fac['faculty']})\n🛑 คำตอบ: **มีข้อห้าม/ข้อยกเว้นครับ!**\nนักศึกษา Data Science (คณะวิทยาศาสตร์) อาจไม่สามารถลงเรียนวิชาโทนี้ได้ทั้งหมด หรือมีเงื่อนไขพิเศษ โปรดอ่านรายละเอียดด้านล่าง:\n\n{reqs}"
                    else:
                        return f"วิชาโท: {m['minor_name']} ({fac['faculty']})\n✅ คำตอบ: **ไม่มีข้อห้าม/ข้อยกเว้นสำหรับคณะวิทยาศาสตร์ครับ**\nสามารถลงเรียนได้ตามเงื่อนไขปกติ:\n\n{reqs}"
    return f"ไม่พบข้อมูลวิชาโทที่เกี่ยวกับ '{minor_keyword}'"

def get_study_plan(year, semester):
    key = f"year_{year}_semester_{semester}"
    plan = major_db.get('study_plan', {}).get(key)
    if not plan:
        return f"ไม่พบแผนการศึกษาสำหรับ ปี {year} เทอม {semester} ครับ"
        
    res = f"แผนการศึกษาแนะนำสำหรับ ปี {year} เทอม {semester}:\n"
    for item in plan:
        if isinstance(item, str):
            c = get_course_info(item)
            if c:
                res += f"- {item} {c['course_name_th']} ({c.get('course_name_en', '')})\n"
            else:
                res += f"- {item} (ไม่พบข้อมูลชื่อวิชา)\n"
        elif isinstance(item, dict):
            if 'category_placeholder' in item:
                res += f"- เลือกเรียนวิชาในกลุ่ม: {item['category_placeholder'].split('/')[-1].strip()} ({item.get('credits_required', '?')} หน่วยกิต)\n"
            elif 'course_options' in item:
                res += f"- เลือกเรียนระหว่าง: {', '.join(item['course_options'])} ({item.get('credits_required', '?')} หน่วยกิต)\n"
    return res.strip()

def get_credit_summary():
    return """สำหรับหลักสูตร Data Science (2567) มีโครงสร้างหน่วยกิตดังนี้ครับ:
- จำนวนหน่วยกิตรวมตลอดหลักสูตร: ไม่น้อยกว่า 129 หน่วยกิต
- หมวดวิชาศึกษาทั่วไป (GE): ไม่น้อยกว่า 30 หน่วยกิต
- หมวดวิชาเฉพาะ (วิชาแกน, บังคับ, เลือก, วิชาโท): ไม่น้อยกว่า 93 หน่วยกิต
- หมวดวิชาเลือกเสรี (Free Elective): ไม่น้อยกว่า 6 หน่วยกิต"""

def get_free_elective_info():
    return """สำหรับ 'วิชาเลือกเสรี' (Free Elective) ในหลักสูตร Data Science:
คุณต้องเก็บให้ได้ **ไม่น้อยกว่า 6 หน่วยกิต** ครับ
โดยสามารถเลือกเรียนรายวิชาใดก็ได้ที่เปิดสอนในมหาวิทยาลัยเชียงใหม่ (ยกเว้นวิชาที่ถูกกำหนดว่าห้ามนับเป็นเลือกเสรี)"""

# ================= QUERY ROUTER =================

def handle_query(query):
    query = query.strip()
    if not query:
        return ""
        
    # 1. EXTRACT COURSE ENTITIES
    course_codes = re.findall(r'\d{6}', query)
    if not course_codes:
        for c in major_db['courses']:
            eng_name = c.get('course_name_en', '').strip()
            if len(eng_name) > 4 and eng_name.lower() in query.lower():
                course_codes.append(c['course_code'])
    
    # 2. COURSE SPECIFIC INTENT (High Priority)
    if course_codes:
        res = ""
        course_codes = list(dict.fromkeys(course_codes))
        
        if "เอกบังคับไหม" in query or "เป็นวิชาบังคับ" in query:
            for code in course_codes:
                res += check_if_compulsory(code) + "\n\n"
            return res.strip()
            
        if "ผ่าน" in query or "ก่อน" in query or "ลง" in query or "เรียน" in query or "prereq" in query.lower() or "รหัสอะไร" in query:
            for code in course_codes:
                res += get_course_prereq(code) + "\n\n"
            return res.strip()
            
        # Fallback if just mentioning a course (like "จัดอยู่ในหมวดไหน")
        for code in course_codes:
            c = get_course_info(code)
            res += f"วิชา {code} {c['course_name_th']} ({c['course_name_en']}) - หมวด: {c['category_or_track']}\n"
        return res.strip()

    # 3. STUDY PLAN INTENT
    if "ปี" in query and "เทอม" in query:
        year_match = re.search(r'ปี\s*(\d)', query)
        sem_match = re.search(r'เทอม\s*(\d)', query)
        if year_match and sem_match:
            return get_study_plan(year_match.group(1), sem_match.group(1))

    # 4. CREDIT SUMMARY & FREE ELECTIVE INTENT
    if "เลือกเสรี" in query:
        return get_free_elective_info()
    if "กี่หน่วยกิต" in query or "โครงสร้างหน่วยกิต" in query or "รวมกี่" in query:
        return get_credit_summary()

    # 5. GE INTENT
    if "ge" in query.lower() or "ศึกษาทั่วไป" in query or "หมวดวิชาศึกษาทั่วไป" in query:
        if "active citizen" in query.lower():
            return get_ge_courses("Active Citizen")
        if "learner person" in query.lower():
            return get_ge_courses("Learner Person")
        if "innovative co-creator" in query.lower():
            return get_ge_courses("Innovative Co-creator")
        return get_ge_courses("") # All GE

    # 6. GENERAL MAJOR INTENT
    if "บังคับพื้นฐาน" in query or "วิชาแกน" in query or "วิชาพื้นฐาน" in query:
        return get_major_basic()
        
    if "วิชาเอกบังคับ" in query or ("เอก" in query and "บังคับ" in query):
        return get_major_compulsory()
        
    if "วิชาเลือกเอก" in query or ("เลือก" in query and "เอก" in query) or "วิชาเอกเลือก" in query:
        return get_major_electives()
        
    # 7. MINOR INTENT
    if "คณะ" in query and "โท" in query and "อะไร" in query:
        # Extract faculty name roughly
        facs = ["วิทยาศาสตร์", "วิศวกรรม", "บริหาร", "มนุษย", "อุตสาหกรรม", "สังคม"]
        for f in facs:
            if f in query:
                return get_minors_by_faculty(f)

    if "โท" in query:
        # check if it's asking for restrictions
        is_checking_restriction = "ห้าม" in query or "ยกเว้น" in query or "ได้ไหม" in query
        
        for fac in minor_db:
            for prog in fac['programs']:
                for m in prog['minors']:
                    clean_name = m['minor_name'].split('(')[0].strip()
                    # special case: if user says "วิชาโทสถิติ" and clean_name is "สถิติ"
                    if clean_name in query:
                        if is_checking_restriction:
                            return check_minor_restriction(clean_name)
                        else:
                            return check_minor_restriction(clean_name) # Using restriction check as default anyway as it prints reqs too
                            
    return "ขออภัยครับ คำถามไม่ชัดเจน ลองถามเกี่ยวกับวิชาเอก (เช่น 'วิชาเอกบังคับมีอะไรบ้าง'), แผนการเรียน ('ปี 1 เทอม 1 เรียนอะไร'), หรือวิชาโท (เช่น 'เงื่อนไขโทบัญชี') ดูนะครับ"

def main():
    print("==================================================")
    print("CMU Chatbot POC: Data Science (2567) Context V2")
    print("ระบบจำลองว่าคุณคือ นักศึกษาสาขา Data Science รหัส 67")
    print("พิมพ์คำถามที่ต้องการ หรือพิมพ์ 'exit' เพื่อออก")
    print("==================================================")
    
    if len(sys.argv) > 1:
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
            print("A:\n" + response)
        except (KeyboardInterrupt, EOFError):
            break

if __name__ == "__main__":
    main()
