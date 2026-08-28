import os
import sys
import random
import uuid
from datetime import datetime, timedelta, time as dt_time
from concurrent.futures import ThreadPoolExecutor

# Add the project root to the python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from src.firebase.firebase_service import FirebaseService
from src.utils.logger import get_logger

logger = get_logger(__name__)

# Fictional Pakistani/International University Demo Names Pool
FIRST_NAMES_MALE = [
    "Muhammad", "Ali", "Ahmed", "Usman", "Bilal", "Hamza", "Zaid", "Hassan",
    "Hussein", "Omar", "Tariq", "Kamran", "Faisal", "Imran", "Farhan", "Saad",
    "Danish", "Zubair", "Adeel", "Noman", "Arslan", "Kashif", "Waqas", "Shahid",
    "Sufyan", "Talha", "Mustafa", "Ibrahim", "Yahya", "Haris"
]

FIRST_NAMES_FEMALE = [
    "Fatima", "Ayesha", "Zainab", "Maryam", "Sana", "Hira", "Anum", "Sadia",
    "Rabia", "Mahnoor", "Iqra", "Noor", "Laiba", "Kiran", "Samra", "Marium",
    "Bushra", "Zara", "Alishba", "Amna", "Sidra", "Mehwish", "Nimra", "Eman"
]

LAST_NAMES = [
    "Khan", "Malik", "Ahmed", "Sheikh", "Raza", "Siddiqui", "Qureshi", "Chaudhry",
    "Bhatti", "Mirza", "Farooq", "Akhtar", "Abbasi", "Butt", "Iqbal", "Shah",
    "Kazmi", "Hashmi", "Ghafoor", "Yousaf", "Mehmood", "Aziz", "Tahir", "Rehman"
]

AVATARS = [
    "https://images.unsplash.com/photo-1534528741775-53994a69daeb?w=100&auto=format&fit=crop&q=80",
    "https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=100&auto=format&fit=crop&q=80",
    "https://images.unsplash.com/photo-1517841905240-472988babdf9?w=100&auto=format&fit=crop&q=80",
    "https://images.unsplash.com/photo-1539571696357-5a69c17a67c6?w=100&auto=format&fit=crop&q=80",
    "https://images.unsplash.com/photo-1500648767791-00dcc994a43e?w=100&auto=format&fit=crop&q=80",
    "https://images.unsplash.com/photo-1524504388940-b1c1722653e1?w=100&auto=format&fit=crop&q=80",
    "https://images.unsplash.com/photo-1492562080023-ab3db95bfbce?w=100&auto=format&fit=crop&q=80",
    "https://images.unsplash.com/photo-1544005313-94ddf0286df2?w=100&auto=format&fit=crop&q=80",
    "https://images.unsplash.com/photo-1506794778202-cad84cf45f1d?w=100&auto=format&fit=crop&q=80",
    "https://images.unsplash.com/photo-1519085360753-af0119f7cbe7?w=100&auto=format&fit=crop&q=80"
]

CAMERAS = [
    "Main Gate Camera",
    "CS Dept Camera",
    "Lab 1 Camera",
    "Lab 2 Camera",
    "Engineering Hall Camera",
    "Library Gate Camera",
    "WEBCAM-01"
]

def generate_random_name():
    is_male = random.random() > 0.4
    first = random.choice(FIRST_NAMES_MALE if is_male else FIRST_NAMES_FEMALE)
    last = random.choice(LAST_NAMES)
    return f"{first} {last}"

