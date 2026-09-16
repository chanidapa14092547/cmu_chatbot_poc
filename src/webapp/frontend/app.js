const API_BASE = 'https://cmu-chatbot-poc.onrender.com/api';
let globalMinors = [];
let globalMinorCoursesMap = {};
let globalOfferedCourses = {};
let globalCourses = [];
let majorTracksList = [];
let currentRequiredPlaceholders = [];

// DOM Elements
const yearSelect = document.getElementById('year-select');
const termSelect = document.getElementById('term-select');
const majorTrackContainer = document.getElementById('major-track-container');
const majorTrackSelect = document.getElementById('major-track');
const dynamicReqsContainer = document.getElementById('dynamic-requirements');
const generateBtn = document.getElementById('generate-btn');
const timeConstraints = document.getElementById('time-constraints');
const chatHistory = document.getElementById('chat-history');
const chatInput = document.getElementById('chat-input');
const sendBtn = document.getElementById('send-btn');

let chatMessages = []; // For Gemini history

async function init() {
    try {
        // Fetch foundational data
        const [tracksRes, minorsRes, coursesRes, planRes, allCoursesRes] = await Promise.all([
            fetch(`${API_BASE}/major-tracks`).then(r => r.json()),
            fetch(`${API_BASE}/minors`).then(r => r.json()),
            fetch(`${API_BASE}/offered-courses`).then(r => r.json()),
            fetch(`${API_BASE}/study-plan/${yearSelect.value}/${termSelect.value}`).then(r => r.json()),
            fetch(`${API_BASE}/courses`).then(r => r.json())
        ]);

        majorTracksList = tracksRes.tracks;
        globalMinors = minorsRes.minors;
        globalMinorCoursesMap = minorsRes.minor_courses_map;
        globalOfferedCourses = coursesRes.courses;
        globalCourses = allCoursesRes.courses;

        // Populate Major Tracks if available
        if (majorTracksList && majorTracksList.length > 0) {
            majorTracksList.forEach(track => {
                const opt = document.createElement('option');
                opt.value = track;
                opt.textContent = track;
                majorTrackSelect.appendChild(opt);
            });
        }

        // Render dynamic plan
        renderStudyPlan(planRes.plan);

    } catch (error) {
        console.error("Error initializing app:", error);
        dynamicReqsContainer.innerHTML = `<div class="loading" style="color: red;">Failed to load data from backend. Ensure FastAPI is running on port 8000.</div>`;
    }
}

async function handlePlanChange() {
    dynamicReqsContainer.innerHTML = '<div class="loading">กำลังโหลดแผนการศึกษา...</div>';
    try {
        const planRes = await fetch(`${API_BASE}/study-plan/${yearSelect.value}/${termSelect.value}`).then(r => r.json());
        renderStudyPlan(planRes.plan);
    } catch (e) {
        console.error(e);
    }
}

yearSelect.addEventListener('change', handlePlanChange);
termSelect.addEventListener('change', handlePlanChange);
majorTrackSelect.addEventListener('change', () => {
    // Re-render study plan to filter major electives
    handlePlanChange();
});

