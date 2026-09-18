import re

with open('src/webapp/frontend/i18n.js', 'r') as f:
    i18n = f.read()

# Add to English
en_add = """
        "quick-sched": "🛠️ Quick Scheduler",
        "lbl-year": "Academic Year",
        "lbl-term": "Term",
        "lbl-track": "Focus Area (Track)",
        "lbl-time": "Time Constraints",
        "plh-time": "e.g., No Monday morning",
        "minor-label": "{name} category ({req}): Select Minor or Major Elective:",
        "minor-none": "Major Electives (No Minor)",
"""
i18n = i18n.replace('"btn-lang": "🇹🇭 เปลี่ยนเป็นภาษาไทย",', '"btn-lang": "🇹🇭 เปลี่ยนเป็นภาษาไทย",' + en_add)

# Add to Thai
th_add = """
        "quick-sched": "🛠️ จัดตารางแบบด่วน",
        "lbl-year": "ชั้นปีที่",
        "lbl-term": "เทอม",
        "lbl-track": "แขนงวิชาเอก (Track)",
        "lbl-time": "เงื่อนไขเวลา",
        "plh-time": "เช่น ไม่เรียนเช้าวันจันทร์",
        "minor-label": "หมวด {name} ({req}): เลือกแขนงวิชาโท หรือ เอกเลือก:",
        "minor-none": "เลือกเป็นเอกเลือก (ไม่ลงโท)",
"""
i18n = i18n.replace('"btn-lang": "🇬🇧 Switch to English",', '"btn-lang": "🇬🇧 Switch to English",' + th_add)

with open('src/webapp/frontend/i18n.js', 'w') as f:
    f.write(i18n)

# Update index.html
with open('src/webapp/frontend/index.html', 'r') as f:
    html = f.read()

html = html.replace('<h2>🛠️ Quick Scheduler</h2>', '<h2 data-i18n="quick-sched">🛠️ Quick Scheduler</h2>')
html = html.replace('<label for="year-select">Academic Year</label>', '<label for="year-select" data-i18n="lbl-year">Academic Year</label>')
html = html.replace('<label for="term-select">Term</label>', '<label for="term-select" data-i18n="lbl-term">Term</label>')
html = html.replace('<label for="major-track">Focus Area (กลุ่มวิชาเอก)</label>', '<label for="major-track" data-i18n="lbl-track">Focus Area (กลุ่มวิชาเอก)</label>')
html = html.replace('<label for="time-constraints">Time Constraints</label>', '<label for="time-constraints" data-i18n="lbl-time">Time Constraints</label>')
html = html.replace('<input type="text" id="time-constraints" placeholder="e.g. No Monday morning">', '<input type="text" id="time-constraints" data-i18n="plh-time" placeholder="e.g. No Monday morning">')

with open('src/webapp/frontend/index.html', 'w') as f:
    f.write(html)

# Update app.js
with open('src/webapp/frontend/app.js', 'r') as f:
    app = f.read()

app = app.replace('`หมวด ${short_name} ${req_text}: เลือกแขนงวิชาโท หรือ เอกเลือก:`', 'window.t("minor-label", {name: short_name, req: req_text})')
app = app.replace('"เลือกเป็นเอกเลือก (ไม่ลงโท)"', 'window.t("minor-none")')
# Also the track options:
app = app.replace('<option value="Mathematics">Mathematics (คณิตศาสตร์)</option>', '<option value="Mathematics">คณิตศาสตร์ (Mathematics)</option>')
app = app.replace('<option value="Statistics">Statistics (สถิติ)</option>', '<option value="Statistics">สถิติ (Statistics)</option>')
app = app.replace('<option value="Computer Science">Computer Science (คอมพิวเตอร์)</option>', '<option value="Computer Science">วิทยาการคอมพิวเตอร์ (CS)</option>')

with open('src/webapp/frontend/app.js', 'w') as f:
    f.write(app)