def seed_demo_university():
    logger.info("=" * 60)
    logger.info("STARTING REALISTIC UNIVERSITY DATA & ATTENDANCE SEEDER")
    logger.info("=" * 60)

    firebase = FirebaseService()
    if not firebase.config.is_valid():
        logger.error("Firebase config is invalid. Check .env file.")
        return

    now = datetime.now().isoformat()

    # =========================================================================
    # 1. UNIVERSITY HIERARCHY
    # =========================================================================
    univ_id = "univ-tech-01"
    univ_data = {
        "name": "Global Tech University",
        "code": "GTU",
        "createdAt": now,
        "active": True
    }
    firebase.create_document_sync("universities", univ_data, document_id=univ_id)
    logger.info(f"[OK] Seeded University: {univ_data['name']}")

    # =========================================================================
    # 2. FACULTIES (4 Faculties)
    # =========================================================================
    faculties_defs = [
        ("fac-comp-01", "Faculty of Computing & Information Technology", "FCIT"),
        ("fac-eng-01", "Faculty of Engineering & Technology", "FOE"),
        ("fac-mgmt-01", "Faculty of Management Sciences", "FMS"),
        ("fac-soc-01", "Faculty of Social Sciences & Humanities", "FSS")
    ]
    for fac_id, fac_name, fac_code in faculties_defs:
        firebase.create_document_sync("faculties", {
            "name": fac_name,
            "code": fac_code,
            "universityId": univ_id,
            "createdAt": now,
            "active": True
        }, document_id=fac_id)
    logger.info(f"[OK] Seeded {len(faculties_defs)} Faculties")

    # =========================================================================
    # 3. DEPARTMENTS (12 Departments)
    # =========================================================================
    departments_defs = [
        # Computing
        ("dept-cs-01", "Computer Science", "CS", "fac-comp-01", "Dr. Kamran Malik"),
        ("dept-se-01", "Software Engineering", "SE", "fac-comp-01", "Dr. Ayesha Siddiqa"),
        ("dept-ai-01", "AI & Data Science", "DS", "fac-comp-01", "Dr. Bilal Ahmed"),
        ("dept-cys-01", "Cyber Security", "CY", "fac-comp-01", "Dr. Tariq Mehmood"),
        # Engineering
        ("dept-ee-01", "Electrical Engineering", "EE", "fac-eng-01", "Dr. Farhan Qureshi"),
        ("dept-me-01", "Mechanical Engineering", "ME", "fac-eng-01", "Dr. Usman Raza"),
        ("dept-ce-01", "Civil Engineering", "CE", "fac-eng-01", "Dr. Khalid Abbasi"),
        # Management
        ("dept-bba-01", "Business Administration", "BA", "fac-mgmt-01", "Dr. Sadia Tahir"),
        ("dept-af-01", "Accounting & Finance", "AF", "fac-mgmt-01", "Dr. Noman Sheikh"),
        ("dept-econ-01", "Economics", "EC", "fac-mgmt-01", "Dr. Zaid Hashmi"),
        # Social Sciences
        ("dept-med-01", "Media Studies & Journalism", "MS", "fac-soc-01", "Dr. Mahnoor Kazmi"),
        ("dept-psy-01", "Applied Psychology", "AP", "fac-soc-01", "Dr. Rabia Mirza"),
    ]
    for dept_id, dept_name, dept_code, fac_id, hod_name in departments_defs:
        firebase.create_document_sync("departments", {
            "name": dept_name,
            "code": dept_code,
            "facultyId": fac_id,
            "universityId": univ_id,
            "head": hod_name,
            "createdAt": now,
            "active": True
        }, document_id=dept_id)
    logger.info(f"[OK] Seeded {len(departments_defs)} Departments")

    # =========================================================================
    # 4. DEGREE PROGRAMS (18 Programs)
    # =========================================================================
    programs_defs = [
        ("prog-bscs-01", "BS Computer Science", "BSCS", "dept-cs-01", "4 Years"),
        ("prog-mscs-01", "MS Computer Science", "MSCS", "dept-cs-01", "2 Years"),
        ("prog-bsse-01", "BS Software Engineering", "BSSE", "dept-se-01", "4 Years"),
        ("prog-msse-01", "MS Software Engineering", "MSSE", "dept-se-01", "2 Years"),
        ("prog-bsai-01", "BS Artificial Intelligence", "BSAI", "dept-ai-01", "4 Years"),
        ("prog-msai-01", "MS Artificial Intelligence", "MSAI", "dept-ai-01", "2 Years"),
        ("prog-bscys-01", "BS Cyber Security", "BSCYS", "dept-cys-01", "4 Years"),
        ("prog-bsee-01", "BS Electrical Engineering", "BSEE", "dept-ee-01", "4 Years"),
        ("prog-msee-01", "MS Electrical Engineering", "MSEE", "dept-ee-01", "2 Years"),
        ("prog-bsme-01", "BS Mechanical Engineering", "BSME", "dept-me-01", "4 Years"),
        ("prog-bsce-01", "BS Civil Engineering", "BSCE", "dept-ce-01", "4 Years"),
        ("prog-bba-01", "Bachelor of Business Administration", "BBA", "dept-bba-01", "4 Years"),
        ("prog-mba-01", "Master of Business Administration", "MBA", "dept-bba-01", "2 Years"),
        ("prog-bsaf-01", "BS Accounting & Finance", "BSAF", "dept-af-01", "4 Years"),
        ("prog-bsecon-01", "BS Economics", "BSECON", "dept-econ-01", "4 Years"),
        ("prog-bsmed-01", "BS Media Studies", "BSMED", "dept-med-01", "4 Years"),
        ("prog-bspsy-01", "BS Applied Psychology", "BSPSY", "dept-psy-01", "4 Years"),
        ("prog-msfin-01", "MS Finance", "MSFIN", "dept-af-01", "2 Years"),
    ]
    for prog_id, prog_name, prog_code, dept_id, duration in programs_defs:
        firebase.create_document_sync("programs", {
            "name": prog_name,
            "code": prog_code,
            "departmentId": dept_id,
            "duration": duration,
            "createdAt": now,
            "active": True
        }, document_id=prog_id)
    logger.info(f"[OK] Seeded {len(programs_defs)} Programs")

    # =========================================================================
    # 5. COURSES (60 Courses)
    # =========================================================================
    courses_defs = [
        # CS & Computing Courses
        ("course-cs101", "CS101", "Programming Fundamentals", 4, "dept-cs-01"),
        ("course-cs102", "CS102", "Object Oriented Programming", 4, "dept-cs-01"),
        ("course-cs201", "CS201", "Data Structures & Algorithms", 4, "dept-cs-01"),
        ("course-cs301", "CS301", "Database Systems", 4, "dept-cs-01"),
        ("course-cs302", "CS302", "Operating Systems", 3, "dept-cs-01"),
        ("course-cs401", "CS401", "Artificial Intelligence", 3, "dept-cs-01"),
        ("course-cs402", "CS402", "Web Engineering", 3, "dept-cs-01"),
        ("course-cs405", "CS405", "Computer Networks", 3, "dept-cs-01"),
        ("course-cs409", "CS409", "Information Security", 3, "dept-cs-01"),
        ("course-cs412", "CS412", "Cloud Computing & DevOps", 3, "dept-cs-01"),
        # SE Courses
        ("course-se201", "SE201", "Software Requirements Eng", 3, "dept-se-01"),
        ("course-se301", "SE301", "Software Design & Architecture", 3, "dept-se-01"),
        ("course-se302", "SE302", "Software Quality Assurance", 3, "dept-se-01"),
        ("course-se401", "SE401", "Software Project Management", 3, "dept-se-01"),
        ("course-se402", "SE402", "Enterprise App Development", 3, "dept-se-01"),
        # AI & Data Science
        ("course-ai301", "DS301", "Applied Machine Learning", 3, "dept-ai-01"),
        ("course-ai302", "DS302", "Data Mining & Visualization", 3, "dept-ai-01"),
        ("course-ai401", "DS401", "Deep Learning & Computer Vision", 3, "dept-ai-01"),
        ("course-ai402", "DS402", "Natural Language Processing", 3, "dept-ai-01"),
        ("course-ai403", "DS403", "Big Data Analytics", 3, "dept-ai-01"),
        # Cyber Security
        ("course-cy301", "CY301", "Network Security & Cryptography", 3, "dept-cys-01"),
        ("course-cy302", "CY302", "Digital Forensics & Incident Response", 3, "dept-cys-01"),
        ("course-cy401", "CY401", "Ethical Hacking & Pen Testing", 3, "dept-cys-01"),
        ("course-cy402", "CY402", "Malware Analysis", 3, "dept-cys-01"),
        ("course-cy403", "CY403", "Secure Software Development", 3, "dept-cys-01"),
        # Electrical Engineering
        ("course-ee101", "EE101", "Linear Circuit Analysis", 4, "dept-ee-01"),
        ("course-ee201", "EE201", "Digital Logic Design", 4, "dept-ee-01"),
        ("course-ee301", "EE301", "Signals and Systems", 3, "dept-ee-01"),
        ("course-ee302", "EE302", "Microprocessor Systems", 4, "dept-ee-01"),
        ("course-ee401", "EE401", "Power System Analysis", 3, "dept-ee-01"),
        # Mechanical Engineering
        ("course-me101", "ME101", "Engineering Mechanics", 3, "dept-me-01"),
        ("course-me201", "ME201", "Thermodynamics", 3, "dept-me-01"),
        ("course-me301", "ME301", "Fluid Mechanics", 3, "dept-me-01"),
        ("course-me302", "ME302", "Heat & Mass Transfer", 3, "dept-me-01"),
        ("course-me401", "ME401", "Manufacturing Processes", 3, "dept-me-01"),
        # Civil Engineering
        ("course-ce101", "CE101", "Surveying & Levelling", 3, "dept-ce-01"),
        ("course-ce201", "CE201", "Mechanics of Solids", 3, "dept-ce-01"),
        ("course-ce301", "CE301", "Structural Analysis", 3, "dept-ce-01"),
        ("course-ce302", "CE302", "Transportation Engineering", 3, "dept-ce-01"),
        ("course-ce401", "CE401", "Concrete Technology", 3, "dept-ce-01"),
        # Management / BBA
        ("course-ba101", "BA101", "Principles of Management", 3, "dept-bba-01"),
        ("course-ba201", "BA201", "Marketing Management", 3, "dept-bba-01"),
        ("course-ba301", "BA301", "Human Resource Management", 3, "dept-bba-01"),
        ("course-ba401", "BA401", "Strategic Business Strategy", 3, "dept-bba-01"),
        ("course-ba402", "BA402", "Entrepreneurship & Innovation", 3, "dept-bba-01"),
        # Accounting & Finance
        ("course-af101", "AF101", "Financial Accounting", 3, "dept-af-01"),
        ("course-af201", "AF201", "Managerial Accounting", 3, "dept-af-01"),
        ("course-af301", "AF301", "Corporate Finance", 3, "dept-af-01"),
        ("course-af401", "AF401", "Financial Markets & Institutions", 3, "dept-af-01"),
        ("course-af402", "AF402", "Investment Analysis & Portfolio", 3, "dept-af-01"),
        # Economics
        ("course-ec101", "EC101", "Principles of Microeconomics", 3, "dept-econ-01"),
        ("course-ec201", "EC201", "Principles of Macroeconomics", 3, "dept-econ-01"),
        ("course-ec301", "EC301", "Econometrics", 3, "dept-econ-01"),
        ("course-ec401", "EC401", "International Trade", 3, "dept-econ-01"),
        # Media Studies
        ("course-ms101", "MS101", "Introduction to Mass Comm", 3, "dept-med-01"),
        ("course-ms201", "MS201", "Digital Media Production", 3, "dept-med-01"),
        ("course-ms301", "MS301", "Broadcast Journalism", 3, "dept-med-01"),
        ("course-ms401", "MS401", "Public Relations & Advertising", 3, "dept-med-01"),
        # Psychology
        ("course-py101", "PY101", "Introduction to Psychology", 3, "dept-psy-01"),
        ("course-py201", "PY201", "Cognitive Psychology", 3, "dept-psy-01"),
        ("course-py301", "PY301", "Social Psychology", 3, "dept-psy-01"),
        ("course-py401", "PY401", "Clinical & Counseling Psychology", 3, "dept-psy-01"),
    ]

    for cid, code, name, ch, dept_id in courses_defs:
        firebase.create_document_sync("courses", {
            "code": code,
            "name": name,
            "creditHours": ch,
            "departmentId": dept_id,
            "createdAt": now,
            "active": True
        }, document_id=cid)
    logger.info(f"[OK] Seeded {len(courses_defs)} Courses")

    # =========================================================================
    # 6. TEACHERS (36 Teachers — 3 per department)
    # =========================================================================
    teachers_list = []
    # Dedicated demo teacher for Ali Khan
    demo_teacher_id = "teacher-ali-01"
    demo_teacher_data = {
        "employeeId": "EMP-101",
        "name": "Dr. Ali Khan",
        "email": "ali.khan@university.edu",
        "departmentId": "dept-cs-01",
        "userId": "user-ali-auth-01",
        "avatar": AVATARS[0],
        "active": True
    }
    firebase.create_document_sync("teachers", demo_teacher_data, document_id=demo_teacher_id)
    teachers_list.append((demo_teacher_id, "Dr. Ali Khan", "dept-cs-01"))

    # Generate the remaining 35 teachers
    emp_counter = 102
    for dept_id, dept_name, _, _, _ in departments_defs:
        count_to_make = 2 if dept_id == "dept-cs-01" else 3
        for _ in range(count_to_make):
            tid = f"teacher-{dept_id[5:7]}-{emp_counter}"
            tname = f"Dr. {generate_random_name()}"
            t_email = f"prof.{tname.lower().replace(' ', '.').replace('dr.', '')}@university.edu"
            tdata = {
                "employeeId": f"EMP-{emp_counter}",
                "name": tname,
                "email": t_email,
                "departmentId": dept_id,
                "avatar": random.choice(AVATARS),
                "active": True
            }
            firebase.create_document_sync("teachers", tdata, document_id=tid)
            teachers_list.append((tid, tname, dept_id))
            emp_counter += 1

    logger.info(f"[OK] Seeded {len(teachers_list)} Teachers across all departments")

    # =========================================================================
    # 7. CLASS / COURSE OFFERINGS (54 Classes)
    # =========================================================================
    # Map department -> teachers
    dept_teachers = {}
    for tid, tname, tdept in teachers_list:
        dept_teachers.setdefault(tdept, []).append(tid)

    # Class definitions: (class_id, course_id, dept_id, prog_id, semester, section, room, schedule, teacher_id)
    classes_defs = [
        # CS Classes (Semester 6 - Key demo classes)
        ("class-ai-6a", "course-cs401", "dept-cs-01", "prog-bscs-01", "6", "A", "Lab 1", "Mon/Wed 08:30 AM", "teacher-ali-01"),
        ("class-web-6a", "course-cs402", "dept-cs-01", "prog-bscs-01", "6", "A", "Lab 2", "Tue/Thu 10:00 AM", "teacher-ali-01"),
        ("class-cn-6a", "course-cs405", "dept-cs-01", "prog-bscs-01", "6", "A", "Hall A", "Mon/Wed 11:30 AM", dept_teachers["dept-cs-01"][1]),
        ("class-is-6a", "course-cs409", "dept-cs-01", "prog-bscs-01", "6", "A", "Room 301", "Tue/Thu 01:30 PM", dept_teachers["dept-cs-01"][2]),
        # CS Section 6B
        ("class-ai-6b", "course-cs401", "dept-cs-01", "prog-bscs-01", "6", "B", "Lab 1", "Mon/Wed 02:00 PM", "teacher-ali-01"),
        ("class-web-6b", "course-cs402", "dept-cs-01", "prog-bscs-01", "6", "B", "Lab 2", "Tue/Thu 03:00 PM", dept_teachers["dept-cs-01"][1]),
        # CS Semester 4
        ("class-dsa-4a", "course-cs201", "dept-cs-01", "prog-bscs-01", "4", "A", "Lab 3", "Mon/Wed 09:00 AM", dept_teachers["dept-cs-01"][1]),
        ("class-db-4a", "course-cs301", "dept-cs-01", "prog-bscs-01", "4", "A", "Lab 2", "Tue/Thu 11:30 AM", dept_teachers["dept-cs-01"][2]),
        ("class-os-4a", "course-cs302", "dept-cs-01", "prog-bscs-01", "4", "A", "Hall B", "Fri 09:00 AM", "teacher-ali-01"),
        # SE Classes (Semester 4 & 6)
        ("class-se-req-4a", "course-se201", "dept-se-01", "prog-bsse-01", "4", "A", "Room 201", "Mon/Wed 10:00 AM", dept_teachers["dept-se-01"][0]),
        ("class-se-des-4a", "course-se301", "dept-se-01", "prog-bsse-01", "4", "A", "Lab 4", "Tue/Thu 08:30 AM", dept_teachers["dept-se-01"][1]),
        ("class-se-qa-6a", "course-se302", "dept-se-01", "prog-bsse-01", "6", "A", "Lab 4", "Mon/Wed 01:00 PM", dept_teachers["dept-se-01"][0]),
        ("class-se-pm-6a", "course-se401", "dept-se-01", "prog-bsse-01", "6", "A", "Hall A", "Tue/Thu 11:00 AM", dept_teachers["dept-se-01"][2]),
        # AI & Data Science
        ("class-ds-ml-6a", "course-ai301", "dept-ai-01", "prog-bsai-01", "6", "A", "AI Lab", "Mon/Wed 08:30 AM", dept_teachers["dept-ai-01"][0]),
        ("course-ds-cv-6a", "course-ai401", "dept-ai-01", "prog-bsai-01", "6", "A", "AI Lab", "Tue/Thu 10:30 AM", dept_teachers["dept-ai-01"][1]),
        ("course-ds-nlp-6a", "course-ai402", "dept-ai-01", "prog-bsai-01", "6", "A", "AI Lab", "Fri 09:30 AM", dept_teachers["dept-ai-01"][2]),
        # Cyber Security
        ("class-cy-net-6a", "course-cy301", "dept-cys-01", "prog-bscys-01", "6", "A", "Cyber Lab", "Mon/Wed 10:00 AM", dept_teachers["dept-cys-01"][0]),
        ("class-cy-for-6a", "course-cy302", "dept-cys-01", "prog-bscys-01", "6", "A", "Cyber Lab", "Tue/Thu 01:00 PM", dept_teachers["dept-cys-01"][1]),
        ("class-cy-eth-6a", "course-cy401", "dept-cys-01", "prog-bscys-01", "6", "A", "Cyber Lab", "Fri 10:00 AM", dept_teachers["dept-cys-01"][2]),
        # Electrical Engineering
        ("class-ee-cir-2a", "course-ee101", "dept-ee-01", "prog-bsee-01", "2", "A", "Circuits Lab", "Mon/Wed 08:30 AM", dept_teachers["dept-ee-01"][0]),
        ("class-ee-dld-4a", "course-ee201", "dept-ee-01", "prog-bsee-01", "4", "A", "DLD Lab", "Tue/Thu 10:00 AM", dept_teachers["dept-ee-01"][1]),
        ("class-ee-sig-6a", "course-ee301", "dept-ee-01", "prog-bsee-01", "6", "A", "Room 102", "Mon/Wed 11:30 AM", dept_teachers["dept-ee-01"][2]),
        # Mechanical Engineering
        ("class-me-mec-2a", "course-me101", "dept-me-01", "prog-bsme-01", "2", "A", "Workshop", "Mon/Wed 08:30 AM", dept_teachers["dept-me-01"][0]),
        ("class-me-thm-4a", "course-me201", "dept-me-01", "prog-bsme-01", "4", "A", "Thermo Lab", "Tue/Thu 10:00 AM", dept_teachers["dept-me-01"][1]),
        ("class-me-flu-6a", "course-me301", "dept-me-01", "prog-bsme-01", "6", "A", "Fluids Lab", "Mon/Wed 01:30 PM", dept_teachers["dept-me-01"][2]),
        # Civil Engineering
        ("class-ce-sur-2a", "course-ce101", "dept-ce-01", "prog-bsce-01", "2", "A", "Survey Lab", "Mon/Wed 09:00 AM", dept_teachers["dept-ce-01"][0]),
        ("class-ce-sol-4a", "course-ce201", "dept-ce-01", "prog-bsce-01", "4", "A", "Solids Lab", "Tue/Thu 11:00 AM", dept_teachers["dept-ce-01"][1]),
        ("class-ce-str-6a", "course-ce301", "dept-ce-01", "prog-bsce-01", "6", "A", "Room 205", "Fri 09:00 AM", dept_teachers["dept-ce-01"][2]),
        # Business Administration
        ("class-ba-mgt-2a", "course-ba101", "dept-bba-01", "prog-bba-01", "2", "A", "Hall C", "Mon/Wed 08:30 AM", dept_teachers["dept-bba-01"][0]),
        ("class-ba-mkt-4a", "course-ba201", "dept-bba-01", "prog-bba-01", "4", "A", "Room 401", "Tue/Thu 10:00 AM", dept_teachers["dept-bba-01"][1]),
        ("class-ba-hrm-6a", "course-ba301", "dept-bba-01", "prog-bba-01", "6", "A", "Room 402", "Mon/Wed 11:30 AM", dept_teachers["dept-bba-01"][2]),
        # Accounting & Finance
        ("class-af-fa-2a", "course-af101", "dept-af-01", "prog-bsaf-01", "2", "A", "Room 405", "Mon/Wed 08:30 AM", dept_teachers["dept-af-01"][0]),
        ("class-af-ma-4a", "course-af201", "dept-af-01", "prog-bsaf-01", "4", "A", "Room 406", "Tue/Thu 10:00 AM", dept_teachers["dept-af-01"][1]),
        ("class-af-cf-6a", "course-af301", "dept-af-01", "prog-bsaf-01", "6", "A", "Room 407", "Mon/Wed 02:00 PM", dept_teachers["dept-af-01"][2]),
        # Economics
        ("class-ec-mic-2a", "course-ec101", "dept-econ-01", "prog-bsecon-01", "2", "A", "Room 501", "Mon/Wed 09:00 AM", dept_teachers["dept-econ-01"][0]),
        ("class-ec-mac-4a", "course-ec201", "dept-econ-01", "prog-bsecon-01", "4", "A", "Room 502", "Tue/Thu 11:30 AM", dept_teachers["dept-econ-01"][1]),
        ("class-ec-emt-6a", "course-ec301", "dept-econ-01", "prog-bsecon-01", "6", "A", "Room 503", "Fri 10:00 AM", dept_teachers["dept-econ-01"][2]),
        # Media Studies
        ("class-ms-mc-2a", "course-ms101", "dept-med-01", "prog-bsmed-01", "2", "A", "Media Studio", "Mon/Wed 09:30 AM", dept_teachers["dept-med-01"][0]),
        ("class-ms-dm-4a", "course-ms201", "dept-med-01", "prog-bsmed-01", "4", "A", "Edit Suite", "Tue/Thu 01:00 PM", dept_teachers["dept-med-01"][1]),
        ("class-ms-bj-6a", "course-ms301", "dept-med-01", "prog-bsmed-01", "6", "A", "Studio A", "Fri 09:00 AM", dept_teachers["dept-med-01"][2]),
        # Psychology
        ("class-py-int-2a", "course-py101", "dept-psy-01", "prog-bspsy-01", "2", "A", "Room 105", "Mon/Wed 08:30 AM", dept_teachers["dept-psy-01"][0]),
        ("class-py-cog-4a", "course-py201", "dept-psy-01", "prog-bspsy-01", "4", "A", "Psych Lab", "Tue/Thu 10:00 AM", dept_teachers["dept-psy-01"][1]),
        ("class-py-soc-6a", "course-py301", "dept-psy-01", "prog-bspsy-01", "6", "A", "Room 106", "Mon/Wed 01:30 PM", dept_teachers["dept-psy-01"][2]),
    ]

    classes_map = {}
    for clsid, cid, dept_id, prog_id, sem, sec, room, sched, tid in classes_defs:
        cdata = {
            "courseId": cid,
            "teacherId": tid,
            "programId": prog_id,
            "departmentId": dept_id,
            "semester": sem,
            "section": sec,
            "academicYear": "Fall 2026",
            "schedule": sched,
            "room": room,
            "active": True
        }
        firebase.create_document_sync("classes", cdata, document_id=clsid)
        classes_map[clsid] = cdata

    logger.info(f"[OK] Seeded {len(classes_defs)} Classes / Course Offerings")

    # =========================================================================
    # 8. STUDENTS (280 Students across degree programs)
    # =========================================================================
    students_list = []
    # Key test student (BSCS Semester 6A)
    demo_student_id = "student-test-01"
    demo_student_data = {
        "studentId": "FA23-BCS-001",
        "rollNumber": "FA23-BCS-001",
        "name": "Darrell Steward",
        "email": "fa23-bcs-001@university.edu",
        "departmentId": "dept-cs-01",
        "programId": "prog-bscs-01",
        "semester": "6",
        "section": "A",
        "batch": "FA23",
        "userId": "user-std1-auth-01",
        "avatar": AVATARS[0],
        "classIds": ["class-ai-6a", "class-web-6a", "class-cn-6a", "class-is-6a"],
        "active": True
    }
    firebase.create_document_sync("students", demo_student_data, document_id=demo_student_id)
    students_list.append(demo_student_data)

    # Group classes by (programId, semester, section)
    cohort_classes = {}
    for clsid, cinfo in classes_map.items():
        key = (cinfo["programId"], cinfo["semester"], cinfo["section"])
        cohort_classes.setdefault(key, []).append(clsid)

    # Generate student cohorts
    student_roll_idx = 2
    student_cohorts = [
        # BSCS 6A (25 students)
        ("prog-bscs-01", "dept-cs-01", "6", "A", "FA23", "BCS", 24),
        # BSCS 6B (22 students)
        ("prog-bscs-01", "dept-cs-01", "6", "B", "FA23", "BCS", 22),
        # BSCS 4A (20 students)
        ("prog-bscs-01", "dept-cs-01", "4", "A", "FA24", "BCS", 20),
        # BSSE 4A (20 students)
        ("prog-bsse-01", "dept-se-01", "4", "A", "FA24", "BSE", 20),
        # BSSE 6A (20 students)
        ("prog-bsse-01", "dept-se-01", "6", "A", "FA23", "BSE", 20),
        # BSAI 6A (22 students)
        ("prog-bsai-01", "dept-ai-01", "6", "A", "FA23", "BAI", 22),
        # BSCYS 6A (20 students)
        ("prog-bscys-01", "dept-cys-01", "6", "A", "FA23", "BCY", 20),
        # BSEE (25 students across 2/4/6)
        ("prog-bsee-01", "dept-ee-01", "2", "A", "FA25", "BEE", 12),
        ("prog-bsee-01", "dept-ee-01", "6", "A", "FA23", "BEE", 13),
        # BSME (20 students)
        ("prog-bsme-01", "dept-me-01", "4", "A", "FA24", "BME", 10),
        ("prog-bsme-01", "dept-me-01", "6", "A", "FA23", "BME", 10),
        # BSCE (18 students)
        ("prog-bsce-01", "dept-ce-01", "4", "A", "FA24", "BCE", 18),
        # BBA (24 students)
        ("prog-bba-01", "dept-bba-01", "4", "A", "FA24", "BBA", 12),
        ("prog-bba-01", "dept-bba-01", "6", "A", "FA23", "BBA", 12),
        # BSAF (15 students)
        ("prog-bsaf-01", "dept-af-01", "6", "A", "FA23", "BAF", 15),
        # BSECON (15 students)
        ("prog-bsecon-01", "dept-econ-01", "4", "A", "FA24", "BEC", 15),
    ]

    def _seed_single_student(s_record, sid):
        firebase.create_document_sync("students", s_record, document_id=sid)

    pending_students = []
    for prog_id, dept_id, sem, sec, batch, code_prefix, count in student_cohorts:
        c_classes = cohort_classes.get((prog_id, sem, sec), [])
        for i in range(count):
            sid = f"student-{code_prefix.lower()}-{student_roll_idx:03d}"
            roll_no = f"{batch}-{code_prefix}-{student_roll_idx:03d}"
            sname = generate_random_name()
            email = f"{roll_no.lower()}@university.edu"
            
            s_record = {
                "studentId": roll_no,
                "rollNumber": roll_no,
                "name": sname,
                "email": email,
                "departmentId": dept_id,
                "programId": prog_id,
                "semester": sem,
                "section": sec,
                "batch": batch,
                "avatar": random.choice(AVATARS),
                "classIds": c_classes,
                "active": True
            }
            pending_students.append((s_record, sid))
            students_list.append(s_record)
            student_roll_idx += 1

    with ThreadPoolExecutor(max_workers=10) as executor:
        futures = [executor.submit(_seed_single_student, s_data, sid) for s_data, sid in pending_students]
        for f in futures:
            f.result()

    logger.info(f"[OK] Seeded {len(students_list)} Students with enrolled class rosters")

    # =========================================================================
    # 9. HISTORICAL ATTENDANCE SIMULATION (Past 45 Weekdays)
    # =========================================================================
    logger.info("Generating historical attendance simulation records for past 45 days...")
    
    # Map classId -> list of students enrolled in that class
    class_students = {}
    for s in students_list:
        for clsid in s.get("classIds", []):
            class_students.setdefault(clsid, []).append(s)

    # Calculate past 45 weekdays
    today = datetime.now().date()
    past_dates = []
    curr_date = today - timedelta(days=60)
    while len(past_dates) < 45 and curr_date <= today:
        if curr_date.weekday() < 5:  # Monday = 0, Friday = 4
            past_dates.append(curr_date)
        curr_date += timedelta(days=1)

    course_lookup = {c[0]: c[2] for c in courses_defs} # cid -> name

    attendance_records = []
    
    for dt in past_dates:
        weekday_name = dt.strftime("%a") # Mon, Tue, Wed, Thu, Fri
        
        for clsid, cinfo in classes_map.items():
            sched = cinfo.get("schedule", "")
            # Check if this class is scheduled on this weekday
            is_class_today = False
            if "Mon" in sched and weekday_name == "Mon": is_class_today = True
            elif "Tue" in sched and weekday_name == "Tue": is_class_today = True
            elif "Wed" in sched and weekday_name == "Wed": is_class_today = True
            elif "Thu" in sched and weekday_name == "Thu": is_class_today = True
            elif "Fri" in sched and weekday_name == "Fri": is_class_today = True

            if not is_class_today:
                continue

            enrolled = class_students.get(clsid, [])
            if not enrolled:
                continue

            c_course_name = course_lookup.get(cinfo["courseId"], "University Lecture")
            cam = random.choice(CAMERAS)

            # Class time base (e.g. 08:30 AM or 10:00 AM)
            start_hour = 8 if "08:" in sched else 10 if "10:" in sched else 11 if "11:" in sched else 14 if "02:" in sched else 9
            start_min = 30 if ":30" in sched else 0

            for student in enrolled:
                rand_val = random.random()
                
                # 4% Absent: no record created
                if rand_val < 0.04:
                    continue

                # Attendance Status & Timings
                if rand_val < 0.89:
                    # 85% Present: Check in 1-8 mins before or at class start
                    status = "Present"
                    checkin_dt = datetime.combine(dt, dt_time(start_hour, start_min)) - timedelta(minutes=random.randint(0, 8))
                    checkout_dt = checkin_dt + timedelta(minutes=random.randint(80, 95))
                elif rand_val < 0.97:
                    # 8% Late: Check in 5-15 mins after class start
                    status = "Late"
                    checkin_dt = datetime.combine(dt, dt_time(start_hour, start_min)) + timedelta(minutes=random.randint(5, 16))
                    checkout_dt = checkin_dt + timedelta(minutes=random.randint(70, 85))
                else:
                    # 3% Early Leave: Normal checkin, leaves 30 mins early
                    status = "Early Leave"
                    checkin_dt = datetime.combine(dt, dt_time(start_hour, start_min)) - timedelta(minutes=random.randint(0, 5))
                    checkout_dt = checkin_dt + timedelta(minutes=random.randint(35, 45))

                record = {
                    "studentId": student["studentId"],
                    "studentName": student["name"],
                    "timestamp": checkin_dt.isoformat(),
                    "checkIn": checkin_dt.strftime("%I:%M %p"),
                    "checkOut": checkout_dt.strftime("%I:%M %p"),
                    "status": status,
                    "eventType": "CHECK_IN",
                    "cameraId": cam,
                    "confidence": round(random.uniform(0.88, 0.98), 2),
                    "livenessScore": round(random.uniform(0.92, 0.99), 2),
                    "sessionId": str(uuid.uuid4()),
                    "classId": clsid,
                    "courseId": cinfo["courseId"],
                    "courseName": c_course_name,
                    "teacherId": cinfo["teacherId"],
                    "departmentId": cinfo["departmentId"],
                    "facultyId": "fac-comp-01" if "dept-cs" in cinfo["departmentId"] or "dept-se" in cinfo["departmentId"] or "dept-ai" in cinfo["departmentId"] or "dept-cys" in cinfo["departmentId"] else "fac-eng-01" if "dept-ee" in cinfo["departmentId"] or "dept-me" in cinfo["departmentId"] or "dept-ce" in cinfo["departmentId"] else "fac-mgmt-01" if "dept-bba" in cinfo["departmentId"] or "dept-af" in cinfo["departmentId"] or "dept-econ" in cinfo["departmentId"] else "fac-soc-01"
                }
                attendance_records.append(record)

    logger.info(f"Total attendance records generated: {len(attendance_records)}. Writing to Firestore...")

    # Write in batches using thread pool
    def _write_att_record(rec):
        firebase.create_document_sync("attendance", rec)

    # High-density sample (approx 800 records across all courses and cohorts)
    sample_records = attendance_records if len(attendance_records) <= 800 else random.sample(attendance_records, 800)
    
    with ThreadPoolExecutor(max_workers=6) as executor:
        futures = [executor.submit(_write_att_record, r) for r in sample_records]
        for f in futures:
            f.result()

    logger.info(f"[OK] Seeded {len(sample_records)} Historical Attendance Records")

    # =========================================================================
    # 10. RECOGNITION EVENTS (120 Events)
    # =========================================================================
    logger.info("Generating realistic AI recognition & spoof security events...")
    rec_events = []
    base_ts = int(datetime.now().timestamp())

    for i in range(120):
        offset_secs = random.randint(10, 86400 * 5) # Past 5 days
        ts = base_ts - offset_secs
        rand_t = random.random()
        cam = random.choice(CAMERAS)

        if rand_t < 0.75:
            # Recognized
            rand_student = random.choice(students_list)
            evt = {
                "timestamp": ts,
                "eventType": "RECOGNIZED",
                "studentName": rand_student["name"],
                "studentId": rand_student["studentId"],
                "cameraId": cam,
                "deviceId": "LAPTOP-01",
                "confidence": round(random.uniform(0.89, 0.98), 2),
                "livenessScore": round(random.uniform(0.91, 0.99), 2),
                "avatar": rand_student.get("avatar")
            }
        elif rand_t < 0.88:
            # Spoof attempt (photo/video attack caught)
            evt = {
                "timestamp": ts,
                "eventType": "SPOOF",
                "studentName": "Unverified Photo Target",
                "studentId": "N/A",
                "cameraId": cam,
                "deviceId": "LAPTOP-01",
                "confidence": round(random.uniform(0.15, 0.35), 2),
                "livenessScore": round(random.uniform(0.08, 0.22), 2)
            }
        else:
            # Unknown Subject
            evt = {
                "timestamp": ts,
                "eventType": "UNKNOWN",
                "studentName": "Visitor / Unregistered Person",
                "studentId": "UNREGISTERED",
                "cameraId": cam,
                "deviceId": "LAPTOP-01",
                "confidence": round(random.uniform(0.30, 0.48), 2),
                "livenessScore": round(random.uniform(0.88, 0.96), 2)
            }
        rec_events.append(evt)

    with ThreadPoolExecutor(max_workers=10) as executor:
        futures = [executor.submit(firebase.create_document_sync, "recognition_events", evt) for evt in rec_events]
        for f in futures:
            f.result()

    logger.info(f"[OK] Seeded {len(rec_events)} AI Recognition and Anti-Spoofing Audit Events")

    # =========================================================================
    # 11. DEMO USERS IN FIRESTORE
    # =========================================================================
    logger.info("Verifying and syncing Demo Role Accounts in Firestore 'users' collection...")
    demo_users = [
        {
            "email": "admin@university.edu",
            "name": "Super Admin",
            "role": "admin",
            "active": True,
            "scope": {"level": "system"}
        },
        {
            "email": "vc@university.edu",
            "name": "Prof. Dr. Muhammad VC",
            "role": "vc",
            "active": True,
            "scope": {"universityId": univ_id}
        },
        {
            "email": "dean@university.edu",
            "name": "Prof. Dr. Tariq Dean",
            "role": "dean",
            "active": True,
            "scope": {"facultyId": "fac-comp-01"}
        },
        {
            "email": "hod@university.edu",
            "name": "Dr. Kamran Malik",
            "role": "hod",
            "active": True,
            "scope": {"departmentId": "dept-cs-01"}
        },
        {
            "email": "ali.khan@university.edu",
            "name": "Dr. Ali Khan",
            "role": "teacher",
            "active": True,
            "scope": {"departmentId": "dept-cs-01", "teacherId": "teacher-ali-01"}
        },
        {
            "email": "fa23-bcs-001@university.edu",
            "name": "Darrell Steward",
            "role": "student",
            "active": True,
            "scope": {"studentId": "FA23-BCS-001"},
            "classIds": ["class-ai-6a", "class-web-6a", "class-cn-6a", "class-is-6a"]
        }
    ]

    for u in demo_users:
        # Create user profile under their email prefix or known id
        uid_doc = f"user-{u['role']}-doc"
        firebase.create_document_sync("users", u, document_id=uid_doc)

    logger.info("=" * 60)
    logger.info("DEMO DATA SEEDING COMPLETE & READY FOR PRODUCTION DASHBOARD DEMO!")
    logger.info("=" * 60)

if __name__ == "__main__":
    seed_demo_university()
