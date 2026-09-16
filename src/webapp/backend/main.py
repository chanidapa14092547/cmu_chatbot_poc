import os
import sys
import json
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from google import genai
from google.genai import types
import os
from dotenv import load_dotenv

base_dir_for_env = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
load_dotenv(os.path.join(base_dir_for_env, '.env'))

app = FastAPI(title="CMU Smart Scheduler API")

# Enable CORS for the frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # For development
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Data Loading ---
def load_data():
    base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
    # base_dir should be scratch/cmu_chatbot_poc
    major_path = os.path.join(base_dir, 'data', 'json_db', 'Faculty of Science', 'Bachelor of Science Program in Data Science (2567).json')
    minor_path = os.path.join(base_dir, 'data', 'json_db', 'Minors.json')
    schedule_path = os.path.join(base_dir, 'data', 'json_db', 'schedule_2567.csv')
    
    try:
        with open(major_path, 'r', encoding='utf-8') as f:
            major_db = f.read()
            major_json = json.loads(major_db)
        with open(minor_path, 'r', encoding='utf-8') as f:
            minor_db = f.read()
            minor_json = json.loads(minor_db)
        with open(schedule_path, 'r', encoding='utf-8') as f:
            schedule_db = f.read()
            
        return major_db, major_json, minor_db, minor_json, schedule_db
    except Exception as e:
        print(f"Error loading data: {e}")
        return None, None, None, None, None

MAJOR_DB_STR, MAJOR_JSON, MINOR_DB_STR, MINOR_JSON, SCHEDULE_DB_STR = load_data()

ALL_CLIENTS = []
def init_gemini_and_model():
    keys_str = os.environ.get("GEMINI_API_KEYS", "")
    single_key = os.environ.get("GEMINI_API_KEY", "")
    all_keys = [single_key] if single_key else []
    if keys_str:
        all_keys.extend(keys_str.split(","))
        
    for key in all_keys:
        key = key.strip()
        if not key: continue
        try:
            ALL_CLIENTS.append(genai.Client(api_key=key))
        except Exception:
            pass
    return "gemini-3.6-flash"

MODEL_NAME = init_gemini_and_model()

# --- Endpoints ---
@app.get("/api/ping")
def ping():
    return {"status": "ok"}

@app.get("/api/major-tracks")
def get_major_tracks():
    if not MAJOR_JSON:
        raise HTTPException(status_code=500, detail="Data not loaded")
    return {"tracks": MAJOR_JSON.get("major_tracks", [])}

@app.get("/api/courses")
def get_courses():
    if not MAJOR_JSON:
        raise HTTPException(status_code=500, detail="Data not loaded")
    return {"courses": MAJOR_JSON.get("courses", [])}

@app.get("/api/minors")
def get_minors():
    if not MINOR_JSON:
        raise HTTPException(status_code=500, detail="Data not loaded")
    all_minors = []
    minor_courses_map = {}
    for fac in MINOR_JSON:
        for prog in fac.get("programs", []):
            for m in prog.get("minors", []):
                m_name = m.get("minor_name", "")
                if m_name not in minor_courses_map:
                    all_minors.append(m_name)
                    minor_courses_map[m_name] = []
                for g in m.get("courses_list", []):
                    for c in g.get("courses", []):
                        if str(c).isdigit() and len(str(c)) == 6:
                            minor_courses_map[m_name].append(str(c))
    
    # Remove duplicates from lists
    for m in minor_courses_map:
        minor_courses_map[m] = list(set(minor_courses_map[m]))
        
    return {"minors": all_minors, "minor_courses_map": minor_courses_map}

@app.get("/api/study-plan/{year}/{term}")
def get_study_plan(year: int, term: int):
    if not MAJOR_JSON:
        raise HTTPException(status_code=500, detail="Data not loaded")
    plan_key = f"year_{year}_semester_{term}"
    study_plan = MAJOR_JSON.get("study_plan", {})
    return {"plan": study_plan.get(plan_key, [])}

@app.get("/api/offered-courses")
def get_offered_courses():
    if not SCHEDULE_DB_STR:
        raise HTTPException(status_code=500, detail="Data not loaded")
    
    offered = {}
    for line in SCHEDULE_DB_STR.splitlines()[1:]:
        if line.strip():
            parts = line.split('|')
            if len(parts) > 1:
                offered[parts[0].strip()] = parts[1].strip()
    return {"courses": offered}

class ChatRequest(BaseModel):
    message: str
    history: list = [] # list of dicts {"role": "user"|"assistant", "content": "..."}

import re

def get_relevant_schedule(text, schedule_str):
    course_codes = set(re.findall(r'\b\d{6}\b', text))
    if not course_codes:
        return "No relevant courses found in the conversation."
    
    lines = schedule_str.splitlines()
    header = lines[0] if lines else ""
    filtered_lines = [header]
    
    for line in lines[1:]:
        parts = line.split('|')
        if len(parts) > 0 and parts[0].strip() in course_codes:
            filtered_lines.append(line)
            
    return "\n".join(filtered_lines)