function renderStudyPlan(planItems) {
    dynamicReqsContainer.innerHTML = '';
    currentRequiredPlaceholders = [];
    
    const fixedCourses = planItems.filter(item => typeof item === 'string');

    let hasElectives = false;
    let hasMajorElective = false;

    planItems.forEach(item => {
        if (typeof item === 'object' && item.category_placeholder) {
            hasElectives = true;
            if (item.category_placeholder.includes("Major Elective") || item.category_placeholder.includes("Minor or Major")) {
                hasMajorElective = true;
            }
            currentRequiredPlaceholders.push({
                placeholder: item.category_placeholder,
                credits: item.credits_required || 3
            });
        }
    });

    if (hasMajorElective && majorTracksList && majorTracksList.length > 0) {
        majorTrackContainer.style.display = 'flex';
    } else {
        majorTrackContainer.style.display = 'none';
    }

    if (!hasElectives) {
        const div = document.createElement('div');
        div.style.color = '#cbd5e1';
        div.style.fontSize = '0.9rem';
        div.style.marginTop = '10px';
        div.textContent = '💡 เทอมนี้เป็นวิชาบังคับล้วน ไม่มีหมวดวิชาเลือกในโครงสร้างหลักสูตรครับ';
        dynamicReqsContainer.appendChild(div);
        return;
    }

    const title = document.createElement('h3');
    title.textContent = "วิชาที่ต้องเลือกสำหรับเทอมนี้ (แสดงเฉพาะที่เปิดสอน):";
    title.style.fontSize = '0.95rem';
    title.style.marginTop = '10px';
    title.style.color = '#c4b5fd';
    dynamicReqsContainer.appendChild(title);

    currentRequiredPlaceholders.forEach((ph_dict, i) => {
        const ph = ph_dict.placeholder;
        const req_courses = Math.floor(ph_dict.credits / 3);
        const req_text = req_courses > 0 ? `(ต้องเลือก ${req_courses} วิชา)` : "";
        const short_name = ph.split('/').pop().trim();

        const groupDiv = document.createElement('div');
        groupDiv.className = 'form-group';
        groupDiv.style.marginTop = '15px';
        groupDiv.style.padding = '15px';
        groupDiv.style.background = 'rgba(0,0,0,0.2)';
        groupDiv.style.borderRadius = '8px';

        if (ph.includes("Minor") || ph.includes("Major Electives")) {
            // Minor or Major Elective Selection Logic
            const label = document.createElement('label');
            label.textContent = `หมวด ${short_name} ${req_text}: เลือกแขนงวิชาโท หรือ เอกเลือก:`;
            groupDiv.appendChild(label);

            const minorSelect = document.createElement('select');
            minorSelect.id = `minor_sel_${i}`;
            const defaultOpt = document.createElement('option');
            defaultOpt.value = "none";
            defaultOpt.textContent = "เลือกลงเป็นวิชาเอกเลือก (Major Elective)";
            minorSelect.appendChild(defaultOpt);

            globalMinors.forEach(m => {
                const opt = document.createElement('option');
                opt.value = m;
                opt.textContent = `วิชาโท: ${m}`;
                minorSelect.appendChild(opt);
            });

            groupDiv.appendChild(minorSelect);

            const coursesContainer = document.createElement('div');
            coursesContainer.id = `courses_container_${i}`;
            coursesContainer.style.marginTop = '10px';
            groupDiv.appendChild(coursesContainer);

            // Handle logic when minor changes
            const updateCoursesUI = async () => {
                coursesContainer.innerHTML = '';
                const selectedMinor = minorSelect.value;
                const selectedTrack = majorTrackSelect.value;

                if (selectedMinor === "none") {
                    // Show Major Electives as checkboxes based on track
                    const label2 = document.createElement('label');
                    label2.textContent = `วิชาเอกเลือก (Major Electives) ที่เปิดสอน ${req_text}:`;
                    coursesContainer.appendChild(label2);
                    
                    let filteredMajors = globalCourses.filter(c => {
                        const cat = c.category_or_track || "";
                        if (!cat.includes("Major Elective")) return false;
                        if (!globalOfferedCourses[c.course_code]) return false; // Must be offered
                        if (selectedTrack && cat !== "Field of Specialization / Major / Major Elective Courses") {
                            // If user selected a track, only show general major electives OR courses matching their track
                            return cat.includes(selectedTrack);
                        }
                        return true;
                    });
                    
                    if (filteredMajors.length > 0) {
                        const cbList = document.createElement('div');
                        cbList.className = 'checkbox-list';
                        filteredMajors.forEach(c => {
                            const lbl = document.createElement('label');
                            lbl.className = 'checkbox-item';
                            const cb = document.createElement('input');
                            cb.type = 'checkbox';
                            cb.value = c.course_code;
                            cb.className = `maj_fallback_cb_${i}`;
                            lbl.appendChild(cb);
                            lbl.appendChild(document.createTextNode(`${c.course_code} ${c.course_name_en}`));
                            cbList.appendChild(lbl);
                        });
                        coursesContainer.appendChild(cbList);
                    } else {
                        coursesContainer.innerHTML += `<div style="color: #fbbf24; font-size: 0.85rem;">⚠️ ไม่มีวิชาเอกเลือกเปิดสอนในเทอมนี้ หรือไม่ตรงกับแขนงที่เลือก</div>`;
                    }
                } else {
                    // Show minor courses
                    const minorCoursesList = globalMinorCoursesMap[selectedMinor] || [];
                    const offeredMinorCourses = minorCoursesList
                        .filter(c => globalOfferedCourses[c])
                        .map(c => ({ course_code: c, course_name_en: globalOfferedCourses[c] }));

                    if (offeredMinorCourses.length > 0) {
                        const label2 = document.createElement('label');
                        label2.textContent = `รายวิชาโท ${selectedMinor} ที่เปิดสอนเทอมนี้ ${req_text}:`;
                        coursesContainer.appendChild(label2);
                        
                        const cbList = document.createElement('div');
                        cbList.className = 'checkbox-list';
                        offeredMinorCourses.forEach(c => {
                            const lbl = document.createElement('label');
                            lbl.className = 'checkbox-item';
                            const cb = document.createElement('input');
                            cb.type = 'checkbox';
                            cb.value = c.course_code;
                            cb.className = `minor_crs_cb_${i}`;
                            lbl.appendChild(cb);
                            lbl.appendChild(document.createTextNode(`${c.course_code} ${c.course_name_en}`));
                            cbList.appendChild(lbl);
                        });
                        coursesContainer.appendChild(cbList);
                    } else {
                        coursesContainer.innerHTML = `<div style="color: #fbbf24; font-size: 0.85rem;">⚠️ วิชาโท ${selectedMinor} ไม่มีวิชาเปิดสอนเทอมนี้เลย</div>`;
                    }
                }
            };

            minorSelect.addEventListener('change', updateCoursesUI);
            updateCoursesUI(); // Initial run

        } else if (ph.includes("Major Elective")) {
            // Standalone Major Elective
            const label = document.createElement('label');
            label.textContent = `หมวด ${short_name} ${req_text}:`;
            groupDiv.appendChild(label);
            
            const selectedTrack = majorTrackSelect.value;
            let filteredMajors = globalCourses.filter(c => {
                const cat = c.category_or_track || "";
                if (!cat.includes("Major Elective")) return false;
                if (!globalOfferedCourses[c.course_code]) return false; // Must be offered
                if (selectedTrack && cat !== "Field of Specialization / Major / Major Elective Courses") {
                    return cat.includes(selectedTrack);
                }
                return true;
            });
            
            if (filteredMajors.length > 0) {
                const cbList = document.createElement('div');
                cbList.className = 'checkbox-list';
                filteredMajors.forEach(c => {
                    const lbl = document.createElement('label');
                    lbl.className = 'checkbox-item';
                    const cb = document.createElement('input');
                    cb.type = 'checkbox';
                    cb.value = c.course_code;
                    cb.className = `maj_elec_cb_${i}`;
                    lbl.appendChild(cb);
                    lbl.appendChild(document.createTextNode(`${c.course_code} ${c.course_name_en}`));
                    cbList.appendChild(lbl);
                });
                groupDiv.appendChild(cbList);
            } else {
                groupDiv.innerHTML += `<div style="color: #fbbf24; font-size: 0.85rem;">⚠️ ไม่มีวิชาเปิดสอน</div>`;
            }
        } else if (ph.includes("Free Elective")) {
            // Free Elective (Text input)
            const label = document.createElement('label');
            label.textContent = `หมวด ${short_name} ${req_text}:`;
            groupDiv.appendChild(label);

            const input = document.createElement('input');
            input.type = 'text';
            input.id = `reg_txt_${i}`;
            input.placeholder = "พิมพ์รหัส/ชื่อวิชา (วิชาใดก็ได้)";
            groupDiv.appendChild(input);
        } else {
            // General Education or other categories with specific course lists
            const label = document.createElement('label');
            label.textContent = `หมวด ${short_name} ${req_text}:`;
            groupDiv.appendChild(label);
            
            let filteredCourses = globalCourses.filter(c => {
                const cat = c.category_or_track || "";
                if (!globalOfferedCourses[c.course_code]) return false;
                // Category matching
                return cat === ph || ph.includes(cat.split('/').pop().trim()) || cat.includes(short_name);
            });
            
            if (filteredCourses.length > 0) {
                // Group courses by their specific category_or_track
                const grouped = {};
                filteredCourses.forEach(c => {
                    const cat = c.category_or_track || "General";
                    if (!grouped[cat]) grouped[cat] = [];
                    grouped[cat].push(c);
                });

                const cats = Object.keys(grouped);
                cats.forEach(cat => {
                    if (cats.length > 1 || cat !== ph) {
                        const subLabel = document.createElement('div');
                        subLabel.style.fontSize = '0.8rem';
                        subLabel.style.color = '#93c5fd';
                        subLabel.style.marginTop = '10px';
                        subLabel.style.marginBottom = '5px';
                        // Extract the sub-category name
                        const subName = cat.replace(ph, '').replace(/^\s*\/\s*/, '') || cat;
                        subLabel.textContent = `▶ กลุ่ม ${subName}`;
                        groupDiv.appendChild(subLabel);
                    }

                    const cbList = document.createElement('div');
                    cbList.className = 'checkbox-list';
                    grouped[cat].forEach(c => {
                        const lbl = document.createElement('label');
                        lbl.className = 'checkbox-item';
                        const cb = document.createElement('input');
                        cb.type = 'checkbox';
                        cb.value = c.course_code;
                        cb.className = `gen_elec_cb_${i}`;
                        lbl.appendChild(cb);
                        lbl.appendChild(document.createTextNode(`${c.course_code} ${c.course_name_en}`));
                        cbList.appendChild(lbl);
                    });
                    groupDiv.appendChild(cbList);
                });
            } else {
                // Fallback to text input if no courses found
                const input = document.createElement('input');
                input.type = 'text';
                input.id = `reg_txt_${i}`;
                input.placeholder = "พิมพ์รหัส/ชื่อวิชา หรือเว้นว่างให้ AI แนะนำ";
                groupDiv.appendChild(input);
            }
        }

        dynamicReqsContainer.appendChild(groupDiv);
    });
}

