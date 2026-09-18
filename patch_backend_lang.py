with open('src/webapp/backend/main.py', 'r') as f:
    backend = f.read()

backend = backend.replace('**IMPORTANT:** Always respond to the user in **Thai language** (except for English course names or technical terms).', '**IMPORTANT:** Always respond to the user in the SAME LANGUAGE they used to ask the question (Thai or English), while keeping course names and technical terms in English.')

with open('src/webapp/backend/main.py', 'w') as f:
    f.write(backend)
