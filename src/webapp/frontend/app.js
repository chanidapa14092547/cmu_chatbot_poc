const API_BASE = 'https://cmu-chatbot-poc.onrender.com/api';
let globalMinors = [];
let globalMinorCoursesMap = {};
let globalOfferedCourses = {};
let globalCourses = [];
let majorTracksList = [];
let currentRequiredPlaceholders = [];
let globalPassedCourses = [];
let globalInferredMinor = "none";
let currentPlanData = null;

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

        // Populate Major Tracks (Skipped to avoid duplication, using hardcoded options in index.html)

        // Render dynamic plan
        currentPlanData = planRes.plan;
        renderStudyPlan(planRes.plan);

    } catch (error) {
        console.error("Error initializing app:", error);
        dynamicReqsContainer.innerHTML = `<div class="loading" style="color: red;">Failed to load data from backend: ${error.message}</div>`;
    }
}

async function handlePlanChange() {
    dynamicReqsContainer.innerHTML = '<div class="loading">กำลังโหลดแผนการศึกษา...</div>';
    try {
        const planRes = await fetch(`${API_BASE}/study-plan/${yearSelect.value}/${termSelect.value}`).then(r => r.json());
        currentPlanData = planRes.plan;
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
    title.textContent = window.t("courses-to-select");
    title.setAttribute('data-i18n', 'courses-to-select');
    title.style.fontSize = '0.95rem';
    title.style.marginTop = '10px';
    title.style.color = 'var(--brand-600)';
    dynamicReqsContainer.appendChild(title);

    currentRequiredPlaceholders.forEach((ph_dict, i) => {
        const ph = ph_dict.placeholder;
        const req_courses = Math.floor(ph_dict.credits / 3);
        const req_text = req_courses > 0 ? window.t("req-courses", {num: req_courses}) : "";
        const short_name = ph.split('/').pop().trim();
        const short_name_t = window.t(short_name);

        const groupDiv = document.createElement('div');
        groupDiv.className = 'form-group';
        groupDiv.style.marginTop = '15px';
        groupDiv.style.padding = '15px';
        groupDiv.style.border = '1px solid var(--border-color)';
        groupDiv.style.borderRadius = '8px';

        if (ph.includes("Minor") || ph.includes("Major Electives")) {
            // Minor or Major Elective Selection Logic
            const label = document.createElement('label');
            label.textContent = window.t(req_courses > 0 ? "minor-label-with-num" : "minor-label", req_courses > 0 ? {name: short_name_t, num: req_courses} : {name: short_name_t});
            label.setAttribute('data-i18n', req_courses > 0 ? "minor-label-with-num" : "minor-label");
            label.setAttribute('data-i18n-args', JSON.stringify(req_courses > 0 ? {name: short_name, num: req_courses} : {name: short_name}));
            groupDiv.appendChild(label);

            const minorSelect = document.createElement('select');
            minorSelect.id = `minor_sel_${i}`;
            minorSelect.classList.add('minor-select');
            const defaultOpt = document.createElement('option');
            defaultOpt.value = "none";
            defaultOpt.textContent = window.formatMinorOption("none", currentLang);
            minorSelect.appendChild(defaultOpt);

            globalMinors.forEach(m => {
                const opt = document.createElement('option');
                opt.value = m;
                opt.textContent = window.formatMinorOption(m, currentLang);
                minorSelect.appendChild(opt);
            });
            
            // Pre-select if AI inferred a minor
            if (globalInferredMinor !== "none" && globalMinors.includes(globalInferredMinor)) {
                minorSelect.value = globalInferredMinor;
            }

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
                    const details = document.createElement('details');
                    details.open = true;
                    const summary = document.createElement('summary');
                    summary.className = 'category-summary';
                    summary.textContent = window.t(req_courses > 0 ? "major-elec-offered-with-num" : "major-elec-offered", req_courses > 0 ? {num: req_courses} : {});
                    summary.setAttribute('data-i18n', req_courses > 0 ? "major-elec-offered-with-num" : "major-elec-offered");
                    summary.setAttribute('data-i18n-args', JSON.stringify(req_courses > 0 ? {num: req_courses} : {}));
                    details.appendChild(summary);
                    coursesContainer.appendChild(details);
                    
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
                        // Filter for 300 or 400 level courses
                        const levelFilteredMajors = filteredMajors.filter(c => {
                            const levelDigit = c.course_code.charAt(3);
                            return levelDigit === '3' || levelDigit === '4';
                        });

                        if (levelFilteredMajors.length > 0) {
                            const cbList = document.createElement('div');
                            cbList.className = 'checkbox-list';
                            
                            levelFilteredMajors.forEach(c => {
                                const lbl = document.createElement('label');
                                lbl.className = 'checkbox-item';
                                const cb = document.createElement('input');
                                cb.type = 'checkbox';
                                cb.value = c.course_code;
                                cb.className = `maj_fallback_cb_${i}`;
                                
                                const isPassed = globalPassedCourses.includes(c.course_code);
                                if (isPassed) {
                                    cb.disabled = true;
                                    lbl.style.opacity = '0.5';
                                    lbl.appendChild(cb);
                                    lbl.appendChild(document.createTextNode(`${c.course_code} ${c.course_name_en} ${window.t("passed")}`));
                                } else {
                                    lbl.appendChild(cb);
                                    lbl.appendChild(document.createTextNode(`${c.course_code} ${c.course_name_en}`));
                                }
                                cbList.appendChild(lbl);
                            });
                            details.appendChild(cbList);
                        } else {
                            coursesContainer.innerHTML += `<div style="color: #fbbf24; font-size: 0.85rem;">${window.t("warn-no-course")}</div>`;
                        }
                    } else {
                        coursesContainer.innerHTML += `<div style="color: #fbbf24; font-size: 0.85rem;">${window.t("warn-no-major")}</div>`;
                    }
                } else {
                    // Show minor courses
                    const minorCoursesList = globalMinorCoursesMap[selectedMinor] || [];
                    const offeredMinorCourses = minorCoursesList
                        .filter(c => globalOfferedCourses[c])
                        .map(c => ({ course_code: c, course_name_en: globalOfferedCourses[c] }));

                    if (offeredMinorCourses.length > 0) {
                        const detailsMinor = document.createElement('details');
                        detailsMinor.open = true;
                        const summaryMinor = document.createElement('summary');
                        summaryMinor.className = 'category-summary';
                        summaryMinor.textContent = window.t(req_courses > 0 ? "minor-offered-with-num" : "minor-offered", req_courses > 0 ? {minor: selectedMinor, num: req_courses} : {minor: selectedMinor});
                        summaryMinor.setAttribute('data-i18n', req_courses > 0 ? "minor-offered-with-num" : "minor-offered");
                        summaryMinor.setAttribute('data-i18n-args', JSON.stringify(req_courses > 0 ? {minor: selectedMinor, num: req_courses} : {minor: selectedMinor}));
                        detailsMinor.appendChild(summaryMinor);
                        coursesContainer.appendChild(detailsMinor);
                        
                        const cbList = document.createElement('div');
                        cbList.className = 'checkbox-list';
                        offeredMinorCourses.forEach(c => {
                            const lbl = document.createElement('label');
                            lbl.className = 'checkbox-item';
                            const cb = document.createElement('input');
                            cb.type = 'checkbox';
                            cb.value = c.course_code;
                            cb.className = `minor_crs_cb_${i}`;
                            
                            const isPassed = globalPassedCourses.includes(c.course_code);
                            if (isPassed) {
                                cb.disabled = true;
                                lbl.style.opacity = '0.5';
                                lbl.appendChild(cb);
                                lbl.appendChild(document.createTextNode(`${c.course_code} ${c.course_name_en} ${window.t("passed")}`));
                            } else {
                                lbl.appendChild(cb);
                                lbl.appendChild(document.createTextNode(`${c.course_code} ${c.course_name_en}`));
                            }
                            
                            cbList.appendChild(lbl);
                        });
                        detailsMinor.appendChild(cbList);
                    } else {
                        coursesContainer.innerHTML = `<div style="color: #fbbf24; font-size: 0.85rem;">${window.t("warn-no-minor", {minor: selectedMinor})}</div>`;
                    }
                }
            };

            minorSelect.addEventListener('change', updateCoursesUI);
            updateCoursesUI(); // Initial run

        } else if (ph.includes("Major Elective")) {
            // Standalone Major Elective
            const detailsStandalone = document.createElement('details');
            detailsStandalone.open = true;
            const summaryStandalone = document.createElement('summary');
            summaryStandalone.className = 'category-summary';
            summaryStandalone.textContent = window.t(req_courses > 0 ? "cat-req-with-num" : "cat-req", req_courses > 0 ? {name: short_name_t, num: req_courses} : {name: short_name_t});
            summaryStandalone.setAttribute('data-i18n', req_courses > 0 ? "cat-req-with-num" : "cat-req");
            summaryStandalone.setAttribute('data-i18n-args', JSON.stringify(req_courses > 0 ? {name: short_name, num: req_courses} : {name: short_name}));
            detailsStandalone.appendChild(summaryStandalone);
            groupDiv.appendChild(detailsStandalone);
            
            const selectedTrack = majorTrackSelect.value;
                // Grouping logic for Major Electives
                let compCodes = [];
                let choiceCodes = [];
                
                if (selectedTrack === "Data analytics using mathematical modeling") {
                    compCodes = ['204426', '204471', '206300', '206341', '206358', '206465'];
                } else if (selectedTrack === "Statistical data analytics") {
                    compCodes = ['204453', '208350', '208354', '208424', '208450'];
                    choiceCodes = ['204422', '204471'];
                } else if (selectedTrack === "Data analytics using computational modeling") {
                    compCodes = ['204383', '204422', '204426', '204471', '204472'];
                    choiceCodes = ['204423', '204453'];
                }

                let filteredMajors = globalCourses.filter(c => {
                    const cat = c.category_or_track || "";
                    if (!cat.includes("Major Elective")) return false;
                    if (!globalOfferedCourses[c.course_code]) return false; // Must be offered
                    
                    // Always include if it is explicitly part of the track's comp/choice lists
                    if (compCodes.includes(c.course_code) || choiceCodes.includes(c.course_code)) {
                        return true;
                    }
                    
                    if (selectedTrack && cat !== "Field of Specialization / Major / Major Elective Courses") {
                        return cat.includes(selectedTrack);
                    }
                    return true;
                });
            
            if (filteredMajors.length > 0) {
                const cbList = document.createElement('div');
                cbList.className = 'checkbox-list';
                


                const compGroup = [];
                const choiceGroup = [];
                const otherGroup = [];

                filteredMajors.forEach(c => {
                    if (compCodes.includes(c.course_code)) compGroup.push(c);
                    else if (choiceCodes.includes(c.course_code)) choiceGroup.push(c);
                    else otherGroup.push(c);
                });

                const createCourseLabel = (c) => {
                    const lbl = document.createElement('label');
                    lbl.className = 'checkbox-item';
                    const cb = document.createElement('input');
                    cb.type = 'checkbox';
                    cb.value = c.course_code;
                    cb.className = `maj_elec_cb_${i}`;
                    
                    const isPassed = globalPassedCourses.includes(c.course_code);
                    if (isPassed) {
                        cb.disabled = true;
                        lbl.style.opacity = '0.5';
                        lbl.appendChild(cb);
                        lbl.appendChild(document.createTextNode(`${c.course_code} ${c.course_name_en} ${window.t("passed")}`));
                    } else {
                        lbl.appendChild(cb);
                        lbl.appendChild(document.createTextNode(`${c.course_code} ${c.course_name_en}`));
                    }
                    return lbl;
                };

                if (compGroup.length > 0) {
                    const subLabel = document.createElement('div');
                    subLabel.style.cssText = 'font-weight: 600; margin-top: 10px; margin-bottom: 5px; color: #3b82f6; font-size: 0.9rem;';
                    subLabel.setAttribute('data-i18n', 'lbl-track-comp');
                    subLabel.textContent = currentLang === 'en' ? 'Track Compulsory Courses' : 'วิชาบังคับในกลุ่มแขนงวิชา';
                    cbList.appendChild(subLabel);
                    compGroup.forEach(c => cbList.appendChild(createCourseLabel(c)));
                }
                
                if (choiceGroup.length > 0) {
                    const subLabel = document.createElement('div');
                    subLabel.style.cssText = 'font-weight: 600; margin-top: 10px; margin-bottom: 5px; color: #3b82f6; font-size: 0.9rem;';
                    subLabel.setAttribute('data-i18n', 'lbl-track-choice');
                    subLabel.textContent = currentLang === 'en' ? 'Select 3 credits from the following' : 'เลือกเรียน 3 หน่วยกิตจากกระบวนวิชาต่อไปนี้';
                    cbList.appendChild(subLabel);
                    choiceGroup.forEach(c => cbList.appendChild(createCourseLabel(c)));
                }

                if (otherGroup.length > 0) {
                    const subLabel = document.createElement('div');
                    subLabel.style.cssText = 'font-weight: 600; margin-top: 10px; margin-bottom: 5px; color: #3b82f6; font-size: 0.9rem;';
                    subLabel.setAttribute('data-i18n', 'lbl-track-other');
                    subLabel.textContent = currentLang === 'en' ? 'Other Major Elective Courses' : 'วิชาเอกเลือกอื่นๆ (เลือกให้ครบหน่วยกิตที่เหลือ)';
                    cbList.appendChild(subLabel);
                    otherGroup.forEach(c => cbList.appendChild(createCourseLabel(c)));
                }
                
                detailsStandalone.appendChild(cbList);
            } else {
                groupDiv.innerHTML += `<div style="color: #fbbf24; font-size: 0.85rem;">${window.t("warn-no-course")}</div>`;
            }
        } else if (ph.includes("Free Elective")) {
            // Free Elective (Text input)
            const label = document.createElement('label');
            label.textContent = window.t(req_courses > 0 ? "cat-req-with-num" : "cat-req", req_courses > 0 ? {name: short_name_t, num: req_courses} : {name: short_name_t});
            label.setAttribute('data-i18n', req_courses > 0 ? "cat-req-with-num" : "cat-req");
            label.setAttribute('data-i18n-args', JSON.stringify(req_courses > 0 ? {name: short_name, num: req_courses} : {name: short_name}));
            groupDiv.appendChild(label);

            const input = document.createElement('input');
            input.type = 'text';
            input.id = `reg_txt_${i}`;
            input.placeholder = window.t("free-elec-placeholder");
            input.setAttribute('data-i18n', 'free-elec-placeholder');
            groupDiv.appendChild(input);
        } else {
            // General Education or other categories with specific course lists
            const detailsGe = document.createElement('details');
            detailsGe.open = true;
            const summaryGe = document.createElement('summary');
            summaryGe.className = 'category-summary';
            summaryGe.textContent = window.t(req_courses > 0 ? "cat-req-with-num" : "cat-req", req_courses > 0 ? {name: short_name_t, num: req_courses} : {name: short_name_t});
            summaryGe.setAttribute('data-i18n', req_courses > 0 ? "cat-req-with-num" : "cat-req");
            summaryGe.setAttribute('data-i18n-args', JSON.stringify(req_courses > 0 ? {name: short_name, num: req_courses} : {name: short_name}));
            detailsGe.appendChild(summaryGe);
            groupDiv.appendChild(detailsGe);
            
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
                        subLabel.textContent = window.t("group-name", {name: subName});
                        subLabel.setAttribute('data-i18n', 'group-name');
                        subLabel.setAttribute('data-i18n-args', JSON.stringify({name: subName}));
                        detailsGe.appendChild(subLabel);
                    }

                    const cbList = document.createElement('div');
                    cbList.className = 'checkbox-list';
                    
                    // Check if group is already fulfilled (e.g., Basic Science requires max 2 courses)
                    const passedInGroup = grouped[cat].filter(c => globalPassedCourses.includes(c.course_code)).length;
                    let groupMax = Infinity;
                    if (cat.includes("Basic Science Courses")) {
                        groupMax = 2;
                    }
                    const groupFull = passedInGroup >= groupMax;

                    grouped[cat].forEach(c => {
                        const lbl = document.createElement('label');
                        lbl.className = 'checkbox-item';
                        const cb = document.createElement('input');
                        cb.type = 'checkbox';
                        cb.value = c.course_code;
                        cb.className = `gen_elec_cb_${i}`;
                        
                        const isPassed = globalPassedCourses.includes(c.course_code);
                        if (isPassed) {
                            cb.disabled = true;
                            lbl.style.opacity = '0.5';
                            lbl.appendChild(cb);
                            lbl.appendChild(document.createTextNode(`${c.course_code} ${c.course_name_en} ${window.t("passed")}`));
                        } else if (groupFull) {
                            cb.disabled = true;
                            lbl.style.opacity = '0.5';
                            lbl.appendChild(cb);
                            const t_complete = currentLang === 'en' ? '(Completed)' : '(ครบหมวดแล้ว)';
                            lbl.appendChild(document.createTextNode(`${c.course_code} ${c.course_name_en} ${t_complete}`));
                        } else {
                            lbl.appendChild(cb);
                            lbl.appendChild(document.createTextNode(`${c.course_code} ${c.course_name_en}`));
                        }
                        
                        cbList.appendChild(lbl);
                    });
                    detailsGe.appendChild(cbList);
                });
            } else {
                // Fallback to text input if no courses found
                const input = document.createElement('input');
                input.type = 'text';
                input.id = `reg_txt_${i}`;
                input.placeholder = window.t("free-elec-placeholder2");
                input.setAttribute('data-i18n', 'free-elec-placeholder2');
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

// --- File Handling Helpers ---
function getBase64(file) {
    return new Promise((resolve, reject) => {
        const reader = new FileReader();
        reader.readAsDataURL(file);
        reader.onload = () => resolve(reader.result);
        reader.onerror = error => reject(error);
    });
}

// --- Chat File Upload ---
let selectedChatFiles = [];
const chatAttachmentInput = document.getElementById('chat-attachment');
const chatFilePreview = document.getElementById('chat-file-preview');

if(chatAttachmentInput) {
    chatAttachmentInput.addEventListener('change', (e) => {
        selectedChatFiles = Array.from(e.target.files);
        renderChatFilePreview();
    });
}

function renderChatFilePreview() {
    if (!chatFilePreview) return;
    chatFilePreview.innerHTML = '';
    selectedChatFiles.forEach((file, index) => {
        const badge = document.createElement('div');
        badge.style.cssText = 'background: #e0e7ff; color: #4338ca; font-size: 0.75rem; padding: 4px 8px; border-radius: 4px; display: flex; align-items: center; gap: 4px;';
        const nameSpan = document.createElement('span');
        nameSpan.textContent = file.name;
        const closeBtn = document.createElement('i');
        closeBtn.setAttribute('data-lucide', 'x');
        closeBtn.style.cssText = 'width: 12px; height: 12px; cursor: pointer;';
        closeBtn.onclick = () => {
            selectedChatFiles.splice(index, 1);
            if (selectedChatFiles.length === 0 && chatAttachmentInput) chatAttachmentInput.value = '';
            renderChatFilePreview();
        };
        badge.appendChild(nameSpan);
        badge.appendChild(closeBtn);
        chatFilePreview.appendChild(badge);
    });
    lucide.createIcons();
}

// --- Transcript File Upload (Dashboard) ---
const transcriptUploadInput = document.getElementById('transcript-upload');
if (transcriptUploadInput) {
    transcriptUploadInput.addEventListener('change', async (e) => {
        const files = Array.from(e.target.files);
        if (files && files.length > 0) {
            const uploadZone = document.getElementById('upload-zone');
            if (uploadZone) {
                const originalHTML = uploadZone.innerHTML;
                uploadZone.innerHTML = `<div style="color: #4338ca; display: flex; flex-direction: column; align-items: center;"><i data-lucide="loader" style="width: 32px; height: 32px; animation: spin 2s linear infinite;"></i><p style="margin-top: 10px; font-weight: 500;">AI กำลังอ่าน Transcript และวิเคราะห์โครงสร้างหลักสูตร...</p></div>`;
                lucide.createIcons();
                
                if (!document.getElementById('spin-keyframes')) {
                    const style = document.createElement('style');
                    style.id = 'spin-keyframes';
                    style.innerHTML = `@keyframes spin { 100% { transform: rotate(360deg); } }`;
                    document.head.appendChild(style);
                }

                try {
                    const base64Files = await Promise.all(files.map(f => getBase64(f)));
                    
                    const response = await fetch(`${API_BASE}/chat`, {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({
                            message: "Here is my transcript. Please analyze it, update my passed courses, and provide the JSON state.",
                            history: [],
                            images: base64Files
                        })
                    });
                    
                    const data = await response.json();
                    if (response.ok && data.response) {
                        parseAIState(data.response);
                        uploadZone.innerHTML = `<div style="color: #10b981; display: flex; flex-direction: column; align-items: center;"><i data-lucide="check-circle" style="width: 32px; height: 32px;"></i><p style="margin-top: 10px; font-weight: 500;">อัปเดตข้อมูลเข้าระบบเรียบร้อยแล้ว!</p></div>`;
                        lucide.createIcons();
                        setTimeout(() => { uploadZone.innerHTML = originalHTML; lucide.createIcons(); }, 3000);
                    } else {
                        throw new Error("Failed to process transcript");
                    }
                } catch (err) {
                    uploadZone.innerHTML = `<div style="color: #ef4444; display: flex; flex-direction: column; align-items: center;"><i data-lucide="alert-triangle" style="width: 32px; height: 32px;"></i><p style="margin-top: 10px; font-weight: 500;">ประมวลผลล้มเหลว กรุณาลองใหม่</p></div>`;
                    lucide.createIcons();
                    setTimeout(() => { uploadZone.innerHTML = originalHTML; lucide.createIcons(); }, 3000);
                }
            }
        }
    });
}

function parseAIState(text) {
    // Extract ```json_state block
    const match = text.match(/```json_state\n([\s\S]*?)\n```/);
    if (match && match[1]) {
        try {
            const state = JSON.parse(match[1]);
            // Update Dashboard UI (Grouped List View)
            // General Education (30 credits)
            if (state.ge_req_credits !== undefined || state.ge_elec_credits !== undefined) {
                const req = state.ge_req_credits || 0;
                const elec = state.ge_elec_credits || 0;
                const totalGe = req + elec;
                
                document.getElementById('ge-score').textContent = `${totalGe} / 30`;
                document.getElementById('ge-fill').style.width = `${Math.round((totalGe/30)*100)}%`;
                document.getElementById('ge-rem').textContent = `${Math.max(0, 30 - totalGe)} ${i18n[currentLang]["cat-rem"]}`;
                
                document.getElementById('ge-req-score').textContent = `${req} / 21`;
                document.getElementById('ge-req-fill').style.width = `${Math.round((req/21)*100)}%`;
                document.getElementById('ge-req-rem').textContent = `${Math.max(0, 21 - req)} ${i18n[currentLang]["cat-rem"]}`;
                
                document.getElementById('ge-elec-score').textContent = `${elec} / 9`;
                document.getElementById('ge-elec-fill').style.width = `${Math.round((elec/9)*100)}%`;
                document.getElementById('ge-elec-rem').textContent = `${Math.max(0, 9 - elec)} ${i18n[currentLang]["cat-rem"]}`;
            }

            // Core & Major Compulsory (62 credits)
            if (state.core_credits !== undefined) {
                const core = state.core_credits;
                document.getElementById('core-score').textContent = `${core} / 27`;
                document.getElementById('core-fill').style.width = `${Math.round((core/27)*100)}%`;
                document.getElementById('core-rem').textContent = `${Math.max(0, 27 - core)} ${i18n[currentLang]["cat-rem"]}`;
            }
            if (state.major_comp_credits !== undefined) {
                const comp = state.major_comp_credits;
                document.getElementById('major-comp-score').textContent = `${comp} / 35`;
                document.getElementById('major-comp-fill').style.width = `${Math.round((comp/35)*100)}%`;
                document.getElementById('major-comp-rem').textContent = `${Math.max(0, 35 - comp)} ${i18n[currentLang]["cat-rem"]}`;
            }

            // Major Elective (24 credits)
            if (state.major_elec_credits !== undefined) {
                const elec = state.major_elec_credits;
                document.getElementById('major-elec-score').textContent = `${elec} / 24`;
                document.getElementById('major-elec-fill').style.width = `${Math.round((elec/24)*100)}%`;
                document.getElementById('major-elec-rem').textContent = `${Math.max(0, 24 - elec)} ${i18n[currentLang]["cat-rem"]}`;
            }

            // Minor (15 credits)
            if (state.minor_credits !== undefined) {
                const minor = state.minor_credits;
                document.getElementById('minor-score').textContent = `${minor} / 15`;
                document.getElementById('minor-fill').style.width = `${Math.round((minor/15)*100)}%`;
                document.getElementById('minor-rem').textContent = `${Math.max(0, 15 - minor)} ${i18n[currentLang]["cat-rem"]}`;
            }

            // Free Elective (6 credits)
            if (state.free_credits !== undefined) {
                const free = state.free_credits;
                const percent = Math.min(100, Math.round((free / 6) * 100));
                document.getElementById('free-score').textContent = `${free} / 6`;
                document.getElementById('free-fill').style.width = `${percent}%`;
                document.getElementById('free-rem').textContent = `${Math.max(0, 6 - free)} ${i18n[currentLang]["cat-rem"]}`;
            }

            // Calculate Total Credits
            // Calculate Total Credits
            const req = state.ge_req_credits || 0;
            const elec = state.ge_elec_credits || 0;
            const core = state.core_credits || 0;
            const majorComp = state.major_comp_credits || 0;
            const majorElec = state.major_elec_credits || 0;
            const minor = state.minor_credits || 0;
            const free = state.free_credits || 0;

            const total = req + elec + core + majorComp + majorElec + minor + free;
            
            const totalPercent = Math.min(100, Math.round((total / 137) * 100));
            document.getElementById('total-score').textContent = `${total} / 137`;
            document.getElementById('total-fill').style.width = `${totalPercent}%`;
            document.getElementById('total-rem').textContent = `${Math.max(0, 137 - total)} ${i18n[currentLang]["cat-rem"]}`;
            
            // Extract Passed Courses and Inferred Minor for UI disabling
            if (state.passed_courses) {
                globalPassedCourses = state.passed_courses;
            }
            if (state.inferred_minor) {
                globalInferredMinor = state.inferred_minor;
            }
            // Delay rendering until we know if we need to fetch a new plan
            let shouldRenderLater = true;
            
            // Check statuses for Curriculum Progress
            document.querySelectorAll('.item-score').forEach(el => {
                const [val, max] = el.textContent.split(' / ').map(Number);
                const statusEl = el.closest('.progress-item').querySelector('.item-status');
                if (statusEl && !statusEl.id.startsWith('check-') && !statusEl.id.startsWith('total-status')) { // Skip checklist items and total status
                    if (val >= max) {
                        statusEl.textContent = window.t('status-complete');
                        statusEl.className = 'item-status complete';
                    } else if (statusEl.classList.contains('option')) {
                        // keep option required
                    } else {
                        statusEl.textContent = window.t('status-incomplete');
                        statusEl.className = 'item-status incomplete';
                    }
                }
            });

            // Update Graduation Readiness Checklist
            const updateChecklist = (idPrefix, val, target) => {
                const statusEl = document.getElementById(`${idPrefix}-status`);
                const iconEl = document.getElementById(`${idPrefix}-icon`);
                if (!statusEl || !iconEl) return;
                
                if (val >= target) {
                    statusEl.textContent = window.t('status-complete');
                    statusEl.className = 'item-status complete';
                    iconEl.innerHTML = '<i data-lucide="check-circle-2" style="width:20px; color:#10b981;"></i>';
                } else {
                    statusEl.textContent = window.t('status-incomplete');
                    statusEl.className = 'item-status incomplete';
                    iconEl.innerHTML = '<i data-lucide="circle-dashed" style="width:20px; color:#9ca3af;"></i>';
                }
            };

            updateChecklist('check-total', total, 137);
            updateChecklist('check-core', core + majorComp, 62);
            updateChecklist('check-ge', req + elec, 30);
            updateChecklist('check-minor', majorElec + minor, 15); // Requires at least 15 for minor
            
            lucide.createIcons(); // Refresh icons

            if (state.passed_courses) {
                globalPassedCourses = state.passed_courses;
            }
            let yearChanged = false;
            if (state.year_standing !== undefined) {
                const ysEl = document.getElementById('year-select');
                if(ysEl && ysEl.value != state.year_standing) {
                    ysEl.value = state.year_standing;
                    yearChanged = true;
                }
            }
            if (state.alert) {
                const alertBox = document.getElementById('curriculum-alert');
                const alertText = document.getElementById('curriculum-alert-text');
                if (alertBox && alertText) {
                    alertText.innerHTML = `<strong>Action Required</strong><br>⚠️ ${state.alert}`;
                    alertBox.style.display = 'flex';
                }
            } else {
                const alertBox = document.getElementById('curriculum-alert');
                if (alertBox) alertBox.style.display = 'none';
            }

            if (yearChanged) {
                handlePlanChange();
            } else if (currentPlanData) {
                // Re-render the study plan so that checkboxes are disabled based on passed courses
                // and the inferred minor is selected automatically
                renderStudyPlan(currentPlanData);
            }
        } catch (e) {
            console.error("Error parsing JSON state:", e);
        }
    }
}

async function sendChat(messageText, hiddenContext = "") {
    let finalMessage = messageText;
    let base64Images = [];
    
    if (selectedChatFiles.length > 0) {
        const fileNames = selectedChatFiles.map(f => f.name).join(", ");
        base64Images = await Promise.all(selectedChatFiles.map(f => getBase64(f)));
        selectedChatFiles = [];
        renderChatFilePreview();
        if (chatAttachmentInput) chatAttachmentInput.value = '';
    }

    if (!finalMessage.trim() && base64Images.length === 0) return;
    
    appendMessage('user', finalMessage || "[Sent Images]");
    chatInput.value = '';
    
    const loadingDiv = document.createElement('div');
    loadingDiv.className = 'message assistant loading-msg';
    loadingDiv.innerHTML = `<div class="avatar">🤖</div><div class="bubble">กำลังประมวลผล...</div>`;
    // Auto-switch to chat on mobile
    if (window.innerWidth <= 768) {
        switchMobileTab('chat');
    }
    chatHistory.appendChild(loadingDiv);
    chatHistory.scrollTop = chatHistory.scrollHeight;
    
    try {
        let fullMessage = finalMessage;
        if (hiddenContext.trim()) {
            fullMessage += `\n\n${hiddenContext}`;
        }
        
        // Inject current academic state to ensure AI remembers context across manual messages
        let stateContext = "\n\n[SYSTEM STATE REMINDER]\n";
        if (yearSelect && termSelect) {
            stateContext += `- Current Target Term for Planning: Year ${yearSelect.value} Semester ${termSelect.value}\n`;
        }
        if (globalPassedCourses && globalPassedCourses.length > 0) {
            stateContext += `- Passed Courses (DO NOT RECOMMEND THESE): ${globalPassedCourses.join(', ')}\n`;
        }
        fullMessage += stateContext;
        
        const payload = {
            message: fullMessage,
            history: chatMessages.slice(0, -1),
            images: base64Images
        };
        
        const response = await fetch(`${API_BASE}/chat`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        });
        
        const data = await response.json();
        if (loadingDiv.parentNode) loadingDiv.remove();
        
        if (response.ok && data.response) {
            parseAIState(data.response);
            
            // Clean the json_state block from the text shown to the user
            let cleanResponse = data.response.replace(/```json_state\n[\s\S]*?\n```/, '').trim();
            appendMessage('assistant', cleanResponse);
        } else {
            let errorMsg = data.detail || "เกิดข้อผิดพลาดในการตอบกลับ";
            appendMessage('assistant', errorMsg);
        }
    } catch (e) {
        if (loadingDiv.parentNode) loadingDiv.remove();
        appendMessage('assistant', `Error: ${e.message}`);
    }
}

