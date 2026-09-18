import re

# Fix app.js
with open('src/webapp/frontend/app.js', 'r') as f:
    app = f.read()

app = app.replace(
    'title.textContent = "วิชาที่ต้องเลือกสำหรับเทอมนี้ (แสดงเฉพาะที่เปิดสอน):";',
    'title.textContent = window.t("courses-to-select");'
)
app = app.replace(
    'input.placeholder = "พิมพ์รหัส/ชื่อวิชา หรือเว้นว่างให้ AI แนะนำ";',
    'input.placeholder = window.t("free-elec-placeholder2");'
)
with open('src/webapp/frontend/app.js', 'w') as f:
    f.write(app)

# Fix i18n.js
with open('src/webapp/frontend/i18n.js', 'r') as f:
    i18n = f.read()

i18n = i18n.replace(
    '"courses-to-select": "Courses to select this semester",',
    '"courses-to-select": "Courses to select this semester (Offered only):",'
)
i18n = i18n.replace(
    '"courses-to-select": "วิชาที่ต้องเลือกสำหรับเทอมนี้",',
    '"courses-to-select": "วิชาที่ต้องเลือกสำหรับเทอมนี้ (แสดงเฉพาะที่เปิดสอน):",'
)

i18n = i18n.replace(
    '"cat-req": "{name} category ({req}):",',
    '"cat-req": "{name} category {req}:",'
)
i18n = i18n.replace(
    '"cat-req": "หมวด {name} ({req}):",',
    '"cat-req": "หมวด {name} {req}:",'
)

# Add free-elec-placeholder2
en_add = """
        "free-elec-placeholder": "Type course code/name (any course)",
        "free-elec-placeholder2": "Type course code/name, or leave blank for AI to suggest",
"""
i18n = i18n.replace('"free-elec-placeholder": "Type course code/name (any course)",', en_add)

th_add = """
        "free-elec-placeholder": "พิมพ์รหัส/ชื่อวิชา (วิชาใดก็ได้)",
        "free-elec-placeholder2": "พิมพ์รหัส/ชื่อวิชา หรือเว้นว่างให้ AI แนะนำ",
"""
i18n = i18n.replace('"free-elec-placeholder": "พิมพ์รหัส/ชื่อวิชา (วิชาใดก็ได้)",', th_add)

with open('src/webapp/frontend/i18n.js', 'w') as f:
    f.write(i18n)

