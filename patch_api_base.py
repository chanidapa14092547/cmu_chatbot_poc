with open('src/webapp/frontend/app.js', 'r') as f:
    app_js = f.read()

app_js = app_js.replace(
    'const API_BASE = window.location.hostname === "localhost" || window.location.hostname === "127.0.0.1" \n    ? "http://localhost:8000/api" \n    : "https://cmu-chatbot-poc.onrender.com/api";',
    'const API_BASE = "https://cmu-chatbot-poc.onrender.com/api"; // Force use production API for testing'
)

with open('src/webapp/frontend/app.js', 'w') as f:
    f.write(app_js)
