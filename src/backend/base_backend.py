from abc import ABC, abstractmethod
import numpy as np
from typing import Dict, List

class InferenceBackend(ABC):
    """
    Abstract interface for inference backends (ONNX Runtime, TensorRT, etc.).
    Kept for extensibility to allow adding custom models (liveness detection, etc.) 
    in the future without changing the core business logic.
    """
    
    @abstractmethod
    def load(self, model_path: str, providers: List[str]) -> None:
        """Loads the model weights into the backend."""
        pass
        
    @abstractmethod
    def infer(self, inputs: Dict[str, np.ndarray]) -> Dict[str, np.ndarray]:
        """Runs inference on the provided inputs."""
        pass
