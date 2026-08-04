import json
import os
import google.genai as genai
from google.genai import types

from dotenv import load_dotenv

load_dotenv()

# Setup Gemini Client
# We use the new google-genai SDK
api_keys_str = os.environ.get("GEMINI_API_KEYS", "")
api_keys = api_keys_str.split(',') if api_keys_str else []
first_key = api_keys[0] if api_keys else os.environ.get("GEMINI_API_KEY")

client = genai.Client(api_key=first_key)
MODEL_ID = 'gemini-3.5-flash'

def get_track_conflicts(track_keyword: str, json_rel_path: str, term: str = "1/2568"):
    """
    Looks up the catalog for the specified track dynamically based on the student's program,
    and returns a summary string of available courses and any conflicts for a specific term.
    """
    base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    json_path = os.path.join(base_dir, json_rel_path)
    schedule_path = os.path.join(base_dir, "src", "logic_engine", "mock_schedule.json")
    
    try:
        with open(json_path, 'r', encoding='utf-8') as f:
            catalog = json.load(f)
        with open(schedule_path, 'r', encoding='utf-8') as f:
            full_schedule = json.load(f)
    except FileNotFoundError:
        return f"ขออภัยค่ะ ไม่พบฐานข้อมูลหลักสูตรที่ {json_rel_path}"

    schedule = full_schedule.get(term, {})

    # Filter courses
    track_courses = []
    for c in catalog['courses']:
        cat = c.get('category_or_track', '')
        if track_keyword.lower() in cat.lower():
            track_courses.append(c)

    available_courses = [c for c in track_courses if c['course_code'] in schedule]
    
    if not available_courses:
        return f"เทอม {term} ยังไม่มีวิชาในหมวด {track_keyword} เปิดสอนในตารางจำลองเลยค่ะ"

    response = f"เทอม {term} เปิดสอน {len(available_courses)} วิชา ได้แก่:\n"
    for c in available_courses:
        response += f"- {c['course_code']} {c['course_name_th'] or c['course_name_en']}\n"
        for sec in schedule[c['course_code']]['sections']:
            response += f"  Sec {sec['sec']}: {sec['day']} {sec['time_start']}-{sec['time_end']}\n"

    # Check conflicts
    conflicts = []
    def to_minutes(t):
        h, m = map(int, t.split(':'))
        return h * 60 + m

    for i in range(len(available_courses)):
        for j in range(i + 1, len(available_courses)):
            c1 = available_courses[i]
            c2 = available_courses[j]
            for sec1 in schedule[c1['course_code']]['sections']:
                for sec2 in schedule[c2['course_code']]['sections']:
                    days1 = set(sec1['day'].split(','))
                    days2 = set(sec2['day'].split(','))
                    if days1.intersection(days2):
                        s1, e1 = to_minutes(sec1['time_start']), to_minutes(sec1['time_end'])
                        s2, e2 = to_minutes(sec2['time_start']), to_minutes(sec2['time_end'])
                        if s1 < e2 and s2 < e1:
                            conflicts.append(f"❌ ชนกัน! {c1['course_code']} (Sec {sec1['sec']}) กับ {c2['course_code']} (Sec {sec2['sec']}) เวลา {sec1['day']} {sec1['time_start']}-{sec1['time_end']}")

    if conflicts:
        response += "\n⚠️ ข้อควรระวัง:\n" + "\n".join(conflicts)
    else:
        response += "\n✅ ทุกวิชาเวลาไม่ชนกัน สามารถลงพร้อมกันได้เลยค่ะ!"

    return response

def generate_with_fallback(contents, sys_instruct=None, mime_type=None):
    """Try to generate content using available API keys until one works."""
    api_keys_str = os.environ.get("GEMINI_API_KEYS", "")
    api_keys = api_keys_str.split(',') if api_keys_str else [os.environ.get("GEMINI_API_KEY")]
    
    last_error = None
    for key in api_keys:
        if not key:
            continue
        
        try:
            temp_client = genai.Client(api_key=key.strip())
            
            kwargs = {"model": MODEL_ID, "contents": contents}
            if sys_instruct or mime_type:
                config = {}
                if sys_instruct:
                    config["system_instruction"] = sys_instruct
                if mime_type:
                    config["response_mime_type"] = mime_type
                kwargs["config"] = types.GenerateContentConfig(**config)
                
            response = temp_client.models.generate_content(**kwargs)
            return response.text
            
        except Exception as e:
            last_error = e
            # If it's a 429, try the next key. Otherwise, maybe break.
            if "429" in str(e):
                continue
            else:
                raise e
    
    raise last_error

