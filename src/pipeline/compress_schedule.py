import json
import csv
import os

with open("data/json_db/schedule_2567.json", "r", encoding="utf-8") as f:
    data = json.load(f)

# Write to CSV using pipe | as delimiter
with open("data/json_db/schedule_2567.csv", "w", encoding="utf-8", newline='') as f:
    writer = csv.writer(f, delimiter='|')
    writer.writerow(["code", "name", "sec", "day", "time", "room", "lecturer"])
    for row in data:
        writer.writerow([
            row["course_code"],
            row["course_name"],
            row["section"],
            row["day"],
            row["time"],
            row["room"],
            row["lecturer"]
        ])
