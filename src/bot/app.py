import streamlit as st
import sys
import os
import json

# Ensure the src folder is in the path
sys.path.append(os.path.join(os.path.dirname(__file__), "src"))
from logic_engine.bot_brain import process_message

st.set_page_config(page_title="CMU Advising Bot", page_icon="🐘", layout="wide")

# --- Load Catalog Index ---
@st.cache_data
def load_catalog_index():
    index_path = os.path.join(os.path.dirname(__file__), "src", "logic_engine", "catalog_index.json")
    with open(index_path, 'r', encoding='utf-8') as f:
        return json.load(f)

catalog_index = load_catalog_index()

# --- Sidebar: Student Profile ---
st.sidebar.header("🎓 ข้อมูลนักศึกษา (Student Profile)")
st.sidebar.markdown("ระบบจะดึงกฎของคณะและสาขาที่คุณเลือกมาใช้อัตโนมัติ")

selected_faculty = st.sidebar.selectbox("คณะ (Faculty)", list(catalog_index.keys()))
programs_in_faculty = list(catalog_index[selected_faculty].keys())
selected_program = st.sidebar.selectbox("สาขาวิชา (Program)", programs_in_faculty)

st.sidebar.markdown("---")
st.sidebar.subheader("ข้อมูลเพิ่มเติมสำหรับการประเมิน")
cefr_level = st.sidebar.selectbox("ระดับภาษาอังกฤษ (CEFR)", ["ยังไม่มีผลคะแนน", "A1", "A2", "B1", "B2", "C1", "C2"])
pathway = st.sidebar.radio("แผนการเรียน (Pathway)", ["ยังไม่ตัดสินใจ", "เลือกเรียนวิชาโท (Minor)", "ไม่เรียนวิชาโท (No Minor / Major Electives)"])

# Compile profile
student_profile = {
    "faculty": selected_faculty,
    "program": selected_program,
    "program_data": catalog_index[selected_faculty][selected_program],
    "cefr_level": cefr_level,
    "pathway": pathway
}

# --- Main Chat UI ---
st.title("🐘 CMU Smart Advising Bot (POC)")
st.caption(f"ปัจจุบันกำลังให้คำปรึกษา: **{catalog_index[selected_faculty][selected_program]['program_name']}**")

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "สวัสดีค่ะ! พี่คือผู้ช่วยแนะนำการลงทะเบียนเรียน\nหนูสามารถพิมพ์ถามพี่ได้เลย เช่น:\n- 'พี่คะ หนูมีคะแนน B1 ต้องลงอังกฤษไหม?'\n- 'หนูเลือก No Minor ต้องลงวิชาเลือกเอกเพิ่มกี่หน่วยกิตคะ?'\n- 'วิชาเอกคอมมีอะไรให้ลงบ้าง และตารางชนกันไหมคะ?'"}
    ]

# Display chat messages from history on app rerun
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# React to user input
if prompt := st.chat_input("พิมพ์ข้อความที่นี่..."):
    st.chat_message("user").markdown(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})

    with st.chat_message("assistant"):
        with st.spinner("กำลังคิดวิเคราะห์..."):
            # Pass BOTH the prompt and the student profile to the brain
            response = process_message(prompt, student_profile)
            st.markdown(response)
    
    st.session_state.messages.append({"role": "assistant", "content": response})

