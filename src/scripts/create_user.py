import os
import sys
import uuid
from typing import Optional, Dict, Any

# Add the project root to the python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from src.firebase.firebase_service import FirebaseService
from src.utils.logger import get_logger

logger = get_logger(__name__)

def create_user(
    email: str, 
    password: str, 
    name: str, 
    role: str, 
    scope: Dict[str, Any], 
    entity_id: Optional[str] = None
):
    """
    Creates a user in Firebase Auth and sets up their role and scope in Firestore.
    """
    firebase = FirebaseService()
    if not firebase.config.is_valid():
        logger.error("Invalid Firebase Config.")
        return

    logger.info(f"Creating user {email} with role {role}...")
    
    # 1. Create in Firebase Auth
    uid = firebase.sign_up(email, password)
    if not uid:
        logger.error("Failed to create user in Firebase Auth.")
        return
        
    logger.info(f"Auth created. UID: {uid}")

    # 2. Create in Firestore 'users' collection
    user_data = {
        "uid": uid,
        "name": name,
        "email": email,
        "role": role,
        "active": True,
        "scope": scope
    }
    
    success = firebase.create_document_sync("users", user_data, document_id=uid)
    if success:
        logger.info(f"User profile created in Firestore 'users' collection.")
    else:
        logger.error(f"Failed to create Firestore profile for {uid}")
        return

    # 3. Link to University Entities (Optional)
    if entity_id:
        if role == "student":
            firebase.update_document("students", entity_id, {"userId": uid})
            logger.info(f"Linked UID {uid} to Student {entity_id}")
        elif role == "teacher":
            firebase.update_document("teachers", entity_id, {"userId": uid})
            logger.info(f"Linked UID {uid} to Teacher {entity_id}")
        elif role == "hod":
            firebase.update_document("departments", entity_id, {"hodUserId": uid})
            logger.info(f"Linked UID {uid} to Department {entity_id} as HOD")
        elif role == "dean":
            firebase.update_document("faculties", entity_id, {"deanUserId": uid})
            logger.info(f"Linked UID {uid} to Faculty {entity_id} as Dean")
        elif role == "vc":
            firebase.update_document("universities", entity_id, {"vcUserId": uid})
            logger.info(f"Linked UID {uid} to University {entity_id} as VC")
            
if __name__ == "__main__":
    # Test Accounts
    logger.info("Initializing Test Accounts...")
    
    # Admin
    create_user("admin@university.edu", "password123", "Super Admin", "admin", scope={"level": "system"})
    
    # VC
    create_user("vc@university.edu", "password123", "Vice Chancellor", "vc", scope={"universityId": "univ-tech-01"}, entity_id="univ-tech-01")
    
    # Dean
    create_user("dean@university.edu", "password123", "Dean of Computing", "dean", scope={"facultyId": "fac-comp-01"}, entity_id="fac-comp-01")
    
    # HOD
    create_user("hod@university.edu", "password123", "HOD Computer Science", "hod", scope={"departmentId": "dept-cs-01"}, entity_id="dept-cs-01")
    
    # Teacher (Linking to teacher-ali-01)
    create_user("ali.khan@university.edu", "password123", "Dr. Ali Khan", "teacher", scope={"departmentId": "dept-cs-01", "teacherId": "teacher-ali-01"}, entity_id="teacher-ali-01")
    
    # Student (Linking to student-test-01)
    create_user("fa23-bcs-001@university.edu", "password123", "Darrell Steward", "student", scope={"studentId": "FA23-BCS-001"}, entity_id="student-test-01")
    
    # Disabled User Test
    firebase = FirebaseService()
    banned_uid = firebase.sign_up("banned@university.edu", "password123")
    if banned_uid:
        user_data = {
            "uid": banned_uid,
            "name": "Banned User",
            "email": "banned@university.edu",
            "role": "student",
            "active": False,
            "scope": {}
        }
        firebase.create_document_sync("users", user_data, document_id=banned_uid)
        logger.info(f"Created disabled user banned@university.edu")
