# 🎓 CMU Smart Scheduler (AI Chatbot)
**ระบบผู้ช่วยอัจฉริยะเพื่อการวางแผนการศึกษาและจัดตารางเรียน มหาวิทยาลัยเชียงใหม่**

โปรเจกต์นี้คือระบบ (Proof of Concept) สำหรับสกัดข้อมูลหลักสูตรทุกคณะในมหาวิทยาลัยเชียงใหม่โดยอัตโนมัติ เพื่อสร้าง AI Chatbot ที่จะช่วยนักศึกษาจัดตารางเรียน แนะนำวิชาสำรอง และตรวจสอบสถานะการขอจบการศึกษา

---

## 🛠️ สถาปัตยกรรมระบบ (System Architecture)
ระบบแบ่งออกเป็น 3 ส่วนหลัก (Microservices):
1. **Data Ingestion (Backend Pipeline):** ระบบสกัดข้อมูลจาก PDF และ Web Scraping
2. **AI Logic Engine (Core Brain):** ระบบคำนวณเงื่อนไขและจัดตารางเรียน
3. **Frontend Interface:** ระบบโต้ตอบกับผู้ใช้ผ่านแพลตฟอร์มสนทนา (LINE OA / Discord) หรือ Web App

---

## 📅 แผนการพัฒนาแบบละเอียด (Detailed Roadmap)

### Phase 1: การจัดการข้อมูลพื้นฐาน (Data Infrastructure)
เป้าหมาย: สร้างฐานข้อมูล (Modular Knowledge Base) ที่เครื่องคอมพิวเตอร์สามารถนำไปคำนวณต่อได้
*   **Task 1.1: Automated Curriculum Extractor (Python)**
    *   เขียนสคริปต์ (เช่น `pdfplumber` หรือ `PyMuPDF`) อ่านไฟล์ PDF หลักสูตรของมหาวิทยาลัย
    *   หรือใช้ LLM API (Gemini/GPT-4) อ่าน PDF และแปลงโครงสร้างเป็นรูปแบบ `JSON` (วิชาแกน, วิชาโท, GE, วิชาบังคับก่อน)
*   **Task 1.2: Schedule Web Scraper (Python)**
    *   เขียนบอท (เช่น `BeautifulSoup` หรือ `Selenium`) ดึงข้อมูล "ตารางเปิดสอน" จากเว็บไซต์สำนักทะเบียน มช.
    *   ดึงฟิลด์: รหัสวิชา, เซคชั่น, วัน-เวลาเรียน, วัน-เวลาสอบ, สถานะที่นั่ง

### Phase 2: พัฒนาสมองกลหลัก (Core AI Logic)
เป้าหมาย: สร้างโปรแกรมตรวจสอบเงื่อนไขและจัดตาราง
*   **Task 2.1: Prerequisite Checker**
    *   เขียนลอจิกรับข้อมูล Transcript ของนักศึกษา (Mock Data) มาเช็คว่าผ่านวิชาตัวต่อหรือยัง ป้องกันการลงทะเบียนข้ามสเต็ป
*   **Task 2.2: Degree Audit (ตะกร้าหน่วยกิต)**
    *   นับหน่วยกิตวิชาเอก วิชาโท และ GE ที่สอบผ่านแล้ว พร้อมคำนวณว่าขาดอีกกี่หน่วยกิตในแต่ละหมวด
*   **Task 2.3: Smart Schedule Builder**
    *   อัลกอริทึมจับคู่ "วิชาที่ต้องเรียน" เข้ากับ "ตารางสอนที่เปิดในเทอมนี้" โดยล็อกเวลาเรียนไม่ให้ชนกัน 

### Phase 3: พัฒนาฟีเจอร์ช่วยเหลือฉุกเฉิน (Advanced Features)
เป้าหมาย: ตอบโจทย์ Pain points จริงช่วงลงทะเบียน
*   **Task 3.1: Exam Clash Detector**
    *   เพิ่มลอจิกสแกน "ตารางสอบกลางภาค/ปลายภาค" เพื่อกรองวิชาที่มีตารางสอบทับซ้อนกันออกไป
*   **Task 3.2: Plan B Suggester**
    *   ระบบเตรียมตัวเลือกสำรอง (Fallback options) ทันทีในหมวด GE เดียวกัน กรณีเซคชั่นเป้าหมายเต็ม
*   **Task 3.3: Graduation Mock-up**
    *   สคริปต์ Checklist สรุปสถานะก่อนขอจบการศึกษา

### Phase 4: การเชื่อมต่อระบบ (Integration & API)
เป้าหมาย: นำลอจิกทั้งหมดมาเชื่อมโยงกันให้เรียกใช้งานได้
*   **Task 4.1: สร้าง RESTful API (FastAPI)**
    *   นำโค้ดใน Phase 2 & 3 มาห่อด้วย `FastAPI` เพื่อสร้าง Endpoint รอรับคำสั่ง (เช่น `/api/schedule`, `/api/audit`)
*   **Task 4.2: AI Controller**
    *   เขียน Prompt หุ้มระบบ เพื่อให้ AI สามารถแปลคำสั่งภาษาพูดของนักศึกษา แล้วไปเรียกใช้ API ได้อย่างถูกต้อง

### Phase 5: หน้าบ้านและผู้ใช้งาน (Frontend & UX)
เป้าหมาย: สร้างหน้าต่างให้ผู้ใช้เข้ามาใช้งานจริง
*   **Task 5.1: LINE Chatbot Setup**
    *   สร้าง LINE Official Account, นำ Webhook มาต่อกับ API ของเรา (ผ่าน `ngrok` สำหรับเทสต์ในเครื่อง หรือ Deploy บน Render/Heroku)
*   **Task 5.2: Transcript Uploader (LIFF / Web App)**
    *   สร้างหน้าเว็บเล็กๆ (HTML/JS) ให้เด็กกดอัปโหลดไฟล์ PDF (Transcript) ของตัวเองเข้าไปประมวลผล

---

## 👥 การแบ่งงานสำหรับทีม 2 คน (Task Delegation)
เพื่อให้ทำงานขนานกันไปได้และลดปัญหา Git Conflict แนะนำให้แบ่งดังนี้:

**🧑‍💻 คนที่ 1 (Data & Backend Engineer):** 
*   **รับผิดชอบ:** Phase 1 และ Phase 4
*   **งานหลัก:** ทำให้มั่นใจว่าเรามีฐานข้อมูล JSON ที่ถูกต้อง และเขียน API รอรับคำสั่ง
*   **โฟลเดอร์ทำงาน:** `/data_pipeline`, `/api`

**🧑‍💻 คนที่ 2 (AI Logic & Frontend Engineer):** 
*   **รับผิดชอบ:** Phase 2, Phase 3 และ Phase 5
*   **งานหลัก:** เขียนลอจิกการคำนวณ (อัลกอริทึมจัดตาราง) และเชื่อมต่อ Webhook ของ LINE
*   **โฟลเดอร์ทำงาน:** `/logic_engine`, `/frontend`

---

## 🚀 เริ่มต้นทำงาน (Getting Started)
1. Clone Repository นี้ลงเครื่อง
2. รันคำสั่ง `python -m venv venv` เพื่อสร้าง Virtual Environment
3. รันคำสั่ง `pip install -r requirements.txt` (สร้างไฟล์นี้ในภายหลังเมื่อเริ่มเขียนโค้ด)