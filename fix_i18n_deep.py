import re

# 1. Update index.html
with open('src/webapp/frontend/index.html', 'r') as f:
    html = f.read()

html = html.replace('<div class="logo-sub">Data Science Track</div>', '<div class="logo-sub" data-i18n="logo-sub">Data Science Track</div>')
html = html.replace('<div class="nav-section">ACADEMIC REVIEW</div>', '<div class="nav-section" data-i18n="nav-review">ACADEMIC REVIEW</div>')
html = html.replace('<div class="user-name">Student Account</div>', '<div class="user-name" data-i18n="user-name">Student Account</div>')
html = html.replace('<div class="user-role">Undergraduate</div>', '<div class="user-role" data-i18n="user-role">Undergraduate</div>')
html = html.replace('<div class="header-title" id="header-title">Next Semester</div>', '<div class="header-title" id="header-title" data-i18n="header-title-next">Next Semester</div>')
html = re.sub(r'<button class="primary-btn"\s*id="generate-btn">([\s\S]*?)Generate Schedule</button>', r'<button class="primary-btn" id="generate-btn">\1<span data-i18n="btn-generate">Generate Schedule</span></button>', html)

with open('src/webapp/frontend/index.html', 'w') as f:
    f.write(html)

# 2. Update app.js
with open('src/webapp/frontend/app.js', 'r') as f:
    app = f.read()

# Make short_name translated
app = app.replace(
    'const short_name = ph.split(\'/\').pop().trim();',
    'const short_name = ph.split(\'/\').pop().trim();\n        const short_name_t = window.t(short_name);'
)

# Fix cat-req to use short_name_t
app = app.replace('JSON.stringify({name: short_name, req: req_text})', 'JSON.stringify({name: short_name_t, req: req_text})')
app = app.replace('{name: short_name, req: req_text}', '{name: short_name_t, req: req_text}')

# Fix header title dynamic switching
header_fix = """if (titleSpan && headerTitle) {
            if (element.id === 'nav-scheduler') headerTitle.setAttribute('data-i18n', 'header-title-next');
            else if (element.id === 'nav-progress') headerTitle.setAttribute('data-i18n', 'header-title-curr');
            headerTitle.innerText = titleSpan.innerText;"""
app = app.replace('if (titleSpan && headerTitle) {\n            headerTitle.innerText = titleSpan.innerText;', header_fix)

with open('src/webapp/frontend/app.js', 'w') as f:
    f.write(app)

# 3. Update i18n.js
with open('src/webapp/frontend/i18n.js', 'r') as f:
    i18n = f.read()

en_add = """
        "logo-sub": "Data Science Track",
        "nav-review": "ACADEMIC REVIEW",
        "user-name": "Student Account",
        "user-role": "Undergraduate",
        "btn-generate": "Generate Schedule",
        "Free Electives": "Free Electives",
        "Free Elective": "Free Elective",
        "Major Elective": "Major Elective",
        "Major Electives": "Major Electives",
        "Minor": "Minor",
        "General Education": "General Education",
"""
i18n = i18n.replace('"lbl-time": "Time Constraints",', '"lbl-time": "Time Constraints",' + en_add)

th_add = """
        "logo-sub": "สาขาวิทยาการข้อมูล",
        "nav-review": "ตรวจสอบวุฒิ",
        "user-name": "บัญชีนักศึกษา",
        "user-role": "ปริญญาตรี",
        "btn-generate": "จัดตารางเรียน",
        "Free Electives": "เลือกเสรี",
        "Free Elective": "เลือกเสรี",
        "Major Elective": "เอกเลือก",
        "Major Electives": "เอกเลือก",
        "Minor": "วิชาโท",
        "General Education": "ศึกษาทั่วไป (GE)",
"""
i18n = i18n.replace('"lbl-time": "เงื่อนไขเวลา",', '"lbl-time": "เงื่อนไขเวลา",' + th_add)

# Also fix the req-courses variable mismatch!
# The bug is: updateLanguage snapshots the translation with whatever req_text was when it rendered.
# We don't want to pass `req_text` which is already "(ต้องเลือก 1 วิชา)".
# We should pass `num: req_courses` instead of `req_text`!
# Let's write a replacement for app.js and i18n.js for that too.

with open('src/webapp/frontend/i18n.js', 'w') as f:
    f.write(i18n)

