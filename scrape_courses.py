import csv
import re

departments = {
    "AC ENG": "Academic English",
    "AFAM": "African American Studies",
    "ANATOMY": "Anatomy and Neurobiology",
    "ANTHRO": "Anthropology",
    "ARABIC": "Arabic",
    "ARMN": "Armenian",
    "ART": "Art",
    "ART HIS": "Art History",
    "ARTS": "Arts",
    "ASIANAM": "Asian American Studies",
    "BIOCHEM": "Biological Chemistry",
    "BIO SCI": "Biological Sciences",
    "BATS": "Biomedical and Translational Science",
    "BME": "Biomedical Engineering",
    "BANA": "Business Analytics",
    "CBE": "Chemical and Biomolecular Engineering",
    "CBEMS": "Chemical Engr and Materials Science",
    "CHEM": "Chemistry",
    "CHC/LAT": "Chicano/Latino Studies",
    "CHINESE": "Chinese",
    "ENGRCEE": "Civil and Environmental Engineering",
    "CLASSIC": "Classics",
    "COGS": "Cognitive Sciences",
    "COM LIT": "Comparative Literature",
    "CSE": "Computer Science and Engineering",
    "COMPSCI": "Computer Science",
    "CRM/LAW": "Criminology, Law and Society",
    "CRITISM": "Criticism",
    "CLT&THY": "Culture and Theory",
    "DANCE": "Dance",
    "DATA": "Data Science",
    "DEV BIO": "Developmental and Cell Biology",
    "DRAMA": "Drama",
    "EARTHSS": "Earth System Science",
    "EAS": "East Asian Studies",
    "ECO EVO": "Ecology and Evolutionary Biology",
    "ECON": "Economics",
    "EDUC": "Education",
    "EECS": "Electrical Engineering & Computer Science",
    "ECPS": "Embedded and Cyber-Physical Systems",
    "ENGR": "Engineering",
    "ENGLISH": "English",
    "EHS": "Environmental Health Sciences",
    "EPIDEM": "Epidemiology",
    "EURO ST": "European Studies",
    "MGMT EP": "Executive MBA",
    "FLM&MDA": "Film and Media Studies",
    "FIN": "Finance",
    "FRENCH": "French",
    "MGMT FE": "Fully Employed MBA",
    "GDIM": "Game Design and Interactive Media",
    "GEN&SEX": "Gender and Sexuality Studies",
    "GERMAN": "German",
    "GLBLCLT": "Global Cultures",
    "GLBL ME": "Global Middle East Studies",
    "GREEK": "Greek",
    "MGMT HC": "Health Care MBA",
    "HEBREW": "Hebrew",
    "HISTORY": "History",
    "HUMAN": "Humanities",
    "IN4MATX": "Informatics",
    "I&C SCI": "Information and Computer Science",
    "INNO": "Innovation and Entrepreneurship",
    "INTL ST": "International Studies",
    "IRAN": "Iranian Studies",
    "ITALIAN": "Italian",
    "JAPANESE": "Japanese",
    "KOREAN": "Korean",
    "LSCI": "Language Science",
    "LATIN": "Latin",
    "LINGUIS": "Linguistics",
    "LIT JRN": "Literary Journalism",
    "LPS": "Logic and Philosophy of Science",
    "MGMTMBA": "Management MBA",
    "MGMT": "Management",
    "MGMTPHD": "Management PhD",
    "MPAC": "Master of Professional Accountancy",
    "MSE": "Materials Science and Engineering",
    "MATH": "Mathematics",
    "ENGRMAE": "Mechanical and Aerospace Engineering",
    "MED HUM": "Medical Humanities",
    "M&MG": "Microbiology and Molecular Genetics",
    "MOL BIO": "Molecular Biology and Biochemistry",
    "MUSIC": "Music",
    "NET SYS": "Networked Systems",
    "NEURBIO": "Neurobiology and Behavior",
    "NUR SCI": "Nursing Science",
    "PATH": "Pathology and Laboratory Medicine",
    "PED GEN": "Pediatrics Genetics",
    "PERSIAN": "Persian",
    "PHRMSCI": "Pharmaceutical Sciences",
    "PHARM": "Pharmacology",
    "PHMD": "Pharmacy",
    "PHILOS": "Philosophy",
    "PHY SCI": "Physical Science",
    "PHYSICS": "Physics",
    "PHYSIO": "Physiology and Biophysics",
    "PP&D": "Planning, Policy, and Design",
    "POL SCI": "Political Science",
    "PORTUG": "Portuguese",
    "PSCI": "Psychological Science",
    "PSYCH": "Psychology",
    "PUBHLTH": "Public Health",
    "PUB POL": "Public Policy",
    "REL STD": "Religious Studies",
    "ROTC": "Reserve Officers' Training Corps",
    "RUSSIAN": "Russian",
    "SOCECOL": "Social Ecology",
    "SPPS": "Social Policy and Public Service",
    "SOC SCI": "Social Science",
    "SOCIOL": "Sociology",
    "SWE": "Software Engineering",
    "SPANISH": "Spanish",
    "STATS": "Statistics",
    "UCDC": "UC Washington DC",
    "UNI AFF": "University Affairs",
    "UNI STU": "University Studies",
    "UPPP": "Urban Planning and Public Policy",
    "VIETMSE": "Vietnamese",
    "VIS STD": "Visual Studies",
    "WRITING": "Writing"
}

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