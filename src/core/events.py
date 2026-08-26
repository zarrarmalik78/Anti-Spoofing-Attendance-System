import time
from enum import Enum
from dataclasses import dataclass
from typing import Optional, List

class EventType(Enum):
    RECOGNIZED = "RECOGNIZED"
    UNKNOWN = "UNKNOWN"
    SPOOF = "SPOOF"
    NO_FACE = "NO_FACE"

@dataclass
class RecognitionEvent:
    """
    Standardized event object returned by the AI Engine.
    Acts as a clean interface between AI processing and business/attendance logic.
    """
    timestamp: float
    bbox: List[int]  # [x1, y1, x2, y2]
    event_type: EventType
    
    student_id: Optional[int] = None
    student_name: Optional[str] = None
    student_roll: Optional[str] = None
    
    recognition_confidence: float = 0.0
    
    is_live: bool = False
    liveness_score: float = 0.0
    
    camera_id: str = "WEBCAM-01"
    device_id: str = "LAPTOP-01"
