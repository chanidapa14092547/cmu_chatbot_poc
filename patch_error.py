with open('src/webapp/frontend/app.js', 'r') as f:
    app_js = f.read()

app_js = app_js.replace(
    'Failed to load data from backend. Ensure FastAPI is running on port 8000.',
    'Failed to load data from backend: ${error.message}'
)

with open('src/webapp/frontend/app.js', 'w') as f:
    f.write(app_js)
