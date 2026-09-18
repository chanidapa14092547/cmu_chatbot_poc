import re

with open('src/webapp/frontend/app.js', 'r') as f:
    content = f.read()

# 1. Replace the generation button click to auto-switch tab
switch_code = """    // Auto-switch to chat on mobile
    if (window.innerWidth <= 768) {
        switchMobileTab('chat');
    }
"""
content = content.replace("    chatHistory.appendChild(loadingDiv);", switch_code + "    chatHistory.appendChild(loadingDiv);")

# 2. Add details/summary for Major Elective (line 179)
content = content.replace(
    """                    const label2 = document.createElement('label');
                    label2.textContent = `วิชาเอกเลือก (Major Electives) ที่เปิดสอน ${req_text}:`;
                    coursesContainer.appendChild(label2);""",
    """                    const details = document.createElement('details');
                    details.open = true;
                    const summary = document.createElement('summary');
                    summary.className = 'category-summary';
                    summary.textContent = `วิชาเอกเลือก (Major Electives) ที่เปิดสอน ${req_text}:`;
                    details.appendChild(summary);
                    coursesContainer.appendChild(details);"""
)
content = content.replace("coursesContainer.appendChild(cbList);", "details.appendChild(cbList);", 1) # first occurrence

# 3. Add details/summary for Minor Courses (line 230)
content = content.replace(
    """                        const label2 = document.createElement('label');
                        label2.textContent = `รายวิชาโท ${selectedMinor} ที่เปิดสอนเทอมนี้ ${req_text}:`;
                        coursesContainer.appendChild(label2);""",
    """                        const detailsMinor = document.createElement('details');
                        detailsMinor.open = true;
                        const summaryMinor = document.createElement('summary');
                        summaryMinor.className = 'category-summary';
                        summaryMinor.textContent = `รายวิชาโท ${selectedMinor} ที่เปิดสอนเทอมนี้ ${req_text}:`;
                        detailsMinor.appendChild(summaryMinor);
                        coursesContainer.appendChild(detailsMinor);"""
)
content = content.replace("coursesContainer.appendChild(cbList);", "detailsMinor.appendChild(cbList);", 1) # second occurrence


# 4. Standalone Major Elective (line 269)
content = content.replace(
    """            // Standalone Major Elective
            const label = document.createElement('label');
            label.textContent = `หมวด ${short_name} ${req_text}:`;
            groupDiv.appendChild(label);""",
    """            // Standalone Major Elective
            const detailsStandalone = document.createElement('details');
            detailsStandalone.open = true;
            const summaryStandalone = document.createElement('summary');
            summaryStandalone.className = 'category-summary';
            summaryStandalone.textContent = `หมวด ${short_name} ${req_text}:`;
            detailsStandalone.appendChild(summaryStandalone);
            groupDiv.appendChild(detailsStandalone);"""
)
content = content.replace("groupDiv.appendChild(cbList);", "detailsStandalone.appendChild(cbList);", 1)

# 5. General Education (line 325)
content = content.replace(
    """            // General Education or other categories with specific course lists
            const label = document.createElement('label');
            label.textContent = `หมวด ${short_name} ${req_text}:`;
            groupDiv.appendChild(label);""",
    """            // General Education or other categories with specific course lists
            const detailsGe = document.createElement('details');
            detailsGe.open = true;
            const summaryGe = document.createElement('summary');
            summaryGe.className = 'category-summary';
            summaryGe.textContent = `หมวด ${short_name} ${req_text}:`;
            detailsGe.appendChild(summaryGe);
            groupDiv.appendChild(detailsGe);"""
)
# For GE, there are subLabels and cbLists appended to groupDiv. Replace all `groupDiv.appendChild(subLabel)` and `groupDiv.appendChild(cbList)` inside the GE block.
# Since it's a bit complex with regex, I'll just use a targeted string replace.
content = content.replace("groupDiv.appendChild(subLabel);", "detailsGe.appendChild(subLabel);")
content = content.replace("groupDiv.appendChild(cbList);", "detailsGe.appendChild(cbList);") # This will also replace the one I already replaced above if I didn't use ,1. Wait, I used ,1 above!
# Let me fix the replace count to make sure it's correct by writing back and formatting properly.
with open('src/webapp/frontend/app.js', 'w') as f:
    f.write(content)

