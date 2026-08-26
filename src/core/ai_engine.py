import time
import numpy as np
from typing import List

from src.core.face_engine import FaceEngine
from src.core.embedding_matcher import EmbeddingMatcher
from src.core.events import EventType, RecognitionEvent
from src.utils.logger import get_logger

logger = get_logger(__name__)

class AIEngine:
    """
    High-level AI orchestrator that unifies face detection, liveness, and recognition.
    Returns clean RecognitionEvent objects to decouple AI from business logic.
    """
    def __init__(self, face_engine: FaceEngine, embedding_matcher: EmbeddingMatcher, similarity_threshold: float = 0.45):
        self.face_engine = face_engine
        self.embedding_matcher = embedding_matcher
        self.similarity_threshold = similarity_threshold
        
        # Hardcoded for Phase 1 as per instructions
        self.camera_id = "WEBCAM-01"
        self.device_id = "LAPTOP-01"

    def process_frame(self, frame: np.ndarray) -> List[RecognitionEvent]:
        """
        Takes a raw camera frame and returns a list of standardized recognition events.
        """
        faces = self.face_engine.detect_and_embed(frame)
        events = []
        
        if not faces:
            # We don't necessarily need to emit NO_FACE for every empty frame,
            # but if required by architecture, we could return a NO_FACE event.
            # Currently skipping emitting NO_FACE to avoid log spam, 
            # but the EventType is available.
            return events
            
        timestamp = time.time()
        
        for face in faces:
            x1, y1, x2, y2 = map(int, face.bbox)
            bbox = [x1, y1, x2, y2]
            
            is_live = getattr(face, 'is_live', True)
            liveness_score = getattr(face, 'liveness_score', 1.0)
            
            if not is_live:
                events.append(RecognitionEvent(
                    timestamp=timestamp,
                    bbox=bbox,
                    event_type=EventType.SPOOF,
                    is_live=is_live,
                    liveness_score=liveness_score,
                    camera_id=self.camera_id,
                    device_id=self.device_id
                ))
                continue
                
            # Perform embedding matching for live faces
            student, score = self.embedding_matcher.match(face.embedding, threshold=self.similarity_threshold)
            
            if student is None:
                events.append(RecognitionEvent(
                    timestamp=timestamp,
                    bbox=bbox,
                    event_type=EventType.UNKNOWN,
                    is_live=is_live,
                    liveness_score=liveness_score,
                    camera_id=self.camera_id,
                    device_id=self.device_id
                ))
            else:
                events.append(RecognitionEvent(
                    timestamp=timestamp,
                    bbox=bbox,
                    event_type=EventType.RECOGNIZED,
                    student_id=student.id,
                    student_name=student.name,
                    student_roll=student.roll_number,
                    recognition_confidence=score,
                    is_live=is_live,
                    liveness_score=liveness_score,
                    camera_id=self.camera_id,
                    device_id=self.device_id
                ))
                
        return events
