import os
import sys
import streamlit as st
from google import genai
from google.genai import types
from dotenv import load_dotenv

load_dotenv()

# Page config
st.set_page_config(page_title="CMU Smart Scheduler", page_icon="🎓", layout="wide")

st.title("🎓 CMU Smart Scheduler (Data Science)")
st.caption("AI-Powered Course Assistant for Chiang Mai University (PoC: Data Science)")

@st.cache_data
def load_data():
    try:
        with open('data/json_db/Faculty of Science/Bachelor of Science Program in Data Science (2567).json', 'r', encoding='utf-8') as f:
            major_db = f.read()
        with open('data/json_db/Minors.json', 'r', encoding='utf-8') as f:
            minor_db = f.read()
        with open('data/json_db/schedule_2567.csv', 'r', encoding='utf-8') as f:
            schedule_db = f.read()
        return major_db, minor_db, schedule_db
    except Exception as e:
        st.error(f"Failed to load data: {e}")
        return None, None, None

def init_gemini_and_model():
    keys_str = os.environ.get("GEMINI_API_KEYS", "")
    single_key = os.environ.get("GEMINI_API_KEY", "")
    
    all_keys = []
    if single_key:
        all_keys.append(single_key)
    if keys_str:
        all_keys.extend(keys_str.split(","))
        
    for key in all_keys:
        key = key.strip()
        if not key:
            continue
        try:
            client = genai.Client(api_key=key)
            model_name = find_working_model(client)
            if model_name:
                return client, model_name
        except Exception:
            continue
            
    return None, None

def find_working_model(client):
    available_models = []
    try:
        for m in client.models.list():
            name = m.name.replace("models/", "")
            available_models.append(name)
    except Exception as e:
        available_models = [
            'gemini-3.5-flash', 'gemini-3.0-flash', 'gemini-2.5-pro',
            'gemini-2.5-flash', 'gemini-2.0-flash-exp', 'gemini-1.5-pro', 'gemini-pro',
            'gemini-flash-lite-latest'
        ]
        
    gemini_models = sorted([m for m in available_models if 'gemini' in m], reverse=True)
    other_models = sorted([m for m in available_models if 'gemini' not in m], reverse=True)
    available_models = gemini_models + other_models
        
    for model_name in available_models:
        if any(skip in model_name for skip in ["embed", "tune", "vision", "aqa", "robotics"]):
            continue
            
        try:
            chat = client.chats.create(model=model_name)
            response = chat.send_message("Hello")
            if response.text:
                return model_name
        except Exception:
            continue
            
    return None

# Initialize session state
if "messages" not in st.session_state:
    st.session_state.messages = []
if "chat_session" not in st.session_state:
    st.session_state.chat_session = None
if "client" not in st.session_state:
    st.session_state.client = None

# Sidebar
with st.sidebar:
    st.header("เกี่ยวกับโปรเจกต์ (About)")
    st.markdown("""
    **Proof of Concept (PoC)**
    *   **Scope:** หลักสูตรวิทยาการข้อมูล (Data Science) คณะวิทยาศาสตร์ มช.
    *   **Core AI:** Gemini Pro + Chain of Thought Reasoning
    *   **Features:** จัดตารางเรียน ป้องกันเวลาชน แนะนำวิชาเลือก
    """)
    if st.button("🗑️ ล้างแชท (Clear Chat)"):
        st.session_state.messages = []
        st.session_state.chat_session = None
        st.session_state.client = None
        st.rerun()

# Load DB and setup
major_db, minor_db, schedule_db = load_data()
if not major_db:
    st.stop()

