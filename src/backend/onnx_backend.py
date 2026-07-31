import numpy as np
import onnxruntime as ort
from typing import Dict, List

from .base_backend import InferenceBackend
from src.utils.logger import get_logger

logger = get_logger(__name__)

class OnnxBackend(InferenceBackend):
    """
    ONNX Runtime implementation of the InferenceBackend interface.
    """
    
    def __init__(self):
        self.session = None
        self._input_names = []
        self._output_names = []
        
    def load(self, model_path: str, providers: List[str] = None) -> None:
        """
        Loads an ONNX model into an InferenceSession.
        """
        if providers is None:
            providers = ['CPUExecutionProvider']
            
        try:
            self.session = ort.InferenceSession(model_path, providers=providers)
            self._input_names = [inp.name for inp in self.session.get_inputs()]
            self._output_names = [out.name for out in self.session.get_outputs()]
            logger.info(f"Loaded ONNX model {model_path} with providers {providers}")
        except Exception as e:
            logger.error(f"Failed to load ONNX model {model_path}: {e}")
            raise
            
    def infer(self, inputs: Dict[str, np.ndarray]) -> Dict[str, np.ndarray]:
        """
        Runs inference.
        """
        if not self.session:
            raise RuntimeError("Model not loaded. Call load() first.")
            
        # Ensure all required inputs are present
        for name in self._input_names:
            if name not in inputs:
                raise ValueError(f"Missing required input: {name}")
                
        outputs = self.session.run(self._output_names, inputs)
        
        return {name: out for name, out in zip(self._output_names, outputs)}
