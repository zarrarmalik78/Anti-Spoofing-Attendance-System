import uuid
import time
from typing import Dict, Set, Tuple
from enum import Enum

from src.database.db_manager import DatabaseManager
from src.utils.logger import get_logger

logger = get_logger(__name__)

class AttendanceStatus(Enum):
    STABILIZING = 1
    NEWLY_MARKED = 2
    ALREADY_MARKED = 3

class AttendanceManager:
    """
    Handles attendance marking logic, session deduplication, and the stability timer.
    """
    def __init__(self, db_manager: DatabaseManager, stability_seconds: float = 1.0):
        self.db_manager = db_manager
        self.stability_seconds = stability_seconds
        
        # Generate a unique session ID for this run
        self.session_id = str(uuid.uuid4())
        logger.info(f"Initialized AttendanceManager with session_id: {self.session_id}")
        
        # State
        self._marked_students: Set[int] = set()
        self._stability_tracker: Dict[int, float] = {}
        self._today_unknown_count: int = 0
        
        # Pre-load already marked students for this session (useful if app restarted with same session, though we gen UUID each time)
        records = self.db_manager.get_session_attendance(self.session_id)
        for r in records:
            self._marked_students.add(r.student_id)

    def on_face_recognized(self, student_id: int) -> Tuple[AttendanceStatus, float]:
        """
        Called continuously while a recognized face is in the frame.
        
        Returns:
            Tuple of (AttendanceStatus, progress_percentage 0.0-1.0)
        """
        if student_id in self._marked_students:
            return AttendanceStatus.ALREADY_MARKED, 1.0
            
        current_time = time.monotonic()
        
        if student_id not in self._stability_tracker:
            self._stability_tracker[student_id] = current_time
            return AttendanceStatus.STABILIZING, 0.0
            
        elapsed = current_time - self._stability_tracker[student_id]
        
        if elapsed >= self.stability_seconds:
            # Mark attendance
            try:
                self.db_manager.insert_attendance(student_id, self.session_id)
                self._marked_students.add(student_id)
                
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

    def increment_unknown(self) -> None:
        """Tracks unknown faces seen today."""
        # Simple counter for now, could be debounced
        self._today_unknown_count += 1
        
    def get_unknown_count(self) -> int:
        return self._today_unknown_count
        
    def get_present_count(self) -> int:
        # For session based, this is len(_marked_students)
        # But for "Today's Attendance" we might want all records from DB for today
        return len(self.db_manager.get_today_attendance())
