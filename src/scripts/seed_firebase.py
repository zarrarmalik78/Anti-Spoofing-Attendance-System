import os
import sys
from datetime import datetime

# Add the project root to the python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from src.firebase.firebase_service import FirebaseService
from src.utils.logger import get_logger

logger = get_logger(__name__)

def seed_database():
    logger.info("Starting Firebase seeding process...")
    firebase = FirebaseService()
    
    if not firebase.config.is_valid():
        logger.error("Firebase config is invalid. Ensure .env is correct.")
        return

    now = datetime.now().isoformat()

    # 1. Create University
    univ_id = "univ-tech-01"
    univ_data = {
        "name": "Global Tech University",
        "code": "GTU",
        "createdAt": now,
        "active": True
    }
    firebase.create_document_sync("universities", univ_data, document_id=univ_id)

    # 2. Create Faculty
    faculty_id = "fac-comp-01"
    faculty_data = {
        "name": "Faculty of Computing",
        "code": "FC",
        "universityId": univ_id,
        "active": True
    }
    firebase.create_document_sync("faculties", faculty_data, document_id=faculty_id)

    # 3. Create Department
    dept_id = "dept-cs-01"
    dept_data = {
        "name": "Computer Science",
        "code": "CS",
        "facultyId": faculty_id,
        "universityId": univ_id,
        "active": True
    }
    firebase.create_document_sync("departments", dept_data, document_id=dept_id)

    # 4. Create Program
    prog_id = "prog-bscs-01"
    prog_data = {
        "name": "BS Computer Science",
        "code": "BSCS",
        "departmentId": dept_id,
        "duration": "4 Years",
        "active": True
    }
    firebase.create_document_sync("programs", prog_data, document_id=prog_id)

    # 5. Create Courses
    course_ai_id = "course-ai-01"
    course_ai_data = {
        "code": "CS401",
        "name": "Artificial Intelligence",
        "creditHours": 3,
        "departmentId": dept_id,
        "active": True
    }
    firebase.create_document_sync("courses", course_ai_data, document_id=course_ai_id)

    course_web_id = "course-web-01"
    course_web_data = {
        "code": "CS402",
        "name": "Web Engineering",
        "creditHours": 3,
        "departmentId": dept_id,
        "active": True
    }
    firebase.create_document_sync("courses", course_web_data, document_id=course_web_id)

    # 6. Create Teacher
    teacher_id = "teacher-ali-01"
    teacher_data = {
        "employeeId": "EMP-901",
        "name": "Ali Khan",
        "email": "ali.khan@university.edu",
        "departmentId": dept_id,
        "userId": "user-ali-auth-01",
        "active": True
    }
    firebase.create_document_sync("teachers", teacher_data, document_id=teacher_id)

    # 7. Create Classes (Course Offerings)
    class_ai_6a_id = "class-ai-6a"
    class_ai_6a_data = {
        "courseId": course_ai_id,
        "teacherId": teacher_id,
        "programId": prog_id,
        "semester": "6",
        "section": "A",
        "academicYear": "Fall 2026",
        "schedule": "Mon/Wed 10:00 AM",
        "room": "Lab 1",
        "active": True
    }
    firebase.create_document_sync("classes", class_ai_6a_data, document_id=class_ai_6a_id)

    class_web_6a_id = "class-web-6a"
    class_web_6a_data = {
        "courseId": course_web_id,
        "teacherId": teacher_id,  # Same teacher for demo
        "programId": prog_id,
        "semester": "6",
        "section": "A",
        "academicYear": "Fall 2026",
        "schedule": "Tue/Thu 11:30 AM",
        "room": "Lab 2",
        "active": True
    }
    firebase.create_document_sync("classes", class_web_6a_data, document_id=class_web_6a_id)

    # 8. Create Student
    student_id = "student-test-01"
    student_data = {
        "studentId": "FA23-BCS-001",
        "rollNumber": "FA23-BCS-001",
        "name": "Student 1",
        "email": "fa23-bcs-001@university.edu",
        "departmentId": dept_id,
        "programId": prog_id,
        "semester": "6",
        "section": "A",
        "batch": "FA23",
        "userId": "user-std1-auth-01",
        "classIds": [class_ai_6a_id, class_web_6a_id], # Student is in 6A AI and 6A Web
        "active": True
    }
    firebase.create_document_sync("students", student_data, document_id=student_id)

    logger.info("Firebase seeding completed successfully!")

if __name__ == "__main__":
    seed_database()
