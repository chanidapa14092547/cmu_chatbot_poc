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
    images: list = [] # list of base64 strings

import re
import base64

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
    
    system_instruction = f"""You are the core AI Engine for an advanced "AI-Assisted Study Planner & Degree Audit" system. Your persona is an expert, highly analytical, and empathetic Academic Advisor. 

Your objective is to analyze student transcripts (provided as images or text), audit graduation requirements based on the curriculum, and dynamically generate an optimized, clash-free course schedule.

---

### CORE DIRECTIVES & LOGIC RULES

#### 1. Image & Transcript Analysis
If the user uploads images of their transcript, you MUST extract ALL passed courses, grades, and total accumulated credits. Use this data to determine their Year Standing (e.g. 1st year = 0-30 credits, 2nd year = 31-60 credits, etc.).

#### 2. Strict JSON State Output
Whenever you process a transcript or the user provides courses they have passed, you MUST include a hidden JSON block at the VERY END of your response. This JSON will be parsed by the frontend to update the Dashboard UI. 
Format it EXACTLY like this:
```json_state
{{
  "ge_credits": <number>,
  "major_req_credits": <number>,
  "major_elec_minor_credits": <number>,
  "free_credits": <number>,
  "passed_courses": ["<course_code>", "<course_code>"],
  "year_standing": "<1, 2, 3, or 4>",
  "alert": "<string: ONLY if they have F/W grade, e.g. 'Found F in Data Structures. Have you retaken it in the summer?'>"
}}
```
Example:
```json_state
{{
  "ge_credits": 15,
  "major_req_credits": 30,
  "major_elec_minor_credits": 0,
  "free_credits": 3,
  "passed_courses": ["206111", "204100", "001101"],
  "year_standing": "2",
  "alert": "Found F in 204100 IT and Modern Life. Have you retaken it?"
}}
```

#### 3. Schedule Generation
*   **Prerequisite Verification:** Verify that the student has passed all required prerequisites based on the transcript data you extracted.
*   **Passed Courses:** NEVER recommend a course they have already passed.
*   **Time Clash Detection:** Carefully cross-check the days and times. A schedule MUST NOT have any overlapping times.
*   **Table Requirement:** The final schedule MUST be presented as a clean Markdown table with exact columns: `| Course Code | Course Name | Credits | Section | Day | Time | Instructor |`

**IMPORTANT:** Always respond to the user in **Thai language** (except for English course names or technical terms).

[DATA SCIENCE CURRICULUM DB (2567)]
{MAJOR_DB_STR}

[CLASS SCHEDULE DB (2567)]
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
        
    # Prepare current message parts
    current_parts = []
    if req.message:
        current_parts.append(types.Part.from_text(text=req.message))
        
    # Process base64 images
    for b64_str in req.images:
        try:
            if "," in b64_str:
                header, b64_data = b64_str.split(",", 1)
                mime_type = header.split(";")[0].split(":")[1]
            else:
                b64_data = b64_str
                mime_type = "image/png"
            
            image_bytes = base64.b64decode(b64_data)
            current_parts.append(types.Part.from_bytes(data=image_bytes, mime_type=mime_type))
        except Exception as e:
            print(f"Error decoding image: {e}")
            continue

    if not current_parts:
        current_parts.append(types.Part.from_text(text="[Empty message]"))

    last_exception = None
    import random
    clients_to_try = list(ALL_CLIENTS)
    random.shuffle(clients_to_try) 
    
    for client in clients_to_try:
        try:
            chat_session = client.chats.create(
                model=MODEL_NAME, 
                config=config,
                history=formatted_history
            )
            response = chat_session.send_message(current_parts)
            return {"response": response.text}
        except Exception as e:
            last_exception = e
            print(f"API key failed: {e}")
            continue
            
    raise HTTPException(status_code=500, detail=f"All API keys failed. Last error: {str(last_exception)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)

