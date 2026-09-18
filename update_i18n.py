# -*- coding: utf-8 -*-
import re

# 1. Update i18n.js
with open('src/webapp/frontend/i18n.js', 'r') as f:
    i18n_content = f.read()

new_en = """
        "nav-next-sem": "Next Semester",
        "nav-curr-prog": "Curriculum Progress",
        "header-title-next": "Next Semester",
        "header-title-curr": "Curriculum Progress",
        "btn-lang": "🇹🇭 เปลี่ยนเป็นภาษาไทย",
        
        "chat-title": "AI Advisor Chat",
        "chat-greeting": "Hello! I am your AI Academic Advisor for the Data Science track at CMU.<br><br>I'm here to provide guidance, recommend courses, check graduation requirements, and help you plan your schedule! Select your courses on the left or type your questions below.",
        "chat-placeholder": "Ask something (e.g., Can you arrange my schedule?)",
        
        "prog-title": "Curriculum Progress",
        "prog-desc": "Actual earned-credit progress against the Data Science curriculum.",
        "upload-btn2": "Upload Transcript",
        "upload-drop": "Drop your transcript here, or click to browse",
        "upload-supports": "Supports PDF, PNG, JPG for AI Processing",
        "action-required": "Action Required",
        
        "group-ge": "General Education",
        "group-core": "Core & Major Courses",
        "group-other": "Other Requirements",
        
        "status-incomplete": "INCOMPLETE",
        "status-complete": "COMPLETE",
        "status-option": "OPTION REQUIRED",
        "credits-remaining": "credits remaining",
        
        "courses-to-select": "Courses to select this semester",
        "major-elec-offered": "Major Electives offered ({req}):",
        "minor-offered": "Minor {minor} courses offered ({req}):",
        "cat-req": "{name} category ({req}):",
        "warn-no-major": "⚠️ No major electives offered this term or none matching your track.",
        "warn-no-minor": "⚠️ No {minor} minor courses offered this term.",
        "warn-no-course": "⚠️ No courses offered",
        "free-elec-placeholder": "Type course code/name (any course)",
        "group-name": "▶ Group {name}",
        "passed": "(Passed)",
        "no-core-left": "(No core courses left to take)",
        
        "cat-ge": "General Education",
        "cat-ge-req": "Required General Education",
        "cat-ge-elec": "GE Electives",
        "cat-core": "Core Courses",
        "cat-major-comp": "Major Compulsory",
        "cat-major-elec": "Major Elective",
        "cat-minor": "Minor / No Minor",
        "cat-free": "Free Elective",
        "cat-total": "Total Credits",
        "cat-rem": "credits remaining",
        
        "upload-btn": "Upload Transcript Images",
        "upload-desc": "Supported formats: JPG, PNG",
        "btn-generate": "Generate Schedule"
"""

