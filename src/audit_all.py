import os
import json
import re

def audit_all():
    json_dir = "data/json_db"
    cond_dir = "data/conditions"
    
    total_jsons = 0
    total_mds = 0
    errors = []
    
    for root, _, files in os.walk(json_dir):
        for file in files:
            if not file.endswith(".json"): continue
            total_jsons += 1
            json_path = os.path.join(root, file)
            
            # MD filename format: exactly match JSON
            md_name = file.replace(".json", ".md")
            md_path = os.path.join(cond_dir, md_name)
            
            if os.path.exists(md_path):
                total_mds += 1
            else:
                errors.append(f"Missing .md condition for {json_path}")
                if "Veterinary" in json_path:
                    print(f"DEBUG: generated md_name = '{md_name}' but file does not exist at '{md_path}'")
                
            try:
                with open(json_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    
                courses = data.get("courses", [])
                if not courses:
                    errors.append(f"No courses found in {json_path}")
                    
                tracks = data.get("major_tracks", [])
                
                track_found_in_courses = set()
                
                for c in courses:
                    if "course_code" not in c or not c["course_code"]:
                        errors.append(f"Missing course_code in {json_path}")
                    
                    credits_str = str(c.get("credits", ""))
                    # Some credits are like "3" or "3(3-0-6)"
                    if not re.search(r'\d+', credits_str):
                        errors.append(f"Invalid credits '{credits_str}' in {json_path}")
                        
                    cat = c.get("category_or_track", "")
                    if not cat:
                        errors.append(f"Missing category_or_track for {c.get('course_code')} in {json_path}")
                    
                    if tracks:
                        for t in tracks:
                            if t.lower() in cat.lower():
                                track_found_in_courses.add(t)
                                
                if tracks and len(tracks) > 0 and tracks[0].lower() != "none":
                    # Check if at least one track was found in the courses
                    if len(track_found_in_courses) == 0:
                        errors.append(f"Tracks defined {tracks} but NO courses mapped to ANY track in {json_path}")
                    
            except Exception as e:
                errors.append(f"Error parsing {json_path}: {e}")
                
    print(f"Audited {total_jsons} JSON files and {total_mds} MD files.")
    if errors:
        print(f"Found {len(errors)} errors:")
        for e in errors[:50]:
            print("  -", e)
        if len(errors) > 50:
            print(f"  ... and {len(errors) - 50} more errors.")
    else:
        print("All data is perfectly formatted and mapped!")

if __name__ == "__main__":
    audit_all()
