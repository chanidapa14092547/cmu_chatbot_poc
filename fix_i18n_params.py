import re

# 1. Update app.js
with open('src/webapp/frontend/app.js', 'r') as f:
    app = f.read()

# Replace all the parameterized calls
replacements = [
    (
        r'window\.t\("minor-label",\s*\{name:\s*short_name_t,\s*req:\s*req_text\}\)',
        r'window.t(req_courses > 0 ? "minor-label-with-num" : "minor-label", req_courses > 0 ? {name: short_name_t, num: req_courses} : {name: short_name_t})'
    ),
    (
        r'setAttribute\(\'data-i18n\',\s*\'minor-label\'\);\n\s*label\.setAttribute\(\'data-i18n-args\',\s*JSON\.stringify\(\{name:\s*short_name_t,\s*req:\s*req_text\}\)\);',
        r'setAttribute(\'data-i18n\', req_courses > 0 ? "minor-label-with-num" : "minor-label");\n            label.setAttribute(\'data-i18n-args\', JSON.stringify(req_courses > 0 ? {name: short_name_t, num: req_courses} : {name: short_name_t}));'
    ),
    (
        r'window\.t\("major-elec-offered",\s*\{req:\s*req_text\}\)',
        r'window.t(req_courses > 0 ? "major-elec-offered-with-num" : "major-elec-offered", req_courses > 0 ? {num: req_courses} : {})'
    ),
    (
        r'setAttribute\(\'data-i18n\',\s*\'major-elec-offered\'\);\n\s*summary\.setAttribute\(\'data-i18n-args\',\s*JSON\.stringify\(\{req:\s*req_text\}\)\);',
        r'setAttribute(\'data-i18n\', req_courses > 0 ? "major-elec-offered-with-num" : "major-elec-offered");\n                    summary.setAttribute(\'data-i18n-args\', JSON.stringify(req_courses > 0 ? {num: req_courses} : {}));'
    ),
    (
        r'window\.t\("minor-offered",\s*\{minor:\s*selectedMinor,\s*req:\s*req_text\}\)',
        r'window.t(req_courses > 0 ? "minor-offered-with-num" : "minor-offered", req_courses > 0 ? {minor: selectedMinor, num: req_courses} : {minor: selectedMinor})'
    ),
    (
        r'setAttribute\(\'data-i18n\',\s*\'minor-offered\'\);\n\s*summaryMinor\.setAttribute\(\'data-i18n-args\',\s*JSON\.stringify\(\{minor:\s*selectedMinor,\s*req:\s*req_text\}\)\);',
        r'setAttribute(\'data-i18n\', req_courses > 0 ? "minor-offered-with-num" : "minor-offered");\n                        summaryMinor.setAttribute(\'data-i18n-args\', JSON.stringify(req_courses > 0 ? {minor: selectedMinor, num: req_courses} : {minor: selectedMinor}));'
    ),
    (
        r'window\.t\("cat-req",\s*\{name:\s*short_name_t,\s*req:\s*req_text\}\)',
        r'window.t(req_courses > 0 ? "cat-req-with-num" : "cat-req", req_courses > 0 ? {name: short_name_t, num: req_courses} : {name: short_name_t})'
    ),
    (
        r'setAttribute\(\'data-i18n\',\s*\'cat-req\'\);\n\s*(summaryStandalone|label|summaryGe)\.setAttribute\(\'data-i18n-args\',\s*JSON\.stringify\(\{name:\s*short_name_t,\s*req:\s*req_text\}\)\);',
        r'setAttribute(\'data-i18n\', req_courses > 0 ? "cat-req-with-num" : "cat-req");\n            \1.setAttribute(\'data-i18n-args\', JSON.stringify(req_courses > 0 ? {name: short_name_t, num: req_courses} : {name: short_name_t}));'
    ),
]

for old, new in replacements:
    app = re.sub(old, new, app)

with open('src/webapp/frontend/app.js', 'w') as f:
    f.write(app)

# 2. Update i18n.js
with open('src/webapp/frontend/i18n.js', 'r') as f:
    i18n = f.read()

en_add = """
        "cat-req-with-num": "{name} category (must choose {num} course(s)):",
        "minor-label-with-num": "{name} category (must choose {num} course(s)): Select Minor or Major Elective:",
        "major-elec-offered-with-num": "Major Electives offered (must choose {num} course(s)):",
        "minor-offered-with-num": "{minor} Minor courses offered (must choose {num} course(s)):",
"""
i18n = i18n.replace('"cat-req": "{name} category {req}:",', '"cat-req": "{name} category:",' + en_add)
i18n = i18n.replace('"minor-label": "{name} category {req}: Select Minor or Major Elective:",', '"minor-label": "{name} category: Select Minor or Major Elective:",')
i18n = i18n.replace('"major-elec-offered": "Major Electives offered {req}:",', '"major-elec-offered": "Major Electives offered:",')
i18n = i18n.replace('"minor-offered": "{minor} Minor courses offered {req}:",', '"minor-offered": "{minor} Minor courses offered:",')

th_add = """
        "cat-req-with-num": "หมวด {name} (ต้องเลือก {num} วิชา):",
        "minor-label-with-num": "หมวด {name} (ต้องเลือก {num} วิชา): เลือกแขนงวิชาโท หรือ เอกเลือก:",
        "major-elec-offered-with-num": "วิชาเอกเลือกที่เปิดสอน (ต้องเลือก {num} วิชา):",
        "minor-offered-with-num": "วิชาโท {minor} ที่เปิดสอน (ต้องเลือก {num} วิชา):",
"""
i18n = i18n.replace('"cat-req": "หมวด {name} {req}:",', '"cat-req": "หมวด {name}:",' + th_add)
i18n = i18n.replace('"minor-label": "หมวด {name} {req}: เลือกแขนงวิชาโท หรือ เอกเลือก:",', '"minor-label": "หมวด {name}: เลือกแขนงวิชาโท หรือ เอกเลือก:",')
i18n = i18n.replace('"major-elec-offered": "วิชาเอกเลือกที่เปิดสอน {req}:",', '"major-elec-offered": "วิชาเอกเลือกที่เปิดสอน:",')
i18n = i18n.replace('"minor-offered": "วิชาโท {minor} ที่เปิดสอน {req}:",', '"minor-offered": "วิชาโท {minor} ที่เปิดสอน:",')

with open('src/webapp/frontend/i18n.js', 'w') as f:
    f.write(i18n)