new_th = """
        "nav-next-sem": "จัดตารางเรียน",
        "nav-curr-prog": "ความคืบหน้าหลักสูตร",
        "header-title-next": "จัดตารางเรียนเทอมถัดไป",
        "header-title-curr": "ความคืบหน้าหลักสูตร",
        "btn-lang": "🇬🇧 Switch to English",
        
        "chat-title": "ผู้ช่วย AI จัดตารางเรียน",
        "chat-greeting": "สวัสดีครับ! ผมคือ Academic Advisor อัจฉริยะ สำหรับสาขา Data Science มช.<br><br>ผมพร้อมให้คำปรึกษา แนะนำการลงทะเบียน ตรวจสอบเงื่อนไขการจบการศึกษา และช่วยจัดตารางเรียนให้คุณแล้วครับ! ลองเลือกวิชาทางซ้ายมือ หรือพิมพ์คำถามมาได้เลยครับ",
        "chat-placeholder": "พิมพ์คำถาม (เช่น ช่วยจัดตารางเรียนให้หน่อย)",
        
        "prog-title": "ความคืบหน้าหลักสูตร",
        "prog-desc": "ตรวจสอบหน่วยกิตที่เก็บได้เทียบกับโครงสร้างหลักสูตรวิทยาการข้อมูล",
        "upload-btn2": "อัปโหลดทรานสคริปต์",
        "upload-drop": "ลากไฟล์ทรานสคริปต์มาวางที่นี่ หรือคลิกเพื่อเลือกไฟล์",
        "upload-supports": "รองรับไฟล์ PDF, PNG, JPG สำหรับให้ AI ประมวลผล",
        "action-required": "ต้องดำเนินการ",
        
        "group-ge": "หมวดวิชาศึกษาทั่วไป (GE)",
        "group-core": "หมวดวิชาแกนและวิชาเอก",
        "group-other": "หมวดวิชาอื่นๆ",
        
        "status-incomplete": "ยังไม่ครบ",
        "status-complete": "ครบแล้ว",
        "status-option": "ต้องเลือก",
        "credits-remaining": "หน่วยกิตที่ขาด",
        
        "courses-to-select": "วิชาที่ต้องเลือกสำหรับเทอมนี้",
        "major-elec-offered": "วิชาเอกเลือก (Major Electives) ที่เปิดสอน ({req}):",
        "minor-offered": "รายวิชาโท {minor} ที่เปิดสอนเทอมนี้ ({req}):",
        "cat-req": "หมวด {name} ({req}):",
        "warn-no-major": "⚠️ ไม่มีวิชาเอกเลือกเปิดสอนในเทอมนี้ หรือไม่ตรงกับแขนงที่เลือก",
        "warn-no-minor": "⚠️ วิชาโท {minor} ไม่มีวิชาเปิดสอนเทอมนี้เลย",
        "warn-no-course": "⚠️ ไม่มีวิชาเปิดสอน",
        "free-elec-placeholder": "พิมพ์รหัส/ชื่อวิชา (วิชาใดก็ได้)",
        "group-name": "▶ กลุ่ม {name}",
        "passed": "(ผ่านแล้ว)",
        "no-core-left": "(ไม่มีวิชาแกนที่เปิดสอนและยังไม่ผ่าน)",
        
        "cat-ge": "หมวดวิชาศึกษาทั่วไป",
        "cat-ge-req": "กลุ่มวิชาศึกษาทั่วไปบังคับ",
        "cat-ge-elec": "กลุ่มวิชาศึกษาทั่วไปเลือก",
        "cat-core": "วิชาแกน",
        "cat-major-comp": "วิชาเอก (บังคับ)",
        "cat-major-elec": "วิชาเอก (เลือก)",
        "cat-minor": "วิชาโท / เลือกเสรี (ไม่มีโท)",
        "cat-free": "หมวดวิชาเลือกเสรี",
        "cat-total": "หน่วยกิตรวมทั้งหมด",
        "cat-rem": "หน่วยกิตที่ขาด",
        
        "upload-btn": "อัปโหลดรูปภาพ Transcript",
        "upload-desc": "รองรับไฟล์: JPG, PNG",
        "btn-generate": "สร้างตารางเรียน"
"""

# Very naive replacement of the dictionaries.
i18n_content = re.sub(r'"en": \{.*?\n    \},', f'"en": {{{new_en}\n    }},', i18n_content, flags=re.DOTALL)
i18n_content = re.sub(r'"th": \{.*?\n    \}', f'"th": {{{new_th}\n    }}', i18n_content, flags=re.DOTALL)

t_helper = """
window.t = function(key, replacements = {}) {
    let text = i18n[currentLang][key] || key;
    for (const [k, v] of Object.entries(replacements)) {
        text = text.replace(`{${k}}`, v);
    }
    return text;
};
"""
if "window.t =" not in i18n_content:
    i18n_content += t_helper

