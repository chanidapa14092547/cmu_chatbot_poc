const i18n = {
    "en": {
        "nav-next-sem": "Next Semester",
        "nav-curr-prog": "Curriculum Progress",
        "header-title-next": "Next Semester",
        "header-title-curr": "Curriculum Progress",
        "btn-lang": "🇹🇭 เปลี่ยนเป็นภาษาไทย",
        
        // Curriculum Progress Names
        "cat-ge": "General Education",
        "cat-ge-req": "Required General Education",
        "cat-ge-elec": "GE Electives",
        "cat-core": "Core Courses",
        "cat-major-comp": "Major Compulsory",
        "cat-major-elec": "Major Elective",
        "cat-minor": "Minor / No Minor",
        "cat-free": "Free Elective",
        "cat-total": "Total Credits",
        "cat-rem": "credits remaining",
        
        "upload-btn": "Upload Transcript Images",
        "upload-desc": "Supported formats: JPG, PNG",
        "chat-placeholder": "Ask something (e.g. Can you arrange my schedule?)",
        "btn-generate": "Generate Schedule"
    },
    "th": {
        "nav-next-sem": "จัดตารางเรียน",
        "nav-curr-prog": "ความคืบหน้าหลักสูตร",
        "header-title-next": "จัดตารางเรียนเทอมถัดไป",
        "header-title-curr": "ความคืบหน้าหลักสูตร",
        "btn-lang": "🇬🇧 Switch to English",
        
        // Curriculum Progress Names (Official)
        "cat-ge": "หมวดวิชาศึกษาทั่วไป",
        "cat-ge-req": "กลุ่มวิชาศึกษาทั่วไปบังคับ",
        "cat-ge-elec": "กลุ่มวิชาศึกษาทั่วไปเลือก",
        "cat-core": "วิชาแกน",
        "cat-major-comp": "วิชาเอก (บังคับ)",
        "cat-major-elec": "วิชาเอก (เลือก)",
        "cat-minor": "วิชาโท / เลือกเสรี (ไม่มีโท)",
        "cat-free": "หมวดวิชาเลือกเสรี",
        "cat-total": "หน่วยกิตรวมทั้งหมด",
        "cat-rem": "หน่วยกิตที่ขาด",
        
        "upload-btn": "อัปโหลดรูปภาพ Transcript",
        "upload-desc": "รองรับไฟล์: JPG, PNG",
        "chat-placeholder": "พิมพ์คำถาม (เช่น ช่วยจัดตารางเรียนให้หน่อย)",
        "btn-generate": "สร้างตารางเรียน"
    }
};

let currentLang = "en";

function toggleLanguage() {
    currentLang = currentLang === "en" ? "th" : "en";
    updateLanguage();
}

function updateLanguage() {
    document.querySelectorAll('[data-i18n]').forEach(el => {
        const key = el.getAttribute('data-i18n');
        if (i18n[currentLang][key]) {
            if (el.tagName === 'INPUT' && el.type === 'text') {
                el.placeholder = i18n[currentLang][key];
            } else {
                el.innerHTML = i18n[currentLang][key];
            }
        }
    });
    
    // Also update dynamic remaining text if possible, but for now we just change static
    document.getElementById('lang-btn').innerHTML = i18n[currentLang]["btn-lang"];
}
