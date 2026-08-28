import os
from dotenv import load_dotenv

load_dotenv()

class FirebaseConfig:
    API_KEY = os.getenv("FIREBASE_API_KEY", "AIzaSyAC_0TAIKxKvRMvYG4XGZjQAc3bLUDEyuM")
    AUTH_DOMAIN = os.getenv("FIREBASE_AUTH_DOMAIN", "edge-ai-attendance-system.firebaseapp.com")
    PROJECT_ID = os.getenv("FIREBASE_PROJECT_ID", "edge-ai-attendance-system")
    STORAGE_BUCKET = os.getenv("FIREBASE_STORAGE_BUCKET", "edge-ai-attendance-system.firebasestorage.app")
    MESSAGING_SENDER_ID = os.getenv("FIREBASE_MESSAGING_SENDER_ID", "505945196859")
    APP_ID = os.getenv("FIREBASE_APP_ID", "1:505945196859:web:74e67decdb2faf84d2cf1e")
    MEASUREMENT_ID = os.getenv("FIREBASE_MEASUREMENT_ID", "G-88JTDS0VLK")
    
    @classmethod
    def is_valid(cls):
        return bool(cls.API_KEY and cls.PROJECT_ID)
