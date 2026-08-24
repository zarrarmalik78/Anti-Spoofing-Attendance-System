import os
import sys
import cv2
import numpy as np
from typing import Tuple, Dict, Any

from src.utils.logger import get_logger

logger = get_logger(__name__)

# ─────────────────────────────────────────────────────────────────────────────
# Official CropImage from minivision-ai/Silent-Face-Anti-Spoofing
# Key difference vs our old code: no zero-padding, boundary overflow is
# corrected by SHIFTING the crop window back inside the image.
# ─────────────────────────────────────────────────────────────────────────────
class _CropImage:
    @staticmethod
    def _get_new_box(src_w: int, src_h: int, bbox, scale: float):
        """
        bbox format: [x, y, w, h]   (top-left corner + dimensions)
        Returns: (left_top_x, left_top_y, right_bottom_x, right_bottom_y)
        Scale is clamped so the window never exceeds the image, and the window
        is SHIFTED (not zero-padded) if it would run off an edge.
        """
        x, y, box_w, box_h = bbox[0], bbox[1], bbox[2], bbox[3]

        # Clamp scale so the expanded box stays inside the image
        scale = min((src_h - 1) / box_h, min((src_w - 1) / box_w, scale))

        new_width  = box_w * scale
        new_height = box_h * scale
        center_x   = box_w / 2 + x
        center_y   = box_h / 2 + y

        lt_x = center_x - new_width  / 2
        lt_y = center_y - new_height / 2
        rb_x = center_x + new_width  / 2
        rb_y = center_y + new_height / 2

        # Shift back in-bounds (no zero-padding)
        if lt_x < 0:
            rb_x -= lt_x
            lt_x  = 0
        if lt_y < 0:
            rb_y -= lt_y
            lt_y  = 0
        if rb_x > src_w - 1:
            lt_x -= (rb_x - src_w + 1)
            rb_x  = src_w - 1
        if rb_y > src_h - 1:
            lt_y -= (rb_y - src_h + 1)
            rb_y  = src_h - 1

        return int(lt_x), int(lt_y), int(rb_x), int(rb_y)

    def crop(self, org_img: np.ndarray, bbox, scale: float,
             out_w: int, out_h: int) -> np.ndarray:
        """Crop with 2.7x (or other) scale, then resize to out_w × out_h."""
        src_h, src_w, _ = org_img.shape
        lt_x, lt_y, rb_x, rb_y = self._get_new_box(src_w, src_h, bbox, scale)
        cropped = org_img[lt_y: rb_y + 1, lt_x: rb_x + 1]
        return cv2.resize(cropped, (out_w, out_h))