function appendMessage(role, text) {
    const msgDiv = document.createElement('div');
    msgDiv.className = `message ${role}`;
    
    const avatar = document.createElement('div');
    avatar.className = 'avatar';
    avatar.textContent = role === 'assistant' ? '🤖' : '👤';
    
    const bubble = document.createElement('div');
    bubble.className = 'bubble';
    
    // Use marked.js to render markdown for assistant
    // Use marked.js to render markdown for assistant
    if (role === 'assistant') {
        bubble.innerHTML = marked.parse(text);
        
        // Find tables and add Export button
        const tables = bubble.querySelectorAll('table');
        tables.forEach((table) => {
            const btn = document.createElement('button');
            btn.innerHTML = '📥 บันทึกตารางนี้เป็น Excel (CSV)';
            btn.style.cssText = 'display:block; margin: 15px 0 5px auto; padding: 6px 12px; font-size: 0.85rem; background: #3b82f6; color: white; border-radius: 6px; cursor: pointer; border: none; font-family: inherit; font-weight: 500; transition: background 0.2s;';
            btn.onmouseover = () => btn.style.background = '#2563eb';
            btn.onmouseout = () => btn.style.background = '#3b82f6';
            btn.onclick = () => exportTableToCSV(table, `schedule_${yearSelect.value}_${termSelect.value}.csv`);
            table.parentNode.insertBefore(btn, table);
        });
    } else {
        bubble.textContent = text;
    }
    
    msgDiv.appendChild(avatar);
    msgDiv.appendChild(bubble);
    chatHistory.appendChild(msgDiv);
    
    chatHistory.scrollTop = chatHistory.scrollHeight;
    
    // Save to history
    chatMessages.push({ role, content: text });
}

