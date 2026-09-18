import re

with open('src/webapp/frontend/i18n.js', 'r') as f:
    i18n = f.read()

i18n = i18n.replace('"cat-minor": "Minor / No Minor"', '"cat-minor": "Minor Courses"')
i18n = i18n.replace('"cat-minor": "วิชาโท / เลือกเสรี (ไม่มีโท)"', '"cat-minor": "วิชาโท"')

with open('src/webapp/frontend/i18n.js', 'w') as f:
    f.write(i18n)

with open('src/webapp/frontend/index.html', 'r') as f:
    html = f.read()

html = html.replace('Minor / No Minor', 'Minor Courses')

with open('src/webapp/frontend/index.html', 'w') as f:
    f.write(html)
