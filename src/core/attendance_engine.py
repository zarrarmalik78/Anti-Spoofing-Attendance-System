import uuid
import time
from typing import Dict, Set, Tuple
from enum import Enum

from src.database.db_manager import DatabaseManager
from src.core.events import RecognitionEvent, EventType
from src.firebase.firebase_service import FirebaseService
from src.utils.logger import get_logger

logger = get_logger(__name__)

class AttendanceStatus(Enum):
    STABILIZING = 1
    NEWLY_MARKED = 2
    ALREADY_MARKED = 3
    IGNORED = 4

class AttendanceEngine:
    """
    Handles attendance marking logic, session deduplication, and the stability timer.
    Processes standardized RecognitionEvent objects and writes to Firestore.
    """
    def __init__(self, db_manager: DatabaseManager, firebase_service: FirebaseService, stability_seconds: float = 1.0):
        self.db_manager = db_manager
        self.firebase_service = firebase_service
        self.stability_seconds = stability_seconds
        
        # Generate a unique session ID for this run
        self.session_id = str(uuid.uuid4())
        logger.info(f"Initialized AttendanceEngine with session_id: {self.session_id}")
        
        # State
        self._marked_students: Set[int] = set()
        self._stability_tracker: Dict[int, float] = {}
        self._today_unknown_count: int = 0
        
        # Throttling to prevent Firebase spam
        self._last_log_time: Dict[str, float] = {}
        
        # Pre-load already marked students for this session
        records = self.db_manager.get_session_attendance(self.session_id)
        for r in records:
            self._marked_students.add(r.student_id)

    def _log_recognition_event_to_firebase(self, event: RecognitionEvent, cooldown: float = 60.0):
        """Helper to log security/recognition events to Firestore with configurable cooldown"""
        key = f"{event.event_type.name}_{event.student_id or 'none'}"
        now = time.time()
        
        if key in self._last_log_time and now - self._last_log_time[key] < cooldown:
            return  # Throttled
            
        self._last_log_time[key] = now
        
        data = {
            "timestamp": event.timestamp,
            "eventType": event.event_type.name,
            "cameraId": event.camera_id,
            "confidence": event.recognition_confidence,
            "livenessScore": event.liveness_score
        }
        if event.student_id is not None:
            data["studentId"] = event.student_id
        if event.student_name is not None:
            data["studentName"] = event.student_name
            
        self.firebase_service.create_document("recognition_events", data)

    def process_event(self, event: RecognitionEvent) -> Tuple[AttendanceStatus, float]:
        """
        Processes a single recognition event.
        - UNKNOWN: UI display only (never written to DB or Firebase)
        - SPOOF (unregistered): Ignored completely
        - SPOOF (registered student): Logged once as security event with 60s cooldown
        - RECOGNIZED: Triggers attendance marking & cloud sync
        """
        if event.event_type == EventType.UNKNOWN:
            self._today_unknown_count += 1
            # Do NOT write unknown events to SQLite or Firebase (UI only)
            return AttendanceStatus.IGNORED, 0.0
            
        if event.event_type == EventType.SPOOF:
            # Only log spoof event if it can be associated with a registered student
            if event.student_id is not None:
                self._log_recognition_event_to_firebase(event, cooldown=60.0)
            return AttendanceStatus.IGNORED, 0.0
            
        if event.event_type != EventType.RECOGNIZED or event.student_id is None:
            return AttendanceStatus.IGNORED, 0.0

        student_id = event.student_id
        
        if student_id in self._marked_students:
            return AttendanceStatus.ALREADY_MARKED, 1.0
            
        current_time = event.timestamp
        
        if student_id not in self._stability_tracker:
            self._stability_tracker[student_id] = current_time
            return AttendanceStatus.STABILIZING, 0.0
            
        elapsed = current_time - self._stability_tracker[student_id]
        
        if elapsed >= self.stability_seconds:
            # Mark attendance
            try:
                # 1. Write to local SQLite
                self.db_manager.insert_attendance(student_id, self.session_id)
                self._marked_students.add(student_id)
                
                # 2. Log recognition event to Firestore
                self._log_recognition_event_to_firebase(event)
                
                # 3. Write attendance record to Firestore
                from datetime import datetime
                iso_time = datetime.fromtimestamp(event.timestamp).isoformat()
                
                # Fetch full student record from SQLite
                student_rec = self.db_manager.get_student_by_id(student_id)
                roll_num = student_rec.roll_number if student_rec else str(student_id)
                std_name = student_rec.name if student_rec else (event.student_name or "Zarar")
                std_email = "zarar@university.edu" if roll_num == "5022" or "zarar" in std_name.lower() else f"student{roll_num}@university.edu"

                attendance_data = {
                    "studentId": student_id,
                    "rollNumber": roll_num,
                    "studentName": std_name,
                    "email": std_email,
                    "status": "Present",
                    "timestamp": iso_time,
                    "eventType": "CHECK_IN",
                    "cameraId": event.camera_id or "WEBCAM-01",
                    "confidence": event.recognition_confidence,
                    "livenessScore": event.liveness_score,
                    "sessionId": self.session_id,
                    "classId": "class-csc-301-a",
                    "courseId": "course-csc-301",
                    "teacherId": "teacher-ali-01",
                    "departmentId": "dept-cs-01"
                }
                self.firebase_service.create_document("attendance", attendance_data)
                
                # Cleanup tracker
                del self._stability_tracker[student_id]
                
                return AttendanceStatus.NEWLY_MARKED, 1.0
            except Exception as e:
                logger.error(f"Failed to mark attendance for {student_id}: {e}")
                # Reset timer on error to try again
                del self._stability_tracker[student_id]
                return AttendanceStatus.STABILIZING, 0.0
                
        # Still stabilizing
        progress = min(1.0, elapsed / self.stability_seconds)
        return AttendanceStatus.STABILIZING, progress
        
    def on_face_lost(self, student_id: int) -> None:
        """
        Called when a previously recognized face is no longer in the frame.
        Resets the stability timer.
        """
        if student_id in self._stability_tracker:
            del self._stability_tracker[student_id]

    def get_unknown_count(self) -> int:
        return self._today_unknown_count
        
    def get_present_count(self) -> int:
        return len(self.db_manager.get_today_attendance())