if st.session_state.chat_session is None:
    client, model_name = init_gemini_and_model()
    st.session_state.client = client
    
    if not client or not model_name:
        st.error("❌ ไม่พบโมเดลใดๆ ที่สามารถใช้งานได้กับ API Key นี้ หรือโควต้า API อาจจะเต็มหมดทุกคีย์ครับ")
        st.stop()
    
    system_instruction = f"""คุณคือผู้ช่วยอัจฉริยะ (Chatbot) ให้คำปรึกษาด้านวิชาการสำหรับนักศึกษาหลักสูตร 'วิทยาการข้อมูล (Data Science) ปี 2567' คณะวิทยาศาสตร์ มหาวิทยาลัยเชียงใหม่
หน้าที่ของคุณคือตอบคำถามนักศึกษาเกี่ยวกับการลงทะเบียนเรียน หมวดวิชา วิชาบังคับ วิชาเลือก วิชาโท แผนการศึกษา เงื่อนไขต่างๆ และ ตารางเรียน โดยอ้างอิงจากฐานข้อมูล JSON ด้านล่างนี้เท่านั้น
เวลาตอบ ให้เน้นตอบอย่างกระชับ ตรงประเด็น เป็นทางการและสุภาพ
**กฎเหล็กเรื่องการจัดตารางเรียน (STRICT RULE):** 
1. หากผู้ใช้ระบุชื่อวิชาเลือกและเงื่อนไขเวลามาให้ครบถ้วนแล้ว (เช่น ส่งมาจากฟอร์ม) ให้คุณลุยจัดตารางแบบ Chain-of-Thought ได้เลย **ห้าม** ถามเซ้าซี้ซ้ำอีก!
2. แต่ถ้าผู้ใช้ระบุวิชาเลือกมาไม่ครบ หรือปล่อยว่างไว้ บอท **ต้องหยุด** และถามกลับดังนี้:
   - ตรวจสอบจากโครงสร้างหลักสูตรว่าเทอมนั้นต้องลงวิชาเลือกหมวดอะไรบ้าง
   - **สำคัญมาก:** คุณต้องดึง "รายชื่อวิชา และ รหัสวิชา" ที่อยู่ในหมวดนั้นๆ จาก JSON มาลิสต์เป็นตัวอย่างให้ผู้ใช้ดู (อย่างน้อย 3-5 วิชา) ผู้ใช้จะได้รู้ว่ามีวิชาอะไรให้เลือกบ้าง ห้ามบอกแค่ชื่อหมวดลอยๆ เด็ดขาด! (ถ้าเป็นหมวด Free Elective ให้แนะนำวิชาที่น่าสนใจทั่วไปได้)
   - "มีเงื่อนไขเวลาไหมครับ เช่น ไม่อยากเรียน 8 โมงเช้า หรืออยากว่างวันไหนเป็นพิเศษ?"
3. ตอนจัดตาราง บอท **ต้องคิดวิเคราะห์หาเซคชั่นที่ไม่ชนกันทีละขั้นตอน (Chain of Thought)** โดยพิมพ์อธิบายทีละบรรทัดว่าเวลาชนไหมก่อนเสมอ ห้ามลักไก่เอาเซค 001 ล้วน
4. ถ้าระหว่างจัดตารางแล้วพบว่า วิชาเลือก (Elective) หรือวิชาโท (Minor) ที่ผู้ใช้เลือกมา **มีเวลาเรียนชนกับวิชาบังคับ และไม่สามารถจัดลงตารางได้เลย** ให้คุณ "แนะนำวิชาเลือกอื่นๆ ในหมวดเดียวกันจากฐานข้อมูลที่เวลาไม่ชน" ขึ้นมาให้ผู้ใช้พิจารณาแทนทันที
5. เมื่ออธิบายเหตุผลจบ ค่อยแสดงตาราง Markdown **โดยต้องระวังการวาดตารางให้ถูกต้องเด็ดขาด ห้ามใส่วิชาลงในคอลัมน์วันที่ไม่ได้เรียน (เช่น ถ้าเรียนแค่ Tu Fr ห้ามเผลอใส่ใน Mo Th เด็ดขาด)**

[DATA SCIENCE CURRICULUM DB (2567)]
{major_db}

[MINORS DB]
{minor_db}

[CLASS SCHEDULE DB (2567)]
{schedule_db}
"""
    config = types.GenerateContentConfig(
        system_instruction=system_instruction,
        temperature=0.2,
    )
    st.session_state.chat_session = client.chats.create(model=model_name, config=config)

import json
try:
    major_json = json.loads(major_db)
    study_plan = major_json.get("study_plan", {})
except Exception:
    study_plan = {}

