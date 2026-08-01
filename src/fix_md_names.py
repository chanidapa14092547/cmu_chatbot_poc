import os
import difflib
import shutil

json_dir = "data/json_db"
cond_dir = "data/conditions"

# Get all JSON base names
json_names = []
json_paths = {}
for root, _, files in os.walk(json_dir):
    for f in files:
        if f.endswith(".json"):
            base = f.replace(".json", "")
            json_names.append(base)
            json_paths[base] = os.path.join(root, f)

# Get all MD base names
md_names = []
for f in os.listdir(cond_dir):
    if f.endswith(".md"):
        md_names.append(f)

print(f"Total JSONs: {len(json_names)}")
print(f"Total MDs: {len(md_names)}")

mapped = set()

# Dry run matching
for md in md_names:
    md_base = md.replace(".md", "").replace("_", " ")
    
    # Fuzzy match against json_names
    matches = difflib.get_close_matches(md_base, json_names, n=1, cutoff=0.3)
    if matches:
        best_match = matches[0]
        mapped.add(best_match)
        print(f"MATCH: {md}  ->  {best_match}.md")
        # To rename:
        old_path = os.path.join(cond_dir, md)
        new_path = os.path.join(cond_dir, f"{best_match}.md")
        os.rename(old_path, new_path)
    else:
        print(f"NO MATCH FOR: {md}")

print("\n--- JSONs WITH NO MD FILE ---")
for j in json_names:
    if j not in mapped:
        print(j)