sendBtn.addEventListener('click', () => sendChat(chatInput.value));
chatInput.addEventListener('keypress', (e) => {
    if (e.key === 'Enter') sendChat(chatInput.value);
});

generateBtn.addEventListener('click', async () => {
    let visibleText = `ช่วยจัดตารางเรียนให้หน่อย สำหรับ ${yearSelect.options[yearSelect.selectedIndex].text} ${termSelect.options[termSelect.selectedIndex].text}`;
    if (currentLang === 'en') {
        visibleText = `Please generate a study schedule for ${yearSelect.options[yearSelect.selectedIndex].text} ${termSelect.options[termSelect.selectedIndex].text}`;
    }
    
    let hiddenContext = "";
    


    // Add Fixed courses to prompt
    const planRes = await fetch(`${API_BASE}/study-plan/${yearSelect.value}/${termSelect.value}`).then(r => r.json());
    const fixedCourses = (planRes.plan || []).filter(item => typeof item === 'string');
    if (fixedCourses.length > 0) {
        if (currentLang === 'en') {
            hiddenContext += `(Compulsory courses already planned in the curriculum: ${fixedCourses.join(', ')})\n`;
        } else {
            hiddenContext += `(วิชาบังคับที่จัดไว้ในหลักสูตรแล้วคือ: ${fixedCourses.join(', ')})\n`;
        }
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
    if (typeof event !== 'undefined' && event && event.preventDefault) {
        event.preventDefault();
    }

    document.querySelectorAll('.sidebar-nav .nav-item').forEach(el => {
        el.classList.remove('active');
    });

    if (element) {
        element.classList.add('active');
        const titleSpan = element.querySelector('span');
        const headerTitle = document.getElementById('header-title');
        if (titleSpan && headerTitle) {
            if (element.id === 'nav-scheduler') headerTitle.setAttribute('data-i18n', 'header-title-next');
            else if (element.id === 'nav-progress') headerTitle.setAttribute('data-i18n', 'header-title-curr');
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


// Mobile Tab Switcher
function switchMobileTab(tab) {
    const grid = document.querySelector('.panel-grid');
    const btns = document.querySelectorAll('.mobile-tab-btn');
    if (!grid || btns.length < 2) return;
    
    if (tab === 'chat') {
        grid.classList.remove('show-scheduler');
        grid.classList.add('show-chat');
        btns[0].classList.remove('active');
        btns[1].classList.add('active');
    } else {
        grid.classList.remove('show-chat');
        grid.classList.add('show-scheduler');
        btns[1].classList.remove('active');
        btns[0].classList.add('active');
    }
}
// Default to showing scheduler on mobile
document.addEventListener("DOMContentLoaded", () => {
    const grid = document.querySelector('.panel-grid');
    if (grid) grid.classList.add('show-scheduler');
});

window.addEventListener('languageChanged', () => {
    // Re-render courses if they are showing
    if (typeof updateCoursesUI === 'function') {
        try { document.getElementById('minor-select').dispatchEvent(new Event('change')); } catch(e){}
    }
    // Also we might want to re-render progress bars, but for simplicity we will just let the user re-upload or rely on static HTML translation.
});
