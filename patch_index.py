with open('src/webapp/frontend/index.html', 'r') as f:
    html = f.read()

# Update Track Select
track_select = """                                    <select id="major-track">
                                        <option value="Mathematics" data-i18n="track-math">Mathematics (คณิตศาสตร์)</option>
                                        <option value="Statistics" data-i18n="track-stats">Statistics (สถิติ)</option>
                                        <option value="Computer Science" data-i18n="track-cs">Computer Science (คอมพิวเตอร์)</option>
                                    </select>"""
html = html.replace('                                    <select id="major-track">\n                                        <option value="Mathematics">Mathematics (คณิตศาสตร์)</option>\n                                        <option value="Statistics">Statistics (สถิติ)</option>\n                                        <option value="Computer Science">Computer Science (คอมพิวเตอร์)</option>\n                                    </select>', track_select)

with open('src/webapp/frontend/index.html', 'w') as f:
    f.write(html)
