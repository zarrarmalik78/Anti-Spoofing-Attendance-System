import os
import cv2
import numpy as np
import onnxruntime
from typing import Tuple, Dict, Any

from src.utils.logger import get_logger

logger = get_logger(__name__)

class AntiSpoofAnalyzer:
    """
    Implements Liveness Detection using MiniFASNet (Silent-Face-Anti-Spoofing).
    Evaluates whether a detected face is from a live person or a spoof attack (printed photo, screen).
    """
    def __init__(self, config: Dict[str, Any]):
        self.config = config.get("anti_spoofing", {})
        self.enabled = self.config.get("enabled", True)
        self.threshold = self.config.get("threshold", 0.90)
        
        # Absolute path resolution
        model_path = self.config.get("model_path", "models/anti_spoofing/minifasnet_v2.onnx")
        if not os.path.isabs(model_path):
            base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            model_path = os.path.join(base_dir, model_path)
            
        self.model_path = model_path
        self.session = None
        
        if self.enabled:
            self._load_model()

    def _load_model(self):
        if not os.path.exists(self.model_path):
            logger.warning(f"Anti-spoofing model not found at {self.model_path}. Disabling liveness detection.")
            self.enabled = False
            return
            
        try:
            # Load with CPUProvider (can be upgraded to TensorrtExecutionProvider for Jetson Nano)
            providers = ['CPUExecutionProvider']
            self.session = onnxruntime.InferenceSession(self.model_path, providers=providers)
            logger.info("Anti-Spoofing model (MiniFASNetV2) loaded successfully.")
        except Exception as e:
            logger.error(f"Failed to load anti-spoofing model: {e}")
            self.enabled = False

    def get_crop_box(self, box: np.ndarray, scale: float, image_shape: Tuple[int, int]) -> Tuple[int, int, int, int]:
        x1, y1, x2, y2 = box
        
        box_w = x2 - x1
        box_h = y2 - y1
        
        center_x = x1 + box_w / 2.0
        center_y = y1 + box_h / 2.0
        
        side = max(box_w, box_h) * scale
        
        new_x1 = int(center_x - side / 2.0)
        new_y1 = int(center_y - side / 2.0)
        new_x2 = int(new_x1 + side)
        new_y2 = int(new_y1 + side)
        
        return new_x1, new_y1, new_x2, new_y2

    def analyze(self, frame: np.ndarray, bbox: np.ndarray) -> Tuple[bool, float]:
        if not self.enabled or self.session is None:
            return True, 1.0
            
        try:
            # 1. Expand Bounding Box (Scale 2.7 for MiniFASNet)
            x1, y1, x2, y2 = self.get_crop_box(bbox, 2.7, frame.shape)
            
            # Extract crop with zero padding if out of bounds
            h, w = frame.shape[:2]
            side = y2 - y1
            canvas = np.zeros((side, side, 3), dtype=np.uint8)
            
            src_x1 = max(0, x1)
            src_y1 = max(0, y1)
            src_x2 = min(w, x2)
            src_y2 = min(h, y2)
            
            dst_x1 = src_x1 - x1
            dst_y1 = src_y1 - y1
            dst_x2 = dst_x1 + (src_x2 - src_x1)
            dst_y2 = dst_y1 + (src_y2 - src_y1)
            
            if src_x2 <= src_x1 or src_y2 <= src_y1:
                return False, 0.0
                
            canvas[dst_y1:dst_y2, dst_x1:dst_x2] = frame[src_y1:src_y2, src_x1:src_x2]
            face_crop = canvas
            
            # 2. Resize to 80x80
            face_crop = cv2.resize(face_crop, (80, 80))
            
            # 3. Normalize
            blob = face_crop.astype(np.float32) / 255.0
            blob = np.transpose(blob, (2, 0, 1))
            blob = np.expand_dims(blob, axis=0)
            
            # 4. Inference
            input_name = self.session.get_inputs()[0].name
            out = self.session.run(None, {input_name: blob})[0]
            
            # 5. Process Output
            exp_out = np.exp(out[0] - np.max(out[0]))
            probs = exp_out / np.sum(exp_out)
            
            # garciafido/minifasnet-v2-anti-spoofing-onnx: [print-attack, replay-attack, live]
            # Index 2 is Live (Real)
            liveness_score = float(probs[2])
            is_live = liveness_score >= self.threshold
            
            return is_live, liveness_score
            
        except Exception as e:
            logger.error(f"Anti-Spoofing inference error: {e}")
            # Fail closed for security, but we don't want to break the whole app
            return False, 0.0
