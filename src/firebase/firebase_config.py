import os
from dotenv import load_dotenv

load_dotenv()

class FirebaseConfig:
    API_KEY = os.getenv("FIREBASE_API_KEY")
    AUTH_DOMAIN = os.getenv("FIREBASE_AUTH_DOMAIN")
    PROJECT_ID = os.getenv("FIREBASE_PROJECT_ID")
    STORAGE_BUCKET = os.getenv("FIREBASE_STORAGE_BUCKET")
    MESSAGING_SENDER_ID = os.getenv("FIREBASE_MESSAGING_SENDER_ID")
    APP_ID = os.getenv("FIREBASE_APP_ID")
    MEASUREMENT_ID = os.getenv("FIREBASE_MEASUREMENT_ID")
    
    @classmethod
    def is_valid(cls):
        return bool(cls.API_KEY and cls.PROJECT_ID)
