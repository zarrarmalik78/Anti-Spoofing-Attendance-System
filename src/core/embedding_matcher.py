import numpy as np
from typing import Tuple, Optional, List
import threading

from src.database.db_manager import DatabaseManager, StudentRecord
from src.utils.logger import get_logger

logger = get_logger(__name__)

class EmbeddingMatcher:
    """
    Manages an in-memory matrix of all registered student embeddings for fast batch matching.
    """
    def __init__(self, db_manager: DatabaseManager):
        self.db_manager = db_manager
        self.students: List[StudentRecord] = []
        self.embedding_matrix: Optional[np.ndarray] = None
        self._lock = threading.Lock()
        self.reload()

    def reload(self) -> None:
        """
        Loads all students from the database and builds the embedding matrix.
        Should be called at startup and after a new student is registered.
        """
        with self._lock:
            self.students = self.db_manager.get_all_students()
            if not self.students:
                self.embedding_matrix = None
                logger.info("No registered students found in database.")
                return

            # Stack all embeddings into an (N, 512) matrix
            embeddings = [student.embedding for student in self.students]
            self.embedding_matrix = np.vstack(embeddings)
            logger.info(f"Loaded {len(self.students)} student embeddings for matching.")

    def match(self, query_emb: np.ndarray, threshold: float = 0.45) -> Tuple[Optional[StudentRecord], float]:
        """
        Matches a query embedding against the loaded database.
        Since embeddings are L2-normalized, dot product is equivalent to cosine similarity.
        
        Args:
            query_emb: (512,) L2-normalized feature vector
            threshold: Minimum similarity score required for a match
            
        Returns:
            Tuple of (StudentRecord if match else None, best_score)
        """
        with self._lock:
            if self.embedding_matrix is None or len(self.students) == 0:
                return None, 0.0

            # Batch compute cosine similarities: (N, 512) @ (512,) -> (N,)
            scores = self.embedding_matrix @ query_emb
            
            best_idx = np.argmax(scores)
            best_score = scores[best_idx]

            if best_score >= threshold:
                return self.students[best_idx], float(best_score)
            
            return None, float(best_score)
            
    def student_count(self) -> int:
        """Returns the number of loaded student embeddings."""
        with self._lock:
            return len(self.students)
