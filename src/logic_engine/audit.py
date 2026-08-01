def evaluate_transcript(transcript_courses, catalog, rules):
    """
    Evaluate a student's transcript against the graduation rules and course catalog.
    """
    course_lookup = {c['course_code']: c for c in catalog['courses']}
    
    results = {
        "major_compulsory": {"earned": 0, "required": rules['major_compulsory'], "courses": []},
        "major_elective": {"earned": 0, "required": rules['major_elective'], "courses": []},
        "ge_and_others": {"earned": 0, "required": "Standard CMU GE (approx 30)", "courses": []},
        "free_elective": {"earned": 0, "required": rules['free_elective'], "courses": []},
    }
    
    for course_code in transcript_courses:
        if course_code in course_lookup:
            info = course_lookup[course_code]
            credits = int(info['credits'])
            category = info['category_or_track'].lower()
            
            if "compulsory" in category or "core" in category:
                results["major_compulsory"]["earned"] += credits
                results["major_compulsory"]["courses"].append(course_code)
            elif "major elective" in category:
                results["major_elective"]["earned"] += credits
                results["major_elective"]["courses"].append(course_code)
            elif "general education" in category:
                results["ge_and_others"]["earned"] += credits
                results["ge_and_others"]["courses"].append(course_code)
            else:
                results["free_elective"]["earned"] += credits
                results["free_elective"]["courses"].append(course_code)
        else:
            # If course is not in the major's catalog, it is likely a free elective from another faculty
            results["free_elective"]["earned"] += 3  # Assume 3 credits for PoC
            results["free_elective"]["courses"].append(course_code)
            
    # Calculate status
    for category, data in results.items():
        if isinstance(data["required"], int):
            data["remaining"] = max(0, data["required"] - data["earned"])
            data["status"] = "PASSED" if data["remaining"] == 0 else "INCOMPLETE"
        else:
            data["remaining"] = "N/A"
            data["status"] = "N/A"
            
    return results
