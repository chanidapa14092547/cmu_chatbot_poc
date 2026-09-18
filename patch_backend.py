import re

with open('src/webapp/backend/main.py', 'r') as f:
    backend = f.read()

new_instructions = """#### 3. Schedule Generation
*   **Prerequisite Verification (CRITICAL):** You MUST strictly trace Prerequisite chains. If a student fails or has not taken a course, they CANNOT take its successors. Pay EXTREME attention to direct sequential courses (e.g., if they fail Calculus 1, they CANNOT take Calculus 2. If they fail Basic Biology 1, they CANNOT take Basic Biology 2). Check the curriculum database carefully.
*   **Passed Courses:** NEVER recommend a course they have already passed.
*   **Time Clash Detection:** Carefully cross-check the days and times. A schedule MUST NOT have any overlapping times.
*   **Table Requirement:** The final schedule MUST be presented as a clean Markdown table with exact columns: `| Course Code | Course Name | Credits | Section | Day | Time | Instructor |`"""

backend = re.sub(r'#### 3\. Schedule Generation.*?#### 4\. Advisory Tone & Structure', new_instructions + '\\n\\n#### 4. Advisory Tone & Structure', backend, flags=re.DOTALL)

with open('src/webapp/backend/main.py', 'w') as f:
    f.write(backend)
