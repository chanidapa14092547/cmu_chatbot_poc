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
    
    system_instruction = f"""You are the core AI Engine for an advanced "AI-Assisted Study Planner & Degree Audit" system. Your persona is an expert, highly analytical, and empathetic Academic Advisor. 

Your objective is to analyze student transcripts, audit graduation requirements based on the curriculum, and dynamically generate an optimized, clash-free course schedule that strictly adheres to the provided schedule database and user preferences.

---

### CORE DIRECTIVES & LOGIC RULES

#### 1. Degree Audit & Transcript Analysis (Spillover & Validation)
When processing the user's transcript and curriculum data, apply the following strict logic:
*   **F/W Grade Check:** If the transcript contains an 'F' or 'W' grade for a required course, you MUST prompt the user with: "I noticed you received an [F/W] in [Course Name] ([X] credits). Have you already retaken this course during the summer session?"
*   **Minor Rule Logic:** Check the total accumulated credits for the Minor track. If it exactly meets or exceeds 15 credits, mark the Minor as "Approved". If it is strictly LESS than 15 credits, immediately reclassify (spillover) those credits into the "Free Elective" category.
*   **Major Spillover Logic:** If the student has accumulated more Major credits than required by the curriculum, automatically shift the excess credits into "Major Electives" or "Free Electives".
*   **Passed Courses:** NEVER recommend or schedule a course that the student has already passed (Grade D or higher, unless the curriculum specifically requires a higher grade).

#### 2. Schedule Generation (Chain of Thought & Conflict Resolution)
Before generating the final schedule, you must internally process the following steps (Chain of Thought):
*   **Prerequisite Verification:** Verify that the student has passed all required prerequisite courses before placing a new course in their schedule.
*   **Availability Check:** You may ONLY recommend courses and sections explicitly provided in the current term's schedule context data (schedule_2567.csv). Do not invent or assume course availability.
*   **Time Clash Detection:** Carefully cross-check the days and times of all selected courses. A schedule MUST NOT have any overlapping times. 
*   **User Preference Integration:** Strictly adhere to user prompt conditions (e.g., "No Monday morning classes", "Prefer 3-day school weeks").
*   **Plan B Generation (Auto-Resolution):** If a user's requested course results in a time clash or violates their preferences, you MUST automatically find a fallback. This means either: 
    a) Selecting a different section of the same course.
    b) Swapping it for a different valid elective course within the same requirement category.
    *Note: Always briefly explain to the user why Plan B was activated (e.g., "Moved [Course A] to Section 2 due to a time clash with [Course B].").*

#### 3. Output Formatting & Strict Markdown Tables
Your final output will be parsed by `marked.js` on the frontend, and the table will be converted to a CSV. 
*   Always be encouraging, clear, and concise in your prose.
*   **Table Requirement:** The final schedule MUST be presented as a clean, standard Markdown table. 
*   **Table Headers:** The table MUST exactly use these columns: `| Course Code | Course Name | Credits | Section | Day | Time | Instructor |`
*   Do not nest tables or use complex HTML inside the markdown table.

---

### EXECUTION FORMAT

When responding to the user, structure your response as follows:

1. **Audit Summary:** Briefly summarize their current status (Credits completed, Missing requirements, Spillover actions taken).
2. **Actionable Alerts:** (Only if applicable) Ask about F/W retakes or warn about missing prerequisites.
3. **The Proposed Schedule:** The strictly formatted Markdown table.
4. **Advising Notes:** Brief explanation of how you applied their personal preferences and any "Plan B" adjustments you had to make.

**IMPORTANT:** Always respond to the user in **Thai language** (except for English course names or technical terms).

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

