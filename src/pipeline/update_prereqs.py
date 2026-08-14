import json
import re

json_path = "/Users/memee/.gemini/antigravity/scratch/cmu_chatbot_poc/data/json_db/Faculty of Science/Bachelor of Science Program in Data Science (2567).json"

extracted_data = {
  "001101": {"prerequisite": [], "condition_raw": "None"},
  "001102": {"prerequisite": [], "condition_raw": "None"},
  "001201": {"prerequisite": ["001101", "001102"], "condition_raw": "001101 or 001102 or e-Pro score of no less than B1; or consent of the department"},
  "001225": {"prerequisite": ["001101", "001102"], "condition_raw": "001101 or 001102 or e-Pro score of no less than B1; or consent of the department"},
  "204100": {"prerequisite": [], "condition_raw": "None"},
  "204217": {"prerequisite": ["204101", "204111", "229223"], "condition_raw": "204101 or 204111 or 229223"},
  "204252": {"prerequisite": ["204114", "204215", "204216", "204217", "204219"], "condition_raw": "204114 or 204215 or 204216 or 204217 or 204219"},
  "204306": {"prerequisite": [], "condition_raw": "third year standing"},
  "204383": {"prerequisite": ["204203", "204212", "204215", "204216", "204217", "204219", "229223", "206111"], "condition_raw": "204203 or 204212 or 204215 or 204216 or 204217 or 204219 or 229223; and 206111"},
  "204423": {"prerequisite": ["204251", "204252", "204271", "208150", "208263", "208264", "208269"], "condition_raw": "204251 or 204252 or 204271; and 208150 or 208263 or 208264 or 208269"},
  "204453": {"prerequisite": ["204251", "204271", "208150", "208263", "208264", "208269"], "condition_raw": "204251 or 204271; and 208150 or 208263 or 208264 or 208269"},
  "204472": {"prerequisite": ["204251", "204252", "204271", "208150", "208263", "208264", "208269"], "condition_raw": "204251 or 204252 or 204271; and 208150 or 208263 or 208264 or 208269"},
  "204483": {"prerequisite": ["204382", "204383"], "condition_raw": "204382 or 204383"},
  "206324": {"prerequisite": ["206111", "206161"], "condition_raw": "206111 or 206161 or consent of the department"},
  "206325": {"prerequisite": ["206112", "206203", "206261"], "condition_raw": "206112 or 206203 or 206261"},
  "206341": {"prerequisite": ["206112", "206116", "206203"], "condition_raw": "206112 or 206116 or 206203"},
  "206355": {"prerequisite": ["206112", "206116", "206203", "206261"], "condition_raw": "206112 or 206116 or 206203 or 206261"},
  "206370": {"prerequisite": ["206111", "206183", "206112"], "condition_raw": "206111 and 206183; or 206112"},
  "206471": {"prerequisite": ["206370", "208323"], "condition_raw": "206370 or 208323"},
  "208150": {"prerequisite": [], "condition_raw": "None"},
  "208251": {"prerequisite": ["208250", "206324"], "condition_raw": "208250 or 206324"},
  "208350": {"prerequisite": ["208250", "208263", "208270", "208272"], "condition_raw": "208250 or 208263 or 208270 or 208272"},
  "208451": {"prerequisite": ["208251"], "condition_raw": "208251"},
  "229123": {"prerequisite": [], "condition_raw": "None"},
  "229223": {"prerequisite": [], "condition_raw": "None"},
  "229352": {"prerequisite": ["229351"], "condition_raw": "229351"},
  "229496": {"prerequisite": [], "condition_raw": "fourth year standing and consent of the department"},
  "261461": {"prerequisite": ["261102", "269102", "229223"], "condition_raw": "261102 or 269102 or 229223"},
  "701181": {"prerequisite": [], "condition_raw": "None"},
  "702101": {"prerequisite": [], "condition_raw": "Non – Finance and Banking majors"},
  "703103": {"prerequisite": [], "condition_raw": "None"},
  "851103": {"prerequisite": [], "condition_raw": "None"},
  "951100": {"prerequisite": [], "condition_raw": "None"},
  "954471": {"prerequisite": ["954340", "204320"], "condition_raw": "954340 or 204320"},
  "954472": {"prerequisite": ["954340", "204320"], "condition_raw": "954340 or 204320"}
}

with open(json_path, 'r', encoding='utf-8') as f:
    curriculum = json.load(f)

for course in curriculum.get('courses', []):
    code = course.get('course_code')
    if code in extracted_data:
        course['prerequisites'] = extracted_data[code]['prerequisite']
        course['condition_raw'] = extracted_data[code]['condition_raw']

with open(json_path, 'w', encoding='utf-8') as f:
    json.dump(curriculum, f, ensure_ascii=False, indent=2)

print("Curriculum updated with conditions from images!")