# Also dispatch an event so app.js knows when lang changes to re-render
i18n_content = i18n_content.replace(
    "if (langBtn) langBtn.innerHTML = i18n[currentLang][\"btn-lang\"];\n}", 
    "if (langBtn) langBtn.innerHTML = i18n[currentLang][\"btn-lang\"];\n    window.dispatchEvent(new Event('languageChanged'));\n}"
)

with open('src/webapp/frontend/i18n.js', 'w') as f:
    f.write(i18n_content)

# 2. Update index.html
with open('src/webapp/frontend/index.html', 'r') as f:
    html = f.read()

html = html.replace('<h3>AI Advisor Chat</h3>', '<h3 data-i18n="chat-title">AI Advisor Chat</h3>')
html = html.replace('<div class="bubble">สวัสดีครับ! ผมคือ Academic Advisor อัจฉริยะ สำหรับสาขา Data Science มช.<br><br>ผมพร้อมให้คำปรึกษา แนะนำการลงทะเบียน ตรวจสอบเงื่อนไขการจบการศึกษา และช่วยจัดตารางเรียนให้คุณแล้วครับ! ลองเลือกวิชาทางซ้ายมือ หรือพิมพ์คำถามมาได้เลยครับ</div>', '<div class="bubble" data-i18n="chat-greeting">สวัสดีครับ! ผมคือ Academic Advisor อัจฉริยะ สำหรับสาขา Data Science มช.<br><br>ผมพร้อมให้คำปรึกษา แนะนำการลงทะเบียน ตรวจสอบเงื่อนไขการจบการศึกษา และช่วยจัดตารางเรียนให้คุณแล้วครับ! ลองเลือกวิชาทางซ้ายมือ หรือพิมพ์คำถามมาได้เลยครับ</div>')
html = html.replace('<input type="text" id="chat-input" placeholder="e.g., No Monday morning classes, prefer free Friday...">', '<input type="text" id="chat-input" data-i18n="chat-placeholder" placeholder="e.g., No Monday morning classes, prefer free Friday...">')
html = html.replace('<h1 style="font-size: 1.5rem; font-weight: 600; margin-bottom: 4px;">Curriculum Progress</h1>', '<h1 style="font-size: 1.5rem; font-weight: 600; margin-bottom: 4px;" data-i18n="prog-title">Curriculum Progress</h1>')
html = html.replace('<p style="color: var(--text-secondary); font-size: 0.85rem;">Actual earned-credit progress against the Data Science curriculum.</p>', '<p style="color: var(--text-secondary); font-size: 0.85rem;" data-i18n="prog-desc">Actual earned-credit progress against the Data Science curriculum.</p>')
html = html.replace(' Upload Transcript', ' <span data-i18n="upload-btn2">Upload Transcript</span>')
html = html.replace('<p style="font-weight: 500; font-size: 0.9rem;">Drop your transcript here, or click to browse</p>', '<p style="font-weight: 500; font-size: 0.9rem;" data-i18n="upload-drop">Drop your transcript here, or click to browse</p>')
html = html.replace('<p style="font-size: 0.75rem; color: var(--text-muted); margin-top: 4px;">Supports PDF, PNG, JPG for AI Processing</p>', '<p style="font-size: 0.75rem; color: var(--text-muted); margin-top: 4px;" data-i18n="upload-supports">Supports PDF, PNG, JPG for AI Processing</p>')
html = html.replace('<strong>Action Required</strong>', '<strong data-i18n="action-required">Action Required</strong>')
html = html.replace('<h3 class="group-title">General Education</h3>', '<h3 class="group-title" data-i18n="group-ge">General Education</h3>')
html = html.replace('<h3 class="group-title">Core & Major Courses</h3>', '<h3 class="group-title" data-i18n="group-core">Core & Major Courses</h3>')
html = html.replace('<h3 class="group-title">Other Requirements</h3>', '<h3 class="group-title" data-i18n="group-other">Other Requirements</h3>')

