import json
import os
import sys

def check_time_conflict(sec1, sec2):
    """Simple check if two sections conflict in time."""
    # Check if they share any days
    days1 = set(sec1['day'].split(','))
    days2 = set(sec2['day'].split(','))
    
    if not days1.intersection(days2):
        return False
        
    def to_minutes(t):
        h, m = map(int, t.split(':'))
        return h * 60 + m
        
    start1, end1 = to_minutes(sec1['time_start']), to_minutes(sec1['time_end'])
    start2, end2 = to_minutes(sec2['time_start']), to_minutes(sec2['time_end'])
    
    if start1 < end2 and start2 < end1:
        return True
    return False

def check_track_courses():
    base_dir = os.path.dirname(os.path.dirname(__file__))
    json_path = os.path.join(base_dir, "data", "json_db", "Faculty of Science", "Bachelor of Science Program in Data Science (2567).json")
    schedule_path = os.path.join(base_dir, "src", "logic_engine", "mock_schedule.json")
    
    with open(json_path, 'r', encoding='utf-8') as f:
        catalog = json.load(f)
        
    with open(schedule_path, 'r', encoding='utf-8') as f:
        schedule = json.load(f)

    # 1. User selects "เอกคอม" (computational modeling)
    track_keyword = "computational modeling"
    print(f"🙋‍♂️ คำถาม: ถ้าเลือกเอกคอม (Track: {track_keyword}) สามารถเลือกลงวิชาไหนได้บ้าง และมีวิชาไหนชนกันไหม?")
    print("-" * 60)
    
    # 2. Filter courses for this track
    track_courses = []
    for c in catalog['courses']:
        cat = c.get('category_or_track', '')
        if track_keyword.lower() in cat.lower():
            track_courses.append(c)

    print(f"📚 วิชาในหมวดนี้ทั้งหมดมี {len(track_courses)} วิชา")
    
    # 3. Filter by available schedule
    available_courses = [c for c in track_courses if c['course_code'] in schedule]
    print(f"✅ เทอมนี้เปิดสอน {len(available_courses)} วิชา ได้แก่:")
    for c in available_courses:
        print(f"   - {c['course_code']} {c['course_name_en']} ({c['course_name_th']})")
        for sec in schedule[c['course_code']]['sections']:
            print(f"     >> Sec {sec['sec']}: {sec['day']} {sec['time_start']}-{sec['time_end']}")

    if len(available_courses) < 2:
        print("\nไม่มีวิชามากพอที่จะเช็คชนกันได้ครับ")
        return

    print("-" * 60)
    print("⚡ ตรวจสอบตารางสอนที่ชนกัน (Collision Check):")
    
    # 4. Check collisions between all available sections of these courses
    conflicts_found = False
    for i in range(len(available_courses)):
        for j in range(i + 1, len(available_courses)):
            c1 = available_courses[i]
            c2 = available_courses[j]
            
            for sec1 in schedule[c1['course_code']]['sections']:
                for sec2 in schedule[c2['course_code']]['sections']:
                    if check_time_conflict(sec1, sec2):
                        conflicts_found = True
                        print(f"❌ ชนกัน! {c1['course_code']} (Sec {sec1['sec']}) ชนกับ {c2['course_code']} (Sec {sec2['sec']})")
                        print(f"   - เวลา: {sec1['day']} {sec1['time_start']}-{sec1['time_end']} ชนกับ {sec2['day']} {sec2['time_start']}-{sec2['time_end']}")
                        
    if not conflicts_found:
        print("✅ ไม่มีวิชาไหนในหมวดนี้ที่เวลาเรียนชนกันเลย สามารถลงควบได้เลยครับ!")

if __name__ == "__main__":
    check_track_courses()
