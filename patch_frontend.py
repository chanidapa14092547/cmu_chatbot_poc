import re

with open('src/webapp/frontend/app.js', 'r') as f:
    app_js = f.read()

# Fix 1: Stop translating short_name in args
app_js = app_js.replace(
    "label.setAttribute('data-i18n-args', JSON.stringify(req_courses > 0 ? {name: short_name_t, num: req_courses} : {name: short_name_t}));",
    "label.setAttribute('data-i18n-args', JSON.stringify(req_courses > 0 ? {name: short_name, num: req_courses} : {name: short_name}));"
)
app_js = app_js.replace(
    "summaryStandalone.setAttribute('data-i18n-args', JSON.stringify(req_courses > 0 ? {name: short_name_t, num: req_courses} : {name: short_name_t}));",
    "summaryStandalone.setAttribute('data-i18n-args', JSON.stringify(req_courses > 0 ? {name: short_name, num: req_courses} : {name: short_name}));"
)
app_js = app_js.replace(
    "summaryGe.setAttribute('data-i18n-args', JSON.stringify(req_courses > 0 ? {name: short_name_t, num: req_courses} : {name: short_name_t}));",
    "summaryGe.setAttribute('data-i18n-args', JSON.stringify(req_courses > 0 ? {name: short_name, num: req_courses} : {name: short_name}));"
)

# Fix 2: Add language awareness to prompt
prompt_logic = """    let promptText = `ช่วยจัดตารางเรียนให้หน่อย สำหรับ ${yearSelect.options[yearSelect.selectedIndex].text} ${termSelect.options[termSelect.selectedIndex].text}`;
    if (currentLang === 'en') {
        promptText = `Please generate a study schedule for ${yearSelect.options[yearSelect.selectedIndex].text} ${termSelect.options[termSelect.selectedIndex].text}`;
    }"""
app_js = app_js.replace('    let promptText = `ช่วยจัดตารางเรียนให้หน่อย สำหรับ ${yearSelect.options[yearSelect.selectedIndex].text} ${termSelect.options[termSelect.selectedIndex].text}`;', prompt_logic)

pass_logic = """    if (globalPassedCourses && globalPassedCourses.length > 0) {
        if (currentLang === 'en') {
            promptText += `\\n\\n(Courses already passed, do NOT recommend: ${globalPassedCourses.join(', ')})`;
        } else {
            promptText += `\\n\\n(วิชาที่สอบผ่านแล้ว ห้ามแนะนำเด็ดขาด: ${globalPassedCourses.join(', ')})`;
        }
    }"""
app_js = re.sub(r'    if \(globalPassedCourses && globalPassedCourses\.length > 0\) \{.*?    \}', pass_logic, app_js, flags=re.DOTALL)

fix_logic = """    if (fixedCourses.length > 0) {
        if (currentLang === 'en') {
            promptText += `\\n\\n(Compulsory courses already planned in the curriculum: ${fixedCourses.join(', ')})`;
        } else {
            promptText += `\\n\\n(วิชาบังคับที่จัดไว้ในหลักสูตรแล้วคือ: ${fixedCourses.join(', ')})`;
        }
    }"""
app_js = re.sub(r'    if \(fixedCourses\.length > 0\) \{.*?    \}', fix_logic, app_js, flags=re.DOTALL)

with open('src/webapp/frontend/app.js', 'w') as f:
    f.write(app_js)

# Fix 3: Translate v dynamically in i18n.js
with open('src/webapp/frontend/i18n.js', 'r') as f:
    i18n_js = f.read()

i18n_replace = """                    for (const [k, v] of Object.entries(parsedArgs)) {
                        let translatedV = i18n[currentLang][v] || v;
                        text = text.replace(`{${k}}`, translatedV);
                    }"""
i18n_js = i18n_js.replace('                    for (const [k, v] of Object.entries(parsedArgs)) {\n                        text = text.replace(`{${k}}`, v);\n                    }', i18n_replace)

with open('src/webapp/frontend/i18n.js', 'w') as f:
    f.write(i18n_js)
