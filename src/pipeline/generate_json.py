import json
import re

def parse_markdown():
    with open('/Users/memee/.gemini/antigravity/brain/2841b509-7aa0-400e-b3b2-e234614fe2ae/verification_report.md', 'r', encoding='utf-8') as f:
        content = f.read()

    data = []
    current_faculty = None
    current_program = None
    current_minor = None

    lines = content.split('\n')
    
    for i, line in enumerate(lines):
        line = line.strip()
        if not line:
            if current_minor and current_minor['parsing_req']:
                current_minor['requirements_th'] += '\n'
            continue
            
        if line.startswith('## '):
            current_faculty = {
                'faculty': line[3:].strip(),
                'programs': []
            }
            data.append(current_faculty)
            current_program = None
            current_minor = None
            
        elif line.startswith('### '):
            current_program = {
                'program_name': line[4:].strip(),
                'minors': []
            }
            if current_faculty is not None:
                current_faculty['programs'].append(current_program)
            current_minor = None
            
        elif line.startswith('#### '):
            # E.g. "#### 1. กฎหมาย (Law)"
            minor_name = line[5:].strip()
            # Remove leading numbers like "1. "
            minor_name = re.sub(r'^\d+\.\s*', '', minor_name)
            current_minor = {
                'minor_name': minor_name,
                'requirements_th': '',
                'parsing_req': False
            }
            if current_program is None and current_faculty is not None:
                # Some faculties might not have a ### program heading, fallback
                current_program = {
                    'program_name': 'วิชาโทที่เปิดสอนสำหรับนักศึกษาทั่วไป',
                    'minors': []
                }
                current_faculty['programs'].append(current_program)
            
            if current_program is not None:
                current_program['minors'].append(current_minor)
                
        elif line.startswith('**รายละเอียดวิชาโท (TH):**'):
            if current_minor is not None:
                current_minor['parsing_req'] = True
                
        elif current_minor is not None and current_minor.get('parsing_req'):
            # Stop if we hit next section
            if line.startswith('#'):
                current_minor['parsing_req'] = False
            else:
                if current_minor['requirements_th']:
                    current_minor['requirements_th'] += '\n'
                current_minor['requirements_th'] += line

    # Cleanup trailing newlines in requirements
    for f in data:
        for p in f['programs']:
            for m in p['minors']:
                m['requirements_th'] = m['requirements_th'].strip()
                del m['parsing_req']

    import os
    os.makedirs('/Users/memee/.gemini/antigravity/scratch/cmu_chatbot_poc/data/json_db', exist_ok=True)
    with open('/Users/memee/.gemini/antigravity/scratch/cmu_chatbot_poc/data/json_db/Minors.json', 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
        
    print(f"Successfully generated Minors.json with {len(data)} faculties.")

if __name__ == '__main__':
    parse_markdown()