# Quick Schedule Form (Dynamic)
with st.expander("🛠️ เมนูจัดตารางเรียนฉบับด่วน (Quick Scheduler)", expanded=True):
    col1, col2 = st.columns(2)
    with col1:
        target_year = st.selectbox("เลือกชั้นปี", ["ปี 1", "ปี 2", "ปี 3", "ปี 4"], key="qs_year")
    with col2:
        target_term = st.selectbox("เลือกเทอม", ["เทอม 1", "เทอม 2"], key="qs_term")
    
    year_num = target_year.split()[1]
    term_num = target_term.split()[1]
    plan_key = f"year_{year_num}_semester_{term_num}"
    
    required_placeholders = []
    if plan_key in study_plan:
        for item in study_plan[plan_key]:
            if isinstance(item, dict) and "category_placeholder" in item:
                required_placeholders.append({
                    "placeholder": item["category_placeholder"],
                    "credits": item.get("credits_required", 3)
                })
    
    with st.container():
        st.markdown(f"**กรอกข้อมูลเพื่อจัดตารางเรียนอัตโนมัติ ({target_year} {target_term})**")
        
        major_tracks = major_json.get("major_tracks", [])
        selected_track = None
        if major_tracks:
            selected_track = st.selectbox("เลือกแขนงวิชาเอก (Major Track):", ["ไม่ระบุ (แสดงทั้งหมด)"] + major_tracks, key="major_track_sel")
        
        # 1. Parse offered course codes from schedule_db
        offered_course_codes = set()
        offered_courses_dict = {}
        for line in schedule_db.splitlines()[1:]:
            if line.strip():
                parts = line.split('|')
                if len(parts) > 1:
                    code = parts[0].strip()
                    name = parts[1].strip()
                    offered_course_codes.add(code)
                    offered_courses_dict[code] = name
                    
        # 2. Parse minor_db
        try:
            minor_json = json.loads(minor_db)
            all_minors = []
            minor_courses_map = {}
            for fac in minor_json:
                for prog in fac.get("programs", []):
                    for m in prog.get("minors", []):
                        m_name = m.get("minor_name", "")
                        if m_name not in minor_courses_map:
                            all_minors.append(m_name)
                            minor_courses_map[m_name] = set()
                        for g in m.get("courses_list", []):
                            for c in g.get("courses", []):
                                if str(c).isdigit() and len(str(c)) == 6:
                                    minor_courses_map[m_name].add(str(c))
        except Exception:
            all_minors = []
            minor_courses_map = {}
                    
        elective_choices = {}
        if required_placeholders:
            st.markdown("**วิชาที่ต้องเลือกสำหรับเทอมนี้ (แสดงเฉพาะที่เปิดสอน):**")
            for i, ph_dict in enumerate(required_placeholders):
                ph = ph_dict["placeholder"]
                req_courses = ph_dict["credits"] // 3
                req_text = f"(ต้องเลือก {req_courses} วิชา)" if req_courses > 0 else ""
                short_name = ph.split('/')[-1].strip()
                
                # Handling Minor or Major Electives
                if "Minor" in ph:
                    minor_choice = st.selectbox(f"หมวด {short_name} {req_text}: เลือกแขนงวิชาโท (ถ้ามี):", ["ไม่ระบุ / เลือกลงเป็นวิชาเอกเลือก (Major Elective) แทน"] + all_minors, key=f"minor_sel_{i}")
                    
                    if minor_choice == "ไม่ระบุ / เลือกลงเป็นวิชาเอกเลือก (Major Elective) แทน":
                        # Fallback to Major Electives
                        available_options = []
                        for c in major_json.get("courses", []):
                            track = c.get("category_or_track", "")
                            code = c.get("course_code", "")
                            name = c.get("course_name_en", "")
                            if "Major Elective" in track and code in offered_course_codes:
                                if selected_track and selected_track != "ไม่ระบุ (แสดงทั้งหมด)" and selected_track not in track:
                                    continue
                                available_options.append(f"{code} {name}")
                        
                        if available_options:
                            elective_choices[f"{short_name}_{i}"] = st.multiselect(f"วิชาเอกเลือก (Major Electives) ที่เปิดสอน {req_text}:", available_options, key=f"maj_fallback_{i}")
                        else:
                            elective_choices[f"{short_name}_{i}"] = st.text_input(f"วิชาเอกเลือก {req_text}:", placeholder="พิมพ์รหัส/ชื่อวิชา หรือเว้นว่างให้ AI แนะนำ", key=f"maj_fallback_txt_{i}")
                    else:
                        # Show Minor Courses
                        minor_courses = minor_courses_map.get(minor_choice, set())
                        offered_minor_courses = [c for c in minor_courses if c in offered_course_codes]
                        if offered_minor_courses:
                            offered_minor_options = [f"{c} {offered_courses_dict[c]}" for c in offered_minor_courses]
                            elective_choices[f"{short_name}_{i}"] = st.multiselect(f"รายวิชาโท {minor_choice} ที่เปิดสอนเทอมนี้ {req_text}:", offered_minor_options, key=f"minor_crs_{i}")
                        else:
                            st.warning(f"⚠️ วิชาโท {minor_choice} ไม่มีวิชาเปิดสอนเทอมนี้เลย (คุณสามารถเปลี่ยนกลับไปเลือกวิชาเอกเลือกแทนได้)")
                            elective_choices[f"{short_name}_{i}"] = ""
                
                else:
                    # Regular Categories
                    available_options = []
                    category_exists_in_db = False
                    
                    for c in major_json.get("courses", []):
                        track = c.get("category_or_track", "")
                        code = c.get("course_code", "")
                        name = c.get("course_name_en", "")
                        if ph in track:
                            category_exists_in_db = True
                            if code in offered_course_codes:
                                if "Major Elective" in ph and selected_track and selected_track != "ไม่ระบุ (แสดงทั้งหมด)" and selected_track not in track:
                                    continue
                                available_options.append(f"{code} {name}")
                    
                    if available_options:
                        elective_choices[f"{short_name}_{i}"] = st.multiselect(f"หมวด {short_name} {req_text}:", available_options, key=f"reg_sel_{i}")
                    elif category_exists_in_db:
                        st.warning(f"⚠️ หมวด {short_name} ไม่มีรายวิชาเปิดสอนในตารางเทอมนี้")
                        elective_choices[f"{short_name}_{i}"] = ""
                    else:
                        # Category not in DB (like Free Electives)
                        elective_choices[f"{short_name}_{i}"] = st.text_input(f"หมวด {short_name} {req_text}:", placeholder="พิมพ์รหัส/ชื่อวิชาอิสระ หรือเว้นว่างให้ AI แนะนำ", key=f"reg_txt_{i}")
        else:
            st.info("💡 เทอมนี้เป็นวิชาบังคับล้วน ไม่มีหมวดวิชาเลือกในโครงสร้างหลักสูตรครับ")
            
        time_constraints = st.text_input("เงื่อนไขเวลาพิเศษ (ถ้ามี)", placeholder="เช่น ไม่เรียน 8 โมงเช้า, ขอหยุดวันศุกร์")
        
        submitted = st.button("✨ เริ่มจัดตารางเรียน")
        
        if submitted:
            prompt_text = f"ช่วยจัดตารางเรียนให้หน่อย สำหรับ {target_year} {target_term}"
            for cat_key, choice in elective_choices.items():
                if choice:
                    cat_name = cat_key.rsplit('_', 1)[0] # Remove the _i suffix
                    if isinstance(choice, list):
                        if choice: # Only if list is not empty
                            prompt_text += f"\n- ขอเลือกวิชาในหมวด {cat_name} เป็น: {', '.join(choice)}"
                    elif "ไม่ระบุ" not in choice:
                        prompt_text += f"\n- ขอเลือกวิชาในหมวด {cat_name} เป็น: {choice}"
            if time_constraints:
                prompt_text += f"\n- เงื่อนไขเพิ่มเติม: {time_constraints}"
            
            st.session_state.pending_prompt = prompt_text

# Display chat history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Chat input and processing
user_input = st.chat_input("พิมพ์คำถามที่นี่ หรือใช้เมนูด้านบนเพื่อความรวดเร็ว")
prompt = None

if st.session_state.get("pending_prompt"):
    prompt = st.session_state.pending_prompt
    st.session_state.pending_prompt = None
elif user_input:
    prompt = user_input

if prompt:
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        with st.spinner("AI กำลังประมวลผล (ใช้วิธีคิดแบบ Chain-of-Thought เพื่อป้องกันเวลาชน)..."):
            try:
                response = st.session_state.chat_session.send_message(prompt)
                message_placeholder.markdown(response.text)
                st.session_state.messages.append({"role": "assistant", "content": response.text})
            except Exception as e:
                message_placeholder.error(f"เกิดข้อผิดพลาด: {e}")
