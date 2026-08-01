import json
from pathlib import Path
import re

def validate_db():
    data_dir = Path("data/json_db")
    json_files = list(data_dir.rglob("*.json"))
    
    stats = {
        "total_files": len(json_files),
        "total_courses": 0,
        "missing_fields": 0,
        "empty_values": 0,
        "suspicious_prereqs": 0
    }
    
    errors = []

    required_keys = {"program_name", "major_tracks", "courses"}
    course_keys = {"course_code", "course_name_en", "course_name_th", "credits", "category_or_track", "prerequisites"}

    for jpath in json_files:
        try:
            with open(jpath, 'r', encoding='utf-8') as f:
                data = json.load(f)
        except Exception as e:
            errors.append(f"[{jpath.name}] JSON Parse Error: {e}")
            continue
            
        # Check main keys
        if not required_keys.issubset(data.keys()):
            stats["missing_fields"] += 1
            errors.append(f"[{jpath.name}] Missing root keys: {required_keys - data.keys()}")
            
        if not data.get("program_name"):
            stats["empty_values"] += 1
            
        courses = data.get("courses", [])
        stats["total_courses"] += len(courses)
        
        for idx, c in enumerate(courses):
            if not course_keys.issubset(c.keys()):
                stats["missing_fields"] += 1
                errors.append(f"[{jpath.name}] Course {idx} missing keys: {course_keys - c.keys()}")
            
            # Check empty values
            for k in course_keys:
                # course_name_th can be null
                if k != "course_name_th" and not c.get(k):
                    if c.get(k) != 0 and c.get(k) != "0": # 0 credits is technically allowed sometimes
                        stats["empty_values"] += 1
                        
            # Suspicious prereq format (e.g., huge blocks of text instead of 'None' or '261102')
            prereqs = c.get("prerequisites", [])
            if isinstance(prereqs, list):
                for p in prereqs:
                    if len(str(p)) > 100:  # Prereq shouldn't be a massive paragraph
                        stats["suspicious_prereqs"] += 1
                        
    print("=== Validation Summary ===")
    print(f"Total Curriculum Files: {stats['total_files']}")
    print(f"Total Courses Extracted: {stats['total_courses']}")
    print(f"Missing Fields Found: {stats['missing_fields']}")
    print(f"Empty/Null Required Values: {stats['empty_values']}")
    print(f"Suspicious Prerequisites (>100 chars): {stats['suspicious_prereqs']}")
    
    if errors:
        print("\n--- Sample Errors ---")
        for e in errors[:10]:
            print(e)
            
if __name__ == "__main__":
    validate_db()
