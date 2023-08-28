import csv
import re

with open("courses.txt", "r", encoding='utf-8') as f:
    lines = f.readlines()

with open("courses.csv", "w", newline='') as csvfile:
    fieldnames = ['Class Name', 'Class Code', 'Department', 'Units', 'Class Description', 'Class URL']
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
    writer.writeheader()
    
    i = 0
    while i < len(lines):
        line = lines[i].strip()
        if not line or line.isdigit() and int(line) > 2312:
            i += 1
            continue

        course_code = ""
        for key in departments:
            if line.startswith(key) and "unit" in line.lower():
                course_code = key
                break

        if course_code:
            line_parts = line.split(".")
            class_code = course_code + line_parts[0].split(course_code)[1]
            class_name = line_parts[1].strip()
            units = line_parts[2].strip()

            description_lines = []
            i += 1
            while i < len(lines):
                line = lines[i].strip()
                if not line:
                    i += 1
                    continue
                
                next_course = False
                for key in departments:
                    if line.startswith(key) and "unit" in line.lower():
                        next_course = True
                        break
                
                if next_course:
                    break

                description_lines.append(line)
                i += 1

            class_description = " ".join(description_lines)
            class_url = f"https://catalogue.uci.edu/allcourses/{course_code.lower().replace(' ', '_')}/"

            writer.writerow({'Class Name': class_name, 'Class Code': class_code, 'Department': departments[course_code], 'Units': units, 'Class Description': class_description, 'Class URL': class_url})
        else:
            i += 1
