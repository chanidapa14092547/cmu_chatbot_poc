import json

json_path = "/Users/memee/.gemini/antigravity/scratch/cmu_chatbot_poc/data/json_db/Faculty of Science/Bachelor of Science Program in Data Science (2567).json"

with open(json_path, 'r', encoding='utf-8') as f:
    curriculum = json.load(f)

# Update 229496 Cooperative Education
for course in curriculum.get('courses', []):
    if course['course_code'] == '229496':
        course['prerequisites'] = ["fourth year standing and consent of the department"]
        course['condition_raw'] = "fourth year standing and consent of the department"
        break

with open(json_path, 'w', encoding='utf-8') as f:
    json.dump(curriculum, f, ensure_ascii=False, indent=2)

print("Updated 229496 in JSON.")
