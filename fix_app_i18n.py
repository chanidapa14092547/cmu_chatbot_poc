import re

# Fix app.js
with open('src/webapp/frontend/app.js', 'r') as f:
    app = f.read()

# Remove the dynamic population of tracks
app = re.sub(
    r'// Populate Major Tracks if available[\s\S]*?if \(majorTracksList && majorTracksList\.length > 0\) \{[\s\S]*?majorTracksList\.forEach\(track => \{[\s\S]*?const opt = document\.createElement\(\'option\'\);[\s\S]*?opt\.value = track;[\s\S]*?opt\.textContent = track;[\s\S]*?majorTrackSelect\.appendChild\(opt\);[\s\S]*?\}\);[\s\S]*?\}',
    '// Populate Major Tracks (Skipped to avoid duplication, using hardcoded options in index.html)',
    app
)

# Change req_text to use i18n
app = app.replace(
    'const req_text = req_courses > 0 ? `(ต้องเลือก ${req_courses} วิชา)` : "";',
    'const req_text = req_courses > 0 ? window.t("req-courses", {num: req_courses}) : "";'
)

with open('src/webapp/frontend/app.js', 'w') as f:
    f.write(app)

# Fix i18n.js
with open('src/webapp/frontend/i18n.js', 'r') as f:
    i18n = f.read()

# Replace minor-label in EN
i18n = i18n.replace(
    '"minor-label": "{name} category ({req}): Select Minor or Major Elective:",',
    '"minor-label": "{name} category {req}: Select Minor or Major Elective:",'
)
# Replace minor-label in TH
i18n = i18n.replace(
    '"minor-label": "หมวด {name} ({req}): เลือกแขนงวิชาโท หรือ เอกเลือก:",',
    '"minor-label": "หมวด {name} {req}: เลือกแขนงวิชาโท หรือ เอกเลือก:",'
)

# Replace minor-none in EN
i18n = i18n.replace(
    '"minor-none": "Major Electives (No Minor)",',
    '"minor-none": "Major Elective",'
)
# Replace minor-none in TH
i18n = i18n.replace(
    '"minor-none": "เลือกเป็นเอกเลือก (ไม่ลงโท)",',
    '"minor-none": "เลือกลงเป็นวิชาเอกเลือก (Major Elective)",'
)

# Add req-courses translation
en_add = """
        "req-courses": "(must choose {num} course(s))",
"""
i18n = i18n.replace('"quick-sched": "🛠️ Quick Scheduler",', '"quick-sched": "🛠️ Quick Scheduler",' + en_add)

th_add = """
        "req-courses": "(ต้องเลือก {num} วิชา)",
"""
i18n = i18n.replace('"quick-sched": "🛠️ จัดตารางแบบด่วน",', '"quick-sched": "🛠️ จัดตารางแบบด่วน",' + th_add)

with open('src/webapp/frontend/i18n.js', 'w') as f:
    f.write(i18n)

