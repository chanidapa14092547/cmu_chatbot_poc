import re

with open('src/webapp/backend/main.py', 'r') as f:
    backend = f.read()

old_str = "Pay EXTREME attention to direct sequential courses (e.g., if they fail Calculus 1, they CANNOT take Calculus 2. If they fail Basic Biology 1, they CANNOT take Basic Biology 2). Check the curriculum database carefully."
new_str = "This applies to ALL courses in the curriculum. Pay EXTREME attention to direct sequential courses (e.g., if they fail Calculus 1, they CANNOT take Calculus 2. If they fail Basic Biology 1, they CANNOT take Basic Biology 2). You MUST check the prerequisite field in the curriculum database for EVERY single course you recommend."

backend = backend.replace(old_str, new_str)

with open('src/webapp/backend/main.py', 'w') as f:
    f.write(backend)
