import json

json_path = "/Users/memee/.gemini/antigravity/scratch/cmu_chatbot_poc/data/json_db/Faculty of Science/Bachelor of Science Program in Data Science (2567).json"

with open(json_path, 'r', encoding='utf-8') as f:
    curriculum = json.load(f)

# The user noted that study_plan is missing category selection placeholders
# We will convert the study plan into a mixed list of strings (specific course IDs)
# and dictionaries (category placeholders).

# Update Year 1 Semester 1 with Basic Science
y1s1 = curriculum['study_plan']['year_1_semester_1']
if "001101" in y1s1: # Ensure we're not duplicating
    # Check if placeholder already exists
    has_basic = any(isinstance(x, dict) and x.get('category_placeholder') == 'Field of Specialization / Core Courses / Basic Science Courses' for x in y1s1)
    if not has_basic:
        curriculum['study_plan']['year_1_semester_1'].append({
            "category_placeholder": "Field of Specialization / Core Courses / Basic Science Courses",
            "credits_required": 3,
            "condition_raw": "Select from 202101, 203103, 207187"
        })

with open(json_path, 'w', encoding='utf-8') as f:
    json.dump(curriculum, f, ensure_ascii=False, indent=2)

print("Updated Year 1 Semester 1 study plan with category placeholder!")
