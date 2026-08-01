import json
import os

def check_time_conflict(sec1, sec2):
    """Simple check if two sections conflict in time."""
    # Check if they share any days
    days1 = set(sec1['day'].split(','))
    days2 = set(sec2['day'].split(','))
    
    if not days1.intersection(days2):
        return False # Different days, no conflict
        
    # If same day, check time overlap
    # Format HH:MM -> convert to minutes for easy comparison
    def to_minutes(t):
        h, m = map(int, t.split(':'))
        return h * 60 + m
        
    start1, end1 = to_minutes(sec1['time_start']), to_minutes(sec1['time_end'])
    start2, end2 = to_minutes(sec2['time_start']), to_minutes(sec2['time_end'])
    
    # Overlap logic
    if start1 < end2 and start2 < end1:
        return True
    return False

def main():
    base_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
    json_path = os.path.join(base_dir, "data", "json_db", "Faculty of Science", "Bachelor of Science Program in Data Science (2567).json")
    schedule_path = os.path.join(os.path.dirname(__file__), "mock_schedule.json")
    
    with open(json_path, 'r', encoding='utf-8') as f:
        catalog = json.load(f)
        
    with open(schedule_path, 'r', encoding='utf-8') as f:
        schedule = json.load(f)
        
    print("🙋‍♂️ คำถาม: มีวิชา 'เอกเลือก' อะไรเปิดบ้าง และถ้าจะลงเรียน มันชนกันไหม?")
    print("-" * 60)
    
    # 1. หาว่ามีวิชาไหนเป็น "เอกเลือก" บ้าง
    major_electives = [c for c in catalog['courses'] if 'Major Elective' in c['category_or_track']]
    print(f"📚 ระบบพบวิชา 'เอกเลือก' ในฐานข้อมูลทั้งหมด: {len(major_electives)} วิชา")
    
    # 2. คัดเฉพาะวิชาที่เปิดสอนในตาราง (mock schedule)
    available_courses = [c for c in major_electives if c['course_code'] in schedule]
    print(f"✅ แต่เทอมนี้เปิดสอนแค่ {len(available_courses)} วิชา ได้แก่:")
    for c in available_courses:
        print(f"   - {c['course_code']}: {c['course_name_en']}")
        
    print("-" * 60)
    print("⚡ ตรวจสอบตารางสอนที่ชนกัน (Schedule Collision Check)")
    
    # Example: Check conflicts
    target_course_1 = schedule['204426']['sections'][0] # Data Eng Sec 001 (M,Th 09:30)
    target_course_2 = schedule['204471']['sections'][0] # AI Sec 001 (M,Th 09:30)
    target_course_3 = schedule['261441']['sections'][0] # IoT Sec 001 (W 09:00)
    
    print("\nสมมติว่านักศึกษาเลือก:")
    print(f"1. 204426 Data Engineering [Sec 001: {target_course_1['day']} {target_course_1['time_start']}-{target_course_1['time_end']}]")
    print(f"2. 204471 Artificial Intelligence [Sec 001: {target_course_2['day']} {target_course_2['time_start']}-{target_course_2['time_end']}]")
    
    if check_time_conflict(target_course_1, target_course_2):
        print("❌ ผลลัพธ์: ลงไม่ได้ครับ! เวลาเรียนชนกัน")
    else:
        print("✅ ผลลัพธ์: ลงได้ครับ เวลาไม่ชน")
        
    print("\nสมมติว่านักศึกษาเปลี่ยนไปเลือก:")
    print(f"1. 204426 Data Engineering [Sec 002: {schedule['204426']['sections'][1]['day']} {schedule['204426']['sections'][1]['time_start']}-{schedule['204426']['sections'][1]['time_end']}]")
    print(f"2. 204471 Artificial Intelligence [Sec 001: {target_course_2['day']} {target_course_2['time_start']}-{target_course_2['time_end']}]")
    
    if check_time_conflict(schedule['204426']['sections'][1], target_course_2):
        print("❌ ผลลัพธ์: ลงไม่ได้ครับ! เวลาเรียนชนกัน")
    else:
        print("✅ ผลลัพธ์: ลงได้ครับ เวลาไม่ชน สามารถลงได้เลย!")

if __name__ == "__main__":
    main()