def process_message(user_message: str, student_profile: dict = None) -> str:
    """
    Main brain function: Takes user text and student profile, and acts as a Smart Advising Engine.
    """
    if not student_profile:
        # Fallback for old tests
        return "System error: No student profile provided."

    prog_data = student_profile.get("program_data", {})
    json_path = prog_data.get("json_path", "")
    md_path = prog_data.get("md_path", "")
    major_tracks = prog_data.get("major_tracks", [])
    tracks_str = ", ".join(major_tracks) if major_tracks else "ไม่มีการแบ่งหมวดวิชาเฉพาะ"
    
    # Read the markdown conditions if they exist
    conditions_text = ""
    if md_path:
        base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        full_md_path = os.path.join(base_dir, md_path)
        try:
            with open(full_md_path, 'r', encoding='utf-8') as f:
                conditions_text = f.read()
        except:
            pass

    sys_instruct = f"""
    คุณคือ "Smart Advising Engine" ผู้ช่วยแนะนำการลงทะเบียนเรียนของมหาวิทยาลัยเชียงใหม่
    
    ข้อมูลโปรไฟล์นักศึกษาปัจจุบัน (Context):
    - คณะ: {student_profile.get('faculty')}
    - สาขา: {student_profile.get('program')}
    - หมวดวิชาเฉพาะที่มีในสาขานี้ (Available Tracks): {tracks_str}
    - ทักษะภาษาอังกฤษ (CEFR): {student_profile.get('cefr_level')}
    - ทางเลือกแผนการเรียน: {student_profile.get('pathway')}
    
    กฎกติกาและเงื่อนไขหลักสูตรของสาขานี้ (Rules):
    {conditions_text}
    
    หน้าที่ของคุณคือต้องวิเคราะห์คำถามของนักศึกษา และตอบกลับเป็น JSON FORMAT เท่านั้น ห้ามมีข้อความอื่นปน
    1. หากนักศึกษาถามเกี่ยวกับการเช็คตารางเรียนชนกัน หรือถามเกี่ยวกับวิชาเลือก หมวดวิชา หรือกลุ่มความสนใจ (เช่น "เอกคอม", "สาย AI", "วิศวะซอฟต์แวร์") ให้คุณวิเคราะห์ว่าคำถามนั้นตรงกับหมวดวิชาใดใน "Available Tracks" ด้านบนมากที่สุด แล้วดึงชื่อหมวดวิชาภาษาอังกฤษที่ถูกต้องเป๊ะๆ ออกมา แล้วตอบเป็น JSON:
       {{"intent": "check_track", "track": "ชื่อหมวดวิชาภาษาอังกฤษที่อยู่ใน Available Tracks"}}
       
    2. หากนักศึกษาถามเกี่ยวกับ **เงื่อนไขภาษาอังกฤษ (CEFR)**, **แผนการเรียน (Minor/No Minor)** หรือ **หน่วยกิต (300/400 level)** ให้คุณใช้ "ข้อมูลโปรไฟล์นักศึกษาปัจจุบัน" มาเทียบกับ "กฎกติกาและเงื่อนไขหลักสูตร" แล้วตอบให้คำปรึกษาเป็น JSON:
       {{"intent": "advising", "reply": "คำตอบให้คำปรึกษาที่แม่นยำตามกฎ"}}
       
    3. หากเป็นคำถามทั่วไป:
       {{"intent": "general", "reply": "ข้อความตอบกลับภาษาไทย"}}
    """

    try:
        response_text = generate_with_fallback(
            contents=user_message,
            sys_instruct=sys_instruct,
            mime_type="application/json"
        )
        
        # Clean up possible markdown wrappers
        clean_json = response_text.strip()
        if clean_json.startswith("```json"):
            clean_json = clean_json[7:]
        elif clean_json.startswith("```"):
            clean_json = clean_json[3:]
        if clean_json.endswith("```"):
            clean_json = clean_json[:-3]
            
        data = json.loads(clean_json.strip())
        
        if data.get("intent") == "check_track":
            track = data.get("track", "")
            logic_result = get_track_conflicts(track, json_path)
            
            format_prompt = f"นักศึกษาโปรไฟล์ {student_profile.get('program')} ถามว่า: '{user_message}'\nข้อมูลจากระบบตารางเรียนคือ:\n{logic_result}\n\nกรุณาสรุปข้อมูลนี้ให้นักศึกษาฟังแบบเป็นกันเองและเข้าใจง่าย (ไม่ต้องเติมข้อมูลที่ไม่มีในระบบ)"
            
            final_response = generate_with_fallback(contents=format_prompt)
            return final_response
        
        elif data.get("intent") == "advising" or data.get("intent") == "general":
            return data.get("reply", "ระบบกำลังประมวลผลคำแนะนำ...")
            
    except Exception as e:
        print(f"Error in AI processing: {e}")
        return f"ขออภัยค่ะ ระบบประมวลผลมีปัญหาชั่วคราว: {str(e)}"

if __name__ == "__main__":
    pass