function exportTableToCSV(table, filename) {
    let csv = [];
    let rows = table.querySelectorAll('tr');
    
    for (let i = 0; i < rows.length; i++) {
        let row = [], cols = rows[i].querySelectorAll('td, th');
        for (let j = 0; j < cols.length; j++) {
            let data = cols[j].innerText.replace(/"/g, '""');
            row.push('"' + data + '"');
        }
        csv.push(row.join(','));
    }
    
    // Add BOM for UTF-8 so Excel reads Thai characters correctly
    let csvFile = new Blob(["\uFEFF" + csv.join('\n')], {type: 'text/csv;charset=utf-8;'});
    let downloadLink = document.createElement("a");
    downloadLink.download = filename;
    downloadLink.href = window.URL.createObjectURL(csvFile);
    downloadLink.style.display = "none";
    document.body.appendChild(downloadLink);
    downloadLink.click();
    document.body.removeChild(downloadLink);
}

async function sendChat(messageText) {
    if (!messageText.trim()) return;
    
    appendMessage('user', messageText);
    chatInput.value = '';
    
    const loadingDiv = document.createElement('div');
    loadingDiv.className = 'message assistant loading-msg';
    loadingDiv.innerHTML = `<div class="avatar">🤖</div><div class="bubble">กำลังประมวลผล (Chain of Thought)...</div>`;
    chatHistory.appendChild(loadingDiv);
    chatHistory.scrollTop = chatHistory.scrollHeight;
    
    try {
        const response = await fetch(`${API_BASE}/chat`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                message: messageText,
                history: chatMessages.slice(0, -1) // Exclude the message we just added
            })
        });
        
        const data = await response.json();
        chatHistory.removeChild(loadingDiv);
        
        if (response.ok && data.response) {
            appendMessage('assistant', data.response);
        } else {
            let errorMsg = data.detail || "เกิดข้อผิดพลาดในการตอบกลับ";
            if (errorMsg.includes("RESOURCE_EXHAUSTED") || errorMsg.includes("429")) {
                errorMsg = "⚠️ ระบบ AI ทำงานหนักเกินโควต้า (Rate Limit Exceeded) กรุณารอประมาณ 1 นาทีแล้วลองใหม่อีกครั้งครับ";
            }
            appendMessage('assistant', errorMsg);
        }
    } catch (e) {
        chatHistory.removeChild(loadingDiv);
        appendMessage('assistant', `Error: ${e.message}`);
    }
}

