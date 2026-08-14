import json

json_path = "/Users/memee/.gemini/antigravity/scratch/cmu_chatbot_poc/data/json_db/Faculty of Science/Bachelor of Science Program in Data Science (2567).json"

with open(json_path, 'r', encoding='utf-8') as f:
    curriculum = json.load(f)

# Define the new comprehensive study plan based on user images
new_study_plan = {
    "year_1_semester_1": [
        "001101",
        "206111",
        "208150",
        "229123",
        "229223",
        {
            "category_placeholder": "Field of Specialization / Core Courses / Basic Science Courses",
            "credits_required": 3
        }
    ],
    "year_1_semester_2": [
        "001102",
        "140104",
        "206112",
        "204100",
        "204217",
        "208250",
        {
            "category_placeholder": "Field of Specialization / Core Courses / Basic Science Courses",
            "credits_required": 3
        }
    ],
    "year_2_semester_1": [
        "001201",
        "201190",
        "204320",
        "206281",
        "229323",
        "229351",
        {
            "category_placeholder": "General Education / GE Electives",
            "credits_required": 3
        }
    ],
    "year_2_semester_2": [
        "001225",
        "204252",
        "206324",
        "206325",  # In the image it says 206324 or 206325. We'll leave both or make an OR block if preferred. But for now, we'll keep the list as they are known courses.
        "229352",
        {
            "category_placeholder": "Field of Specialization / Major / Major Elective Courses",
            "credits_required": 3
        },
        {
            "category_placeholder": "Minor or Major Electives",
            "credits_required": 3
        }
    ],
    "year_3_semester_1": [
        "204371",
        {
            "category_placeholder": "Field of Specialization / Major / Major Elective Courses",
            "credits_required": 9
        },
        {
            "category_placeholder": "Minor or Major Electives",
            "credits_required": 3
        },
        {
            "category_placeholder": "Free Electives",
            "credits_required": 3
        }
    ],
    "year_3_semester_2": [
        "204306",
        "204456",
        {
            "category_placeholder": "Field of Specialization / Major / Major Elective Courses",
            "credits_required": 6
        },
        {
            "category_placeholder": "Minor or Major Electives",
            "credits_required": 6
        },
        {
            "category_placeholder": "Free Electives",
            "credits_required": 3
        }
    ],
    "year_4_semester_1": [
        "229496"
    ],
    "year_4_semester_2": [
        "229490",
        {
            "category_placeholder": "General Education / GE Electives",
            "credits_required": 6
        },
        {
            "category_placeholder": "Field of Specialization / Major / Major Elective Courses",
            "credits_required": 6
        },
        {
            "category_placeholder": "Minor or Major Electives",
            "credits_required": 3
        }
    ]
}

# In Year 2 Sem 2, it's either 206324 OR 206325. We can represent it as a dict.
new_study_plan["year_2_semester_2"] = [
    "001225",
    "204252",
    {
        "course_options": ["206324", "206325"],
        "credits_required": 3
    },
    "229352",
    {
        "category_placeholder": "Field of Specialization / Major / Major Elective Courses",
        "credits_required": 3
    },
    {
        "category_placeholder": "Minor or Major Electives",
        "credits_required": 3
    }
]

curriculum['study_plan'] = new_study_plan

with open(json_path, 'w', encoding='utf-8') as f:
    json.dump(curriculum, f, ensure_ascii=False, indent=2)

print("Successfully updated the study plan with all categories and placeholders!")
