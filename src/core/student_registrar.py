import numpy as np
from typing import List, Tuple, Optional

from src.database.db_manager import DatabaseManager
from src.core.embedding_matcher import EmbeddingMatcher
from src.core.face_engine import FaceEngine
from src.utils.logger import get_logger

logger = get_logger(__name__)

POSE_INSTRUCTIONS = [
    ("Look Straight",        "Center your face in the frame"),
    ("Turn Slightly Left",   "Rotate head gently to the left"),
    ("Turn Slightly Right",  "Rotate head gently to the right"),
    ("Tilt Up Slightly",     "Raise your chin a little"),
    ("Tilt Down Slightly",   "Lower your chin a little"),
    ("Look Straight",        "Return to center"),
    ("Smile Naturally",      "Relax and smile"),
    ("Neutral Expression",   "Return to neutral"),
    ("Turn Left More",       "Rotate head further left"),
    ("Turn Right More",      "Rotate head further right"),
]

from src.firebase.firebase_service import FirebaseService

class StudentRegistrar:
    """
    Handles the registration workflow: capturing multiple face samples,
    averaging them for robustness, and saving to the database.
    """
    def __init__(self, face_engine: FaceEngine, db_manager: DatabaseManager, matcher: EmbeddingMatcher, firebase_service: FirebaseService = None):
        self.face_engine = face_engine
        self.db_manager = db_manager
        self.matcher = matcher
        self.firebase_service = firebase_service

    def capture_sample(self, frame: np.ndarray) -> Tuple[bool, str, Optional[np.ndarray]]:
        """
        Processes a single frame for registration.
        Validates that exactly one face is present.
        
        Returns:
            Tuple of (success, message, embedding)
        """
        faces = self.face_engine.detect_and_embed(frame)
        
        if len(faces) == 0:
            return False, "No face detected. Please adjust position.", None
            
        if len(faces) > 1:
            return False, "Multiple faces detected. Please ensure only one person is in frame.", None
            
        face = faces[0]
        
        if not getattr(face, 'is_live', True):
            return False, "Live face required for registration.", None
            
        # Optional: Add quality checks here based on det_score or face size
        if face.det_score < 0.6:
            return False, "Face detection confidence too low. Please move into better lighting.", None
            
        return True, "Capture successful.", face.embedding

    def register_student(self, name: str, roll_number: str, department: str, embeddings: List[np.ndarray]) -> bool:
        """
        Averages the captured embeddings, normalizes, and saves/updates student record in SQLite & Firestore.
        Sets faceEnrollmentStatus = 'ENROLLED' in Cloud Firestore.
        """
        if embeddings is None or (isinstance(embeddings, (list, tuple)) and len(embeddings) == 0):
            raise ValueError("No valid embeddings provided for registration.")

        if isinstance(embeddings, np.ndarray):
            if embeddings.ndim == 1:
                stacked_embeddings = embeddings.reshape(1, -1)
            else:
                stacked_embeddings = embeddings
        else:
            stacked_embeddings = np.vstack(embeddings)
        
        # Compute mean along the sample axis: shape (512,)
        mean_embedding = np.mean(stacked_embeddings, axis=0)
        
        # L2-normalize the averaged embedding
        norm = np.linalg.norm(mean_embedding)
        if norm == 0:
            raise ValueError("Computed mean embedding has zero norm.")
        final_embedding = mean_embedding / norm
        
        # Save or update SQLite DB
        try:
            if self.db_manager.student_exists(roll_number):
                student_id = self.db_manager.update_student_embedding(roll_number, name, department, final_embedding)
            else:
                student_id = self.db_manager.insert_student(name, roll_number, department, final_embedding)
            
            # Sync enrollment status to Cloud Firestore
            if self.firebase_service:
                import time
                student_data = {
                    "studentId": roll_number,
                    "name": name,
                    "rollNumber": roll_number,
                    "departmentId": department if "dept-" in department else "dept-cs-01",
                    "faceEnrollmentStatus": "ENROLLED",
                    "embeddingEnrolled": True,
                    "enrolledAt": str(time.strftime('%Y-%m-%dT%H:%M:%SZ'))
                }
                import re
                clean_roll = re.sub(r'[^a-zA-Z0-9]', '', str(roll_number)).lower()
                self.firebase_service.create_document("students", student_data, document_id=f"student-{clean_roll}")
            
            # Reload the matcher immediately so the student can be recognized live
            self.matcher.reload()
            logger.info(f"Successfully registered student {name} ({roll_number}) with face enrollment status ENROLLED.")
            return True
        except Exception as e:
            logger.error(f"Failed to register student: {e}")
            raise