sendBtn.addEventListener('click', () => sendChat(chatInput.value));
chatInput.addEventListener('keypress', (e) => {
    if (e.key === 'Enter') sendChat(chatInput.value);
});

generateBtn.addEventListener('click', async () => {
    let promptText = `ช่วยจัดตารางเรียนให้หน่อย สำหรับ ${yearSelect.options[yearSelect.selectedIndex].text} ${termSelect.options[termSelect.selectedIndex].text}`;
    
    // Add Fixed courses to prompt
    const planRes = await fetch(`${API_BASE}/study-plan/${yearSelect.value}/${termSelect.value}`).then(r => r.json());
    const fixedCourses = (planRes.plan || []).filter(item => typeof item === 'string');
    if (fixedCourses.length > 0) {
        promptText += `\n\n(วิชาบังคับที่จัดไว้ในหลักสูตรแล้วคือ: ${fixedCourses.join(', ')})`;
    }
    
    // Gather form data
    currentRequiredPlaceholders.forEach((ph_dict, i) => {
        const short_name = ph_dict.placeholder.split('/').pop().trim();
        let choice = "";
        
        if (ph_dict.placeholder.includes("Minor") || ph_dict.placeholder.includes("Major Electives")) {
            const minorSel = document.getElementById(`minor_sel_${i}`);
            if (minorSel && minorSel.value !== "none") {
                const cbs = document.querySelectorAll(`.minor_crs_cb_${i}:checked`);
                const selected = Array.from(cbs).map(cb => cb.value).join(", ");
                if (selected) {
                    choice = `วิชาโท ${minorSel.value} (รายวิชา: ${selected})`;
                } else {
                    choice = `วิชาโท ${minorSel.value} (ให้ AI ช่วยแนะนำวิชา)`;
                }
            } else {
                const cbs = document.querySelectorAll(`.maj_fallback_cb_${i}:checked`);
                const selected = Array.from(cbs).map(cb => cb.value).join(", ");
                if (selected) {
                    choice = `วิชาเอกเลือก (${selected})`;
                }
            }
        } else if (ph_dict.placeholder.includes("Major Elective")) {
            const cbs = document.querySelectorAll(`.maj_elec_cb_${i}:checked`);
            const selected = Array.from(cbs).map(cb => cb.value).join(", ");
            if (selected) {
                choice = selected;
            }
        } else if (ph_dict.placeholder.includes("Free Elective")) {
            const regTxt = document.getElementById(`reg_txt_${i}`);
            if (regTxt && regTxt.value) {
                choice = regTxt.value;
            }
        } else {
            const cbs = document.querySelectorAll(`.gen_elec_cb_${i}:checked`);
            if (cbs.length > 0) {
                choice = Array.from(cbs).map(cb => cb.value).join(", ");
            } else {
                const regTxt = document.getElementById(`reg_txt_${i}`);
                if (regTxt && regTxt.value) {
                    choice = regTxt.value;
                }
            }
        }
        
        if (choice) {
            promptText += `\n- ขอเลือกวิชาในหมวด ${short_name} เป็น: ${choice}`;
        }
    });
    
    const tc = timeConstraints.value;
    if (tc) {
        promptText += `\n- เงื่อนไขเพิ่มเติม: ${tc}`;
    }
    
    sendChat(promptText);
});

// Start
init();

// --- Tab Switching Logic ---
function switchTab(tabId, element) {
    if(event) event.preventDefault();

    document.querySelectorAll('.sidebar-nav .nav-item').forEach(el => {
        el.classList.remove('active');
    });

    if (element) {
        element.classList.add('active');
        const titleSpan = element.querySelector('span');
        const headerTitle = document.getElementById('header-title');
        if (titleSpan && headerTitle) {
            headerTitle.innerText = titleSpan.innerText;
        }
    }

    document.querySelectorAll('.view-section').forEach(el => {
        el.style.display = 'none';
        el.classList.remove('active');
    });

    const target = document.getElementById('view-' + tabId);
    if (target) {
        target.style.display = 'block';
        // brief timeout to allow display:block before adding opacity animation class
        setTimeout(() => target.classList.add('active'), 10);
    }
}

