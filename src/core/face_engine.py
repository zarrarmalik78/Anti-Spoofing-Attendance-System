import numpy as np
from insightface.app import FaceAnalysis
from dataclasses import dataclass
from typing import List

from src.utils.logger import get_logger

logger = get_logger(__name__)

@dataclass
class FaceResult:
    """
    Data class representing the result of face detection and embedding.
    """
    bbox: np.ndarray        # [x1, y1, x2, y2]
    landmarks: np.ndarray   # 5x2 points
    det_score: float
    embedding: np.ndarray = None  # 512-d L2-normalized feature vector (None if spoofed)
    is_live: bool = True
    liveness_score: float = 1.0

    @classmethod
    def from_insightface(cls, face, is_live=True, liveness_score=1.0) -> 'FaceResult':
        """Constructs a FaceResult from InsightFace's Face object."""
        return cls(
            bbox=face.bbox,
            landmarks=face.kps,
            embedding=face.normed_embedding if hasattr(face, 'normed_embedding') else None,
            det_score=face.det_score,
            is_live=is_live,
            liveness_score=liveness_score
        )

class FaceEngine:
    """
    Wrapper around InsightFace's FaceAnalysis API.
    Handles detection, alignment, and ArcFace feature extraction internally.
    """
    def __init__(self, config: dict, model_root: str = "models", pack_name: str = "buffalo_l", 
                 providers: List[str] = None):
        if providers is None:
            providers = ['CPUExecutionProvider']
            
        try:
            self._app = FaceAnalysis(name=pack_name, root=model_root, providers=providers)
            # Initialize with default context (ctx_id=0 for first GPU if available, else CPU)
            # det_size=(640, 640) is recommended for SCRFD
            self._app.prepare(ctx_id=0, det_size=(640, 640))
            logger.info(f"Initialized FaceEngine with models from {model_root} and providers {providers}")
            
            # Anti-Spoofing enabled (PyTorch ensemble, two-model, label==1=Real)
            from src.core.anti_spoofing import AntiSpoofAnalyzer
            self.anti_spoof = AntiSpoofAnalyzer(config)
        except Exception as e:
            logger.error(f"Failed to initialize FaceEngine: {e}")
            raise

    def detect_and_embed(self, frame: np.ndarray) -> List[FaceResult]:
        """
        Processes a BGR image frame.
        Detects faces, checks liveness, and only generates embeddings for live faces.
        Returns a list of FaceResult objects.
        """
        try:
            # 1. Detection
            # InsightFace's get() usually does everything, but we can do it step by step
            bboxes, kpss = self._app.models['detection'].detect(frame, max_num=0)
            if bboxes.shape[0] == 0:
                return []
                
            from insightface.app.common import Face
            results = []
            
            for i in range(bboxes.shape[0]):
                bbox = bboxes[i, 0:4]
                det_score = bboxes[i, 4]
                kps = kpss[i] if kpss is not None else None
                face = Face(bbox=bbox, kps=kps, det_score=det_score)
                
                # 2. Anti-Spoofing Check
                if self.anti_spoof is not None:
                    is_live, liveness_score = self.anti_spoof.analyze(frame, bbox)
                else:
                    is_live, liveness_score = True, 1.0
                
                if is_live:
                    # 3. Recognition (Embedding generation)
                    # Run other models (alignment, recognition)
                    for model_name, model in self._app.models.items():
                        if model_name != 'detection':
                            model.get(frame, face)
                
                results.append(FaceResult.from_insightface(face, is_live, liveness_score))
                
            return results
        except Exception as e:
            logger.error(f"Error during face processing: {e}")
            return []
