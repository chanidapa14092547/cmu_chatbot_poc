import os
import json
from parser import load_catalog, load_rules, parse_rules
from audit import evaluate_transcript

def main():
    base_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
    
    # File paths
    md_path = os.path.join(base_dir, "data", "conditions", "Bachelor_of_Science_Program_in_Data_Science_2567.md")
    json_path = os.path.join(base_dir, "data", "json_db", "Faculty of Science", "Bachelor of Science Program in Data Science (2567).json")
    transcript_path = os.path.join(os.path.dirname(__file__), "mock_transcript.json")
    
    print("🎓 CMU Smart Scheduler - Degree Audit PoC")
    print("-" * 50)
    
    # 1. Load Data
    print("Loading Catalog and Rules...")
    catalog = load_catalog(json_path)
    md_text = load_rules(md_path)
    
    with open(transcript_path, 'r') as f:
        transcript = json.load(f)
        
    print(f"Loaded {len(catalog['courses'])} courses from catalog.")
    print(f"Loaded {len(transcript)} courses from student transcript.")
    
    # 2. Parse Rules
    rules = parse_rules(md_text)
    print("\n[Graduation Rules from MD]")
    print(f"Major Compulsory Required: {rules['major_compulsory']} credits")
    print(f"Major Elective Required: {rules['major_elective']} credits")
    print(f"Free Elective Required: {rules['free_elective']} credits")
    
    # 3. Evaluate Transcript
    print("\n[Evaluating Transcript...]")
    results = evaluate_transcript(transcript, catalog, rules)
    
    # 4. Print Output
    print("-" * 50)
    print("📊 Degree Audit Results")
    print("-" * 50)
    for category, data in results.items():
        print(f"Category: {category.replace('_', ' ').title()}")
        print(f"  Earned: {data['earned']} / {data['required']} credits")
        if data.get('remaining') != "N/A":
            print(f"  Remaining: {data['remaining']} credits")
        print(f"  Status: {data.get('status', 'N/A')}")
        print(f"  Courses Taken: {', '.join(data['courses'])}")
        print("-" * 30)

if __name__ == "__main__":
    main()