# also replace hardcoded INCOMPLETE/etc with span data-i18n if possible, but actually app.js rewrites them on transcript upload.
# I'll just change them in index.html to have data-i18n too.
html = html.replace('<span class="item-status incomplete">INCOMPLETE</span>', '<span class="item-status incomplete" data-i18n="status-incomplete">INCOMPLETE</span>')
html = html.replace('<span class="item-status option">OPTION REQUIRED</span>', '<span class="item-status option" data-i18n="status-option">OPTION REQUIRED</span>')
# I won't touch "credits remaining" here since it's mixed in the ID. I'll rely on app.js to fix it, or I can run a quick replace for them if needed.

with open('src/webapp/frontend/index.html', 'w') as f:
    f.write(html)

# 3. Update app.js
with open('src/webapp/frontend/app.js', 'r') as f:
    app = f.read()

app = app.replace('`วิชาที่ต้องเลือกสำหรับเทอมนี้`', 'window.t("courses-to-select")')
app = app.replace('`วิชาเอกเลือก (Major Electives) ที่เปิดสอน ${req_text}:`', 'window.t("major-elec-offered", {req: req_text})')
app = app.replace('`รายวิชาโท ${selectedMinor} ที่เปิดสอนเทอมนี้ ${req_text}:`', 'window.t("minor-offered", {minor: selectedMinor, req: req_text})')
app = app.replace('`หมวด ${short_name} ${req_text}:`', 'window.t("cat-req", {name: short_name, req: req_text})')
app = app.replace('`<div style="color: #fbbf24; font-size: 0.85rem;">⚠️ ไม่มีวิชาเอกเลือกเปิดสอนในเทอมนี้ หรือไม่ตรงกับแขนงที่เลือก</div>`', '`<div style="color: #fbbf24; font-size: 0.85rem;">${window.t("warn-no-major")}</div>`')
app = app.replace('`<div style="color: #fbbf24; font-size: 0.85rem;">⚠️ วิชาโท ${selectedMinor} ไม่มีวิชาเปิดสอนเทอมนี้เลย</div>`', '`<div style="color: #fbbf24; font-size: 0.85rem;">${window.t("warn-no-minor", {minor: selectedMinor})}</div>`')
app = app.replace('`<div style="color: #fbbf24; font-size: 0.85rem;">⚠️ ไม่มีวิชาเปิดสอน</div>`', '`<div style="color: #fbbf24; font-size: 0.85rem;">${window.t("warn-no-course")}</div>`')
app = app.replace('"พิมพ์รหัส/ชื่อวิชา (วิชาใดก็ได้)"', 'window.t("free-elec-placeholder")')
app = app.replace('`▶ กลุ่ม ${subName}`', 'window.t("group-name", {name: subName})')
app = app.replace(' (ผ่านแล้ว)', ' ${window.t("passed")}')
app = app.replace(' (ไม่มีวิชาแกนที่เปิดสอนและยังไม่ผ่าน)', ' ${window.t("no-core-left")}')
app = app.replace(' (ผ่านแล้ว)', ' ${window.t("passed")}') # Just in case

# Progress updates
app = app.replace('"INCOMPLETE"', 'window.t("status-incomplete")')
app = app.replace('"COMPLETE"', 'window.t("status-complete")')
app = app.replace('"OPTION REQUIRED"', 'window.t("status-option")')
app = app.replace(' credits remaining', ' ${window.t("credits-remaining")}')
app = app.replace('`${req - completed} credits remaining`', '`${req - completed} ${window.t("credits-remaining")}`')

# Listen for language change to re-render courses
app_add = """
window.addEventListener('languageChanged', () => {
    // Re-render courses if they are showing
    if (typeof updateCoursesUI === 'function') {
        try { document.getElementById('minor-select').dispatchEvent(new Event('change')); } catch(e){}
    }
    // Also we might want to re-render progress bars, but for simplicity we will just let the user re-upload or rely on static HTML translation.
});
"""
if "languageChanged" not in app:
    app += app_add

with open('src/webapp/frontend/app.js', 'w') as f:
    f.write(app)

