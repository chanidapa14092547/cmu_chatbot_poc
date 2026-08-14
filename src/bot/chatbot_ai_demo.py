import os
import sys
import json
import warnings
import logging
warnings.filterwarnings("ignore")
logging.getLogger().setLevel(logging.ERROR)
from google import genai
from google.genai import types

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

def main():
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        print("❌ Error: ไม่พบ GEMINI_API_KEY")
        sys.exit(1)
        
    client = genai.Client(api_key=api_key)
    
    model_name = find_working_model(client)
    if not model_name:
        print("\n❌ ไม่พบโมเดลใดๆ ที่สามารถใช้งานได้กับบัญชีนี้")
        print("อาจจะต้องพรีเซนต์ด้วย chatbot_datasci.py (เวอร์ชันธรรมดา) ไปก่อนครับพรุ่งนี้!")
        sys.exit(1)
        
    try:
        with open('data/json_db/Faculty of Science/Bachelor of Science Program in Data Science (2567).json', 'r', encoding='utf-8') as f:
            major_db = f.read()
        with open('data/json_db/Minors.json', 'r', encoding='utf-8') as f:
            minor_db = f.read()
        
        # Load the newly extracted schedule data (compressed as CSV to save tokens)
        with open('data/json_db/schedule_2567.csv', 'r', encoding='utf-8') as f:
            schedule_db = f.read()
    except Exception as e:
        print(f"Error loading JSON data: {e}")
        sys.exit(1)
        
    system_instruction = f"""คุณคือผู้ช่วยอัจฉริยะ (Chatbot) ให้คำปรึกษาด้านวิชาการสำหรับนักศึกษาหลักสูตร 'วิทยาการข้อมูล (Data Science) ปี 2567' คณะวิทยาศาสตร์ มหาวิทยาลัยเชียงใหม่
หน้าที่ของคุณคือตอบคำถามนักศึกษาเกี่ยวกับการลงทะเบียนเรียน หมวดวิชา วิชาบังคับ วิชาเลือก วิชาโท แผนการศึกษา เงื่อนไขต่างๆ และ ตารางเรียน (วัน/เวลา/สถานที่/อาจารย์ผู้สอน) โดยอ้างอิงจากฐานข้อมูล JSON ด้านล่างนี้เท่านั้น ห้ามแต่งข้อมูลขึ้นเอง
เวลาตอบ ให้เน้นตอบอย่างกระชับ ตรงประเด็น เป็นทางการและสุภาพ (Professional) แต่ยังคงความเป็นธรรมชาติ หลีกเลี่ยงคำสร้อยหรือคำทักทายที่ดูวัยรุ่นเกินไป (เช่น ไม่ต้องใช้คำว่า 'จ้า', 'หวัดดี', 'น้อง') และสามารถเข้าใจคำย่อได้ (เช่น 'แมท' = คณิตศาสตร์, 'สแตต' = สถิติ, 'คอม' = คอมพิวเตอร์)
**คำสั่งพิเศษเรื่องตารางเรียน:** หากมีคำถามเรื่องตารางเรียนหรือเซคชั่น ให้เตือนสั้นๆ ท้ายคำตอบเสมอว่า "หมายเหตุ: ข้อมูลตารางเรียนนี้อ้างอิงจากฐานข้อมูลเบื้องต้น กรุณาตรวจสอบข้อมูลล่าสุดจากสำนักทะเบียนอีกครั้ง"
**กฎเหล็กเรื่องการจัดตารางเรียน (STRICT RULE):** 
1. การ "จัดตารางเรียน" คือการเลือกเซคชั่น วัน เวลา และห้องเรียน มาประกอบกัน (ไม่ใช่แค่การบอกแผนการศึกษา)
2. เมื่อนักศึกษาพิมพ์ขอให้ "จัดตารางเรียน" **ห้าม** บอทจัดตารางให้ทันที และ **ห้าม** ลิสต์รายวิชาให้ดูก่อนเด็ดขาด! บอท **ต้องหยุด** และถามกลับ 2 คำถามนี้ก่อนเสมอ:
   - ตรวจสอบจากโครงสร้างหลักสูตรว่าเทอมนั้นมีวิชาเลือกกลุ่มไหน (เช่น Basic Science) และมีวิชาย่อยอะไรบ้าง จากนั้นลิสต์ชื่อวิชาที่มีให้เลือกทั้งหมดส่งไปถามผู้ใช้ (เช่น "วิชาเลือก Basic Science ของเทอมนี้มี Biology 1, Chemistry 1, และ Physics 1 สนใจลงตัวไหนครับ?")
   - "มีเงื่อนไขเวลาไหมครับ เช่น ไม่อยากเรียน 8 โมงเช้า หรืออยากว่างวันไหนเป็นพิเศษ?"
3. หลังจากนักศึกษาตอบคำถาม บอท **ต้องคิดวิเคราะห์หาเซคชั่นที่ไม่ชนกันทีละขั้นตอน (Chain of Thought)** โดยให้พิมพ์อธิบายกระบวนการคิดออกมาก่อน ดังนี้:
   - "วิชาที่ 1: ... เลือกเซคชั่น ... เวลา ..."
   - "วิชาที่ 2: ... ขอพิจารณาเซคชั่น ... (เช็คว่าเวลาชนกับวิชาที่ 1 ไหม? ถ้าชนให้เปลี่ยนเซคชั่น) สรุปเลือกเซคชั่น ... เวลา ..."
   - "วิชาที่ 3: ..."
   บอทต้องตรวจสอบวันและเวลาอย่างละเอียด ห้ามลักไก่เลือกเซคชั่น 001 หมดเด็ดขาด และถ้าวิชาไหนมีเซคชั่นเดียวและหลีกเลี่ยงเวลาไม่ได้ ให้แจ้งผู้ใช้ตามตรงว่าหลีกเลี่ยงไม่ได้
4. เมื่ออธิบายเหตุผลจบแล้ว ค่อยแสดงผลลัพธ์เป็น **ตาราง (Markdown Table)** เท่านั้น (คอลัมน์: รหัสวิชา | ชื่อวิชา | เซคชั่น | วัน-เวลา | ห้องเรียน)

[DATA SCIENCE CURRICULUM DB (2567)]
{major_db}

[MINORS DB]
{minor_db}

[CLASS SCHEDULE DB (2567)]
{schedule_db}
"""

    print("==================================================")
    print("CMU Chatbot AI Demo: Data Science (2567)")
    print(f"Model: {model_name}")
    print("พิมพ์คำถามที่ต้องการ หรือพิมพ์ 'exit' เพื่อออก")
    print("==================================================")

    config = types.GenerateContentConfig(
        system_instruction=system_instruction,
        temperature=0.2,
    )
    
    chat = client.chats.create(model=model_name, config=config)
    
    while True:
        try:
            query = input("\nQ: ")
            if query.lower() in ['exit', 'quit']:
                break
            if not query.strip():
                continue
            
            response = chat.send_message(query)
            print(f"A:\n{response.text}")
            
        except (KeyboardInterrupt, EOFError):
            break
        except Exception as e:
            print(f"Error: {e}")

if __name__ == "__main__":
    main()
