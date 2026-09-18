import re

# Fix i18n.js
with open('src/webapp/frontend/i18n.js', 'r') as f:
    i18n = f.read()

replacement = """function updateLanguage() {
    document.querySelectorAll('[data-i18n]').forEach(el => {
        const key = el.getAttribute('data-i18n');
        if (i18n[currentLang][key]) {
            let text = i18n[currentLang][key];
            const args = el.getAttribute('data-i18n-args');
            if (args) {
                try {
                    const parsedArgs = JSON.parse(args.replace(/&quot;/g, '"'));
                    for (const [k, v] of Object.entries(parsedArgs)) {
                        text = text.replace(`{${k}}`, v);
                    }
                } catch(e) {}
            }
            if (el.tagName.toLowerCase() === 'input' && el.type === 'text') {
                el.placeholder = text;
            } else {
                el.innerHTML = text;
            }
        }
    });"""

i18n = re.sub(r'function updateLanguage\(\) \{[\s\S]*?el\.innerHTML = i18n\[currentLang\]\[key\];\n            \}\n        \}\n    \}\);', replacement, i18n)

with open('src/webapp/frontend/i18n.js', 'w') as f:
    f.write(i18n)


# Fix app.js
with open('src/webapp/frontend/app.js', 'r') as f:
    app = f.read()

# Replace assignments with function calls that also set attributes
def repl(match):
    indent = match.group(1)
    element = match.group(2)
    prop = match.group(3)
    key = match.group(4)
    args = match.group(5)
    
    res = f"{indent}{element}.{prop} = window.t(\"{key}\""
    if args:
        res += f", {args});\n"
        res += f"{indent}{element}.setAttribute('data-i18n', '{key}');\n"
        res += f"{indent}{element}.setAttribute('data-i18n-args', JSON.stringify({args}));"
    else:
        res += f");\n"
        res += f"{indent}{element}.setAttribute('data-i18n', '{key}');"
    return res

app = re.sub(r'^(\s+)([a-zA-Z0-9_]+)\.(textContent|placeholder)\s*=\s*window\.t\("([^"]+)"(?:,\s*(\{.*?\}))?\);', repl, app, flags=re.MULTILINE)

with open('src/webapp/frontend/app.js', 'w') as f:
    f.write(app)