@app.post("/api/chat")
def chat(req: ChatRequest):
    if not ALL_CLIENTS or not MODEL_NAME:
        raise HTTPException(status_code=500, detail="Gemini clients not initialized")
        
    # Extract relevant schedule based on mentioned courses
    all_text = req.message
    for msg in req.history:
        all_text += " " + msg.get("content", "")
    
    relevant_schedule = get_relevant_schedule(all_text, SCHEDULE_DB_STR)
    
    system_instruction = f"""คุณคือผู้ช่วยอัจฉริยะ (Chatbot) ให้คำปรึกษาด้านวิชาการสำหรับนักศึกษาหลักสูตร 'วิทยาการข้อมูล (Data Science) ปี 2567' คณะวิทยาศาสตร์ มหาวิทยาลัยเชียงใหม่
หน้าที่ของคุณคือตอบคำถามนักศึกษาเกี่ยวกับการลงทะเบียนเรียน หมวดวิชา วิชาบังคับ วิชาเลือก วิชาโท แผนการศึกษา เงื่อนไขต่างๆ และ ตารางเรียน โดยอ้างอิงจากฐานข้อมูล JSON ด้านล่างนี้เท่านั้น
เวลาตอบ ให้เน้นตอบอย่างกระชับ ตรงประเด็น เป็นทางการและสุภาพ
**กฎเหล็กเรื่องการจัดตารางเรียน (STRICT RULE):** 
1. หากผู้ใช้ระบุชื่อวิชาเลือกและเงื่อนไขเวลามาให้ครบถ้วนแล้ว (เช่น ส่งมาจากฟอร์ม) ให้คุณลุยจัดตารางแบบ Chain-of-Thought ได้เลย **ห้าม** ถามเซ้าซี้ซ้ำอีก!
2. แต่ถ้าผู้ใช้ระบุวิชาเลือกมาไม่ครบ หรือปล่อยว่างไว้ บอท **ต้องหยุด** และถามกลับดังนี้:
   - ตรวจสอบจากโครงสร้างหลักสูตรว่าเทอมนั้นต้องลงวิชาเลือกหมวดอะไรบ้าง
   - **สำคัญมาก:** คุณต้องดึง "รายชื่อวิชา และ รหัสวิชา" ที่อยู่ในหมวดนั้นๆ จาก JSON มาลิสต์เป็นตัวอย่างให้ผู้ใช้ดู (อย่างน้อย 3-5 วิชา) ห้ามบอกแค่ชื่อหมวดลอยๆ เด็ดขาด!
   - (หมายเหตุ: ถ้าหมวดที่ขาดคือ "Free Electives (วิชาเลือกเสรี)" ให้แนะนำวิชาที่น่าสนใจทั่วไปได้เลย แต่ห้ามเขียนสับสนหรือใช้ชื่อปนกับหมวด "GE Electives (วิชาศึกษาทั่วไป)" เด็ดขาด เพราะมันคือคนละหมวดกัน)
   - "มีเงื่อนไขเวลาไหมครับ เช่น ไม่อยากเรียน 8 โมงเช้า หรืออยากว่างวันไหนเป็นพิเศษ?"
3. ตอนจัดตาราง บอท **ต้องคิดวิเคราะห์หาเซคชั่นที่ไม่ชนกันทีละขั้นตอน (Chain of Thought)** โดยพิมพ์อธิบายทีละบรรทัดว่าเวลาชนไหมก่อนเสมอ ห้ามลักไก่เอาเซค 001 ล้วน
**สิ่งสำคัญ:** ให้ซ่อนกระบวนการคิด (Chain of Thought) ไว้ในแท็ก `<details><summary>คลิกเพื่อดูเบื้องหลังการคำนวณตารางเวลา</summary> ... (กระบวนการคิด) ... </details>` เสมอ เพื่อไม่ให้ข้อความรกสายตาผู้ใช้
4. ถ้าระหว่างจัดตารางแล้วพบว่า วิชาเลือก (Elective) หรือวิชาโท (Minor) ที่ผู้ใช้เลือกมา **มีเวลาเรียนชนกับวิชาบังคับ และไม่สามารถจัดลงตารางได้เลย** ให้คุณ "แนะนำวิชาเลือกอื่นๆ ในหมวดเดียวกันจากฐานข้อมูลที่เวลาไม่ชน" ขึ้นมาให้ผู้ใช้พิจารณาแทนทันที
5. เมื่อจัดตารางเสร็จ ให้สรุปตารางเรียนออกมาเป็น **ตาราง Markdown ที่ถูกต้อง (Markdown Table)** โดยให้มี Header คอลัมน์คือ `| วัน | เวลา | รหัสวิชา | ชื่อวิชา | Sec | ห้องเรียน |` และมีบรรทัด `|---|---|---|---|---|---|` คั่นเสมอ ให้จัดกลุ่มวันเดียวกันไว้ติดกัน และเว้นช่อง 'วัน' ให้ว่างไว้สำหรับวิชาที่เรียนวันเดียวกัน (ไม่ต้องพิมพ์ชื่อวันซ้ำ) เพื่อให้อ่านง่ายที่สุด

[DATA SCIENCE CURRICULUM DB (2567)]
{MAJOR_DB_STR}

[MINORS DB]
{MINOR_DB_STR}

[CLASS SCHEDULE DB (2567) - FILTERED FOR RELEVANT COURSES ONLY]
{relevant_schedule}
"""
    config = types.GenerateContentConfig(
        system_instruction=system_instruction,
        temperature=0.2,
    )
    
    # Convert history format
    formatted_history = []
    for msg in req.history:
        role = msg.get("role", "user")
        if role == "assistant":
            role = "model"
        formatted_history.append(types.Content(
            role=role,
            parts=[types.Part.from_text(text=msg.get("content", ""))]
        ))
        
    last_exception = None
    import random
    clients_to_try = list(ALL_CLIENTS)
    random.shuffle(clients_to_try) # Try a random key to spread load
    
    for client in clients_to_try:
        try:
            chat_session = client.chats.create(
                model=MODEL_NAME, 
                config=config,
                history=formatted_history
            )
            response = chat_session.send_message(req.message)
            return {"response": response.text}
        except Exception as e:
            last_exception = e
            print(f"API key failed: {e}")
            continue
            
    raise HTTPException(status_code=500, detail=f"All API keys failed. Last error: {str(last_exception)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)

