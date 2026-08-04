import os
import json
import glob

def build_index():
    base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    json_db_dir = os.path.join(base_dir, "data", "json_db")
    conditions_dir = os.path.join(base_dir, "data", "conditions")
    
    catalog_index = {}
    
    # Iterate through all faculties
    if not os.path.exists(json_db_dir):
        print(f"Error: Directory {json_db_dir} does not exist.")
        return

    faculties = [f for f in os.listdir(json_db_dir) if os.path.isdir(os.path.join(json_db_dir, f))]
    
    for faculty in faculties:
        catalog_index[faculty] = {}
        faculty_dir = os.path.join(json_db_dir, faculty)
        json_files = glob.glob(os.path.join(faculty_dir, "*.json"))
        
        for json_file in json_files:
            try:
                with open(json_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    program_name = data.get("program_name", "Unknown Program")
                    
                    # Create a friendly key for the UI (using the filename without extension)
                    file_basename = os.path.basename(json_file).replace(".json", "")
                    
                    # Check if MD file exists
                    md_path = os.path.join(conditions_dir, f"{file_basename}.md")
                    has_conditions = os.path.exists(md_path)
                    
                    catalog_index[faculty][file_basename] = {
                        "program_name": program_name,
                        "json_path": os.path.relpath(json_file, base_dir),
                        "md_path": os.path.relpath(md_path, base_dir) if has_conditions else None,
                        "major_tracks": data.get("major_tracks", [])
                    }
            except Exception as e:
                print(f"Error processing {json_file}: {e}")
                
    # Save the index
    output_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "catalog_index.json")
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(catalog_index, f, ensure_ascii=False, indent=2)
        
    print(f"Successfully built catalog index with {len(faculties)} faculties.")
    print(f"Saved to {output_path}")

if __name__ == "__main__":
    build_index()