# ─────────────────────────────────────────────────────────────────────────────
# PyTorch model loader — loaded lazily on first call to analyze()
# ─────────────────────────────────────────────────────────────────────────────
class AntiSpoofAnalyzer:
    """
    Liveness detection using the official Silent-Face-Anti-Spoofing ensemble.

    Model: minivision-ai/Silent-Face-Anti-Spoofing
    Two-model ensemble (MiniFASNetV2 + MiniFASNetV1SE), PyTorch inference.
    Label indexing:  index 1 → Real/Live,  index 0 or 2 → Fake/Spoof
    (This is the OFFICIAL label convention from test.py in the source repo.)

    Input format:
      - bbox must be [x, y, w, h]  (InsightFace gives [x1,y1,x2,y2], converted below)
      - frame must be BGR (as returned by OpenCV / CameraManager)
    """

    # Class indices from official test.py: label==1 → Real
    _LIVE_CLASS_IDX = 1

    def __init__(self, config: Dict[str, Any]):
        cfg = config.get("anti_spoofing", {})
        self.enabled   = cfg.get("enabled", True)
        self.threshold = cfg.get("threshold", 0.6)   # liveness score >= threshold → live

        # Resolve model directory (contains both .pth files)
        model_dir = cfg.get("model_dir", "models/anti_spoofing/pt_models")
        if not os.path.isabs(model_dir):
            base = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            model_dir = os.path.join(base, model_dir)
        self.model_dir = model_dir

        # Diagnostic mode – print full tensor stats every N frames
        self._diag_every = cfg.get("diagnostic_every", 0)   # 0 = off
        self._diag_count = 0

        self._crop = _CropImage()
        self._models: list = []    # list of (torch.nn.Module, scale, h, w)

        if self.enabled:
            self._load_models()

    # ── Model Loading ──────────────────────────────────────────────────────────
    def _load_models(self):
        """Load both .pth files from model_dir using PyTorch (not ONNX)."""
        if not os.path.isdir(self.model_dir):
            logger.warning(
                f"Anti-spoofing model directory not found: {self.model_dir}. "
                "Liveness detection disabled."
            )
            self.enabled = False
            return

        # Add Silent-Face repo to path if present (for the network definitions)
        repo_src = os.path.join(
            os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
            "scratch", "Silent-Face-Anti-Spoofing"
        )
        if os.path.isdir(repo_src) and repo_src not in sys.path:
            sys.path.insert(0, repo_src)

        try:
            import torch
            import torch.nn.functional as F
            from src.model_lib.MiniFASNet import (
                MiniFASNetV1, MiniFASNetV2, MiniFASNetV1SE, MiniFASNetV2SE
            )
            from src.utility import get_kernel, parse_model_name
        except ImportError as e:
            logger.error(
                f"Cannot import MiniFASNet: {e}. "
                "Make sure scratch/Silent-Face-Anti-Spoofing is present."
            )
            self.enabled = False
            return

        MODEL_MAP = {
            "MiniFASNetV1":   MiniFASNetV1,
            "MiniFASNetV2":   MiniFASNetV2,
            "MiniFASNetV1SE": MiniFASNetV1SE,
            "MiniFASNetV2SE": MiniFASNetV2SE,
        }

        pth_files = [f for f in os.listdir(self.model_dir) if f.endswith(".pth")]
        if not pth_files:
            logger.warning(f"No .pth model files found in {self.model_dir}. Disabling.")
            self.enabled = False
            return

        import torch
        for fname in pth_files:
            path = os.path.join(self.model_dir, fname)
            try:
                h_in, w_in, model_type, scale = parse_model_name(fname)
                kernel = get_kernel(h_in, w_in)
                net = MODEL_MAP[model_type](conv6_kernel=kernel, num_classes=3)
                sd = torch.load(path, map_location="cpu")
                if list(sd.keys())[0].startswith("module."):
                    sd = {k[7:]: v for k, v in sd.items()}
                net.load_state_dict(sd, strict=True)
                net.eval()
                self._models.append((net, scale, h_in, w_in))
                logger.info(
                    f"Loaded anti-spoof model: {fname} "
                    f"(type={model_type}, scale={scale}, input={h_in}×{w_in})"
                )
            except Exception as e:
                logger.error(f"Failed to load anti-spoof model {fname}: {e}")

        if not self._models:
            logger.error("No anti-spoof models loaded. Disabling liveness detection.")
            self.enabled = False
        else:
            logger.info(
                f"Anti-Spoofing ensemble ready with {len(self._models)} model(s). "
                f"Threshold={self.threshold:.2f}, LiveClass={self._LIVE_CLASS_IDX}"
            )

    # ── Inference ─────────────────────────────────────────────────────────────
    def analyze(self, frame: np.ndarray, bbox: np.ndarray) -> Tuple[bool, float]:
        """
        Parameters
        ----------
        frame : np.ndarray   BGR image (full camera frame)
        bbox  : np.ndarray   [x1, y1, x2, y2]  (InsightFace format)

        Returns
        -------
        (is_live, liveness_score)
          liveness_score ∈ [0, 1]  — probability that class 1 (Real) is predicted
        """
        if not self.enabled or not self._models:
            return True, 1.0

        # Convert InsightFace bbox [x1,y1,x2,y2] → [x, y, w, h]
        x1, y1, x2, y2 = int(bbox[0]), int(bbox[1]), int(bbox[2]), int(bbox[3])
        xywh = [x1, y1, x2 - x1, y2 - y1]

        try:
            import torch
            import torch.nn.functional as F_torch

            prediction = np.zeros((1, 3), dtype=np.float32)
            self._diag_count += 1
            diag = (self._diag_every > 0 and self._diag_count % self._diag_every == 0)

            for net, scale, h_in, w_in in self._models:
                # 1. Crop with the official SHIFT-based boundary handling
                crop = self._crop.crop(frame, xywh, scale=scale, out_w=w_in, out_h=h_in)

                if diag:
                    logger.debug(
                        f"[AntiSpoof DIAG] crop shape={crop.shape} "
                        f"min={crop.min()} max={crop.max()} mean={crop.mean():.2f}"
                    )

                # 2. Preprocess: BGR [0,255] → float [0,255], HWC → NCHW
                tensor = torch.from_numpy(crop).permute(2, 0, 1).float()
                tensor = tensor.unsqueeze(0)   # (1, C, H, W)

                if diag:
                    logger.debug(
                        f"[AntiSpoof DIAG] tensor shape={tuple(tensor.shape)} "
                        f"min={tensor.min():.4f} max={tensor.max():.4f} mean={tensor.mean():.4f}"
                    )

                # 3. Inference
                with torch.no_grad():
                    raw = net(tensor)
                    probs = F_torch.softmax(raw, dim=1).squeeze(0).numpy()

                if diag:
                    logger.debug(
                        f"[AntiSpoof DIAG] raw={raw[0].numpy().round(4)} "
                        f"softmax={probs.round(4)} "
                        f"live_class({self._LIVE_CLASS_IDX})={probs[self._LIVE_CLASS_IDX]:.4f}"
                    )

                prediction += probs

            # 4. Ensemble decision (sum of softmax, argmax, official label==1 → live)
            label = int(np.argmax(prediction[0]))
            live_raw = float(prediction[0][self._LIVE_CLASS_IDX])
            # Normalise to [0,1] across the number of models for a clean score
            liveness_score = live_raw / len(self._models)
            is_live = label == self._LIVE_CLASS_IDX

            if diag:
                logger.debug(
                    f"[AntiSpoof DIAG] ensemble prediction={prediction[0].round(4)} "
                    f"label={label} is_live={is_live} liveness_score={liveness_score:.4f}"
                )

            return is_live, liveness_score

        except Exception as e:
            logger.error(f"Anti-Spoofing inference error: {e}", exc_info=True)
            return True, 1.0   # fail-open to avoid blocking legitimate users
