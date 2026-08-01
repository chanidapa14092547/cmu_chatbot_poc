import json
import re

def load_catalog(json_path):
    """Load the course catalog JSON file for a specific major."""
    with open(json_path, 'r', encoding='utf-8') as f:
        return json.load(f)

def load_rules(md_path):
    """Load the markdown rules file."""
    with open(md_path, 'r', encoding='utf-8') as f:
        return f.read()

def parse_rules(md_text):
    """
    Parse the graduation rules from the markdown text using regex.
    This is a Proof of Concept parser.
    """
    rules = {
        "major_compulsory": 0,
        "major_elective": 0,
        "free_elective": 0,
        "minor": 0
    }
    
    # Extract Compulsory (วิชาเอกบังคับ)
    match = re.search(r'วิชาเอกบังคับ\s*(\d+)', md_text)
    if match:
        rules['major_compulsory'] = int(match.group(1))
        
    # Extract Major Elective (วิชาเอกเลือก)
    match = re.search(r'วิชาเอกเลือก\s*ไม่น้อยกว่า\s*(\d+)', md_text)
    if match:
        rules['major_elective'] = int(match.group(1))
        
    # Extract Free Elective (วิชาเลือกเสรี)
    match = re.search(r'วิชาเลือกเสรี\s*ไม่น้อยกว่า\s*(\d+)', md_text)
    if match:
        rules['free_elective'] = int(match.group(1))
        
    # Extract Minor (วิชาโท)
    match = re.search(r'วิชาโท\s*\(ถ้ามี\)\s*ไม่น้อยกว่า\s*(\d+)', md_text)
    if match:
        rules['minor'] = int(match.group(1))
        
    return rules
