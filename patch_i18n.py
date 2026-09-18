with open('src/webapp/frontend/i18n.js', 'r') as f:
    i18n = f.read()

en_tracks = """
        "track-math": "Mathematics",
        "track-stats": "Statistics",
        "track-cs": "Computer Science",
"""
i18n = i18n.replace('"btn-generate": "Generate Schedule"', '"btn-generate": "Generate Schedule",' + en_tracks)

th_tracks = """
        "track-math": "กลุ่มวิชาคณิตศาสตร์ (Mathematics)",
        "track-stats": "กลุ่มวิชาสถิติ (Statistics)",
        "track-cs": "กลุ่มวิชาวิทยาการคอมพิวเตอร์ (Computer Science)",
"""
i18n = i18n.replace('"btn-generate": "จัดตารางเรียน"', '"btn-generate": "จัดตารางเรียน",' + th_tracks)

with open('src/webapp/frontend/i18n.js', 'w') as f:
    f.write(i18n)
