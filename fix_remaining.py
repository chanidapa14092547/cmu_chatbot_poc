import re

with open('src/webapp/frontend/index.html', 'r') as f:
    html = f.read()

# E.g. >15 credits remaining</span>
html = re.sub(r'>(\d+) credits remaining</span>', r'>\1 <span data-i18n="credits-remaining">credits remaining</span></span>', html)

with open('src/webapp/frontend/index.html', 'w') as f:
    f.write(html)
