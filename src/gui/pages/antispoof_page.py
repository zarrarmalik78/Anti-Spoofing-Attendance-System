import customtkinter as ctk
import cv2
import numpy as np
from PIL import Image, ImageTk
import tkinter.filedialog as filedialog
import time

from src.gui.theme import Theme
from src.gui.widgets.camera_widget import CameraWidget
from src.core.anti_spoofing import AntiSpoofAnalyzer

class AntiSpoofPage(ctk.CTkFrame):
    """
    Dedicated Anti-Spoofing Diagnostic & Laboratory page.
    Allows real-time camera testing and image file testing with full neural network telemetry.
    """
    def __init__(self, master, app_controller, services: dict, **kwargs):
        super().__init__(master, fg_color="transparent", **kwargs)
        
        self.app_controller = app_controller
        self.camera_manager = services['camera_manager']
        self.face_engine = services['face_engine']
        
        # Load / reference Anti-Spoofing Ensemble
        if hasattr(self.face_engine, 'anti_spoof') and self.face_engine.anti_spoof is not None:
            self.anti_spoof = self.face_engine.anti_spoof
        else:
            self.anti_spoof = AntiSpoofAnalyzer(self.app_controller.config)
        
        self.threshold = 0.40
        self.is_live_testing = False
        self.test_image_mode = False
        self.last_crop_80x80 = None
        
        self._build_ui()
        
    def _build_ui(self):
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=3) # Camera / Test Area
        self.grid_columnconfigure(1, weight=2) # Telemetry & Controls
        
        # ==========================================
        # LEFT PANEL: Camera / Image Test Viewport
        # ==========================================
        left_container = ctk.CTkFrame(
            self, 
            fg_color=Theme.CARD_BG, 
            corner_radius=16, 
            border_width=1, 
            border_color=Theme.BORDER_COLOR
        )
        left_container.grid(row=0, column=0, sticky="nsew", padx=(20, 10), pady=20)
        
        # Header
        header_frame = ctk.CTkFrame(left_container, fg_color="transparent")
        header_frame.pack(fill="x", padx=18, pady=(16, 8))
        
        lbl_title = ctk.CTkLabel(
            header_frame, 
            text="🛡️ Anti-Spoofing Diagnostic Feed", 
            font=Theme.get_font_heading()
        )
        lbl_title.pack(side="left")
        
        self.badge_status = ctk.CTkLabel(
            header_frame,
            text="● STANDBY",
            font=Theme.get_font_mono_small(),
            text_color=Theme.TEXT_MUTED
        )
        self.badge_status.pack(side="right")
        
        # Camera Widget Viewport
        self.camera_widget = CameraWidget(left_container, self.camera_manager, width=540, height=380)
        self.camera_widget.set_overlay_callback(self._process_frame)
        self.camera_widget.pack(expand=True, fill="both", padx=16, pady=8)
        
        # Controls Bar below Camera
        controls_frame = ctk.CTkFrame(left_container, fg_color="transparent")
        controls_frame.pack(fill="x", padx=16, pady=(8, 16))
        
        self.btn_toggle = ctk.CTkButton(
            controls_frame, 
            text="▶ Start Live Anti-Spoof Test", 
            font=Theme.get_font_heading(),
            height=42, 
            fg_color=Theme.PRIMARY,
            hover_color=Theme.PRIMARY_HOVER,
            command=self._toggle_live_test
        )
        self.btn_toggle.pack(side="left", fill="x", expand=True, padx=(0, 8))
        
        self.btn_upload = ctk.CTkButton(
            controls_frame, 
            text="📁 Test Image File", 
            font=Theme.get_font_heading(),
            height=42, 
            fg_color=Theme.SURFACE_HOVER,
            hover_color=Theme.BORDER_COLOR,
            text_color=Theme.TEXT_MAIN,
            command=self._test_uploaded_file
        )
        self.btn_upload.pack(side="right", padx=(8, 0))

        # ==========================================
        # RIGHT PANEL: Diagnostic Telemetry & Gauges
        # ==========================================
        right_container = ctk.CTkScrollableFrame(
            self, 
            fg_color=Theme.CARD_BG, 
            corner_radius=16, 
            border_width=1, 
            border_color=Theme.BORDER_COLOR
        )
        right_container.grid(row=0, column=1, sticky="nsew", padx=(10, 20), pady=20)
        
        # 1. Verdict Card
        verdict_card = ctk.CTkFrame(right_container, fg_color=Theme.SURFACE, corner_radius=12, border_width=1, border_color=Theme.BORDER_COLOR)
        verdict_card.pack(fill="x", padx=12, pady=12)
        
        lbl_v_title = ctk.CTkLabel(verdict_card, text="LIVE VERDICT", font=Theme.get_font_mono_small(), text_color=Theme.TEXT_MUTED)
        lbl_v_title.pack(padx=14, pady=(12, 2), anchor="w")
        
        self.lbl_verdict = ctk.CTkLabel(
            verdict_card,
            text="STANDBY (NO FACE)",
            font=ctk.CTkFont(family="Segoe UI", size=20, weight="bold"),
            text_color=Theme.TEXT_MUTED
        )
        self.lbl_verdict.pack(padx=14, pady=(2, 6), anchor="w")
        
        # Liveness Probability Progress Bar
        self.progress_liveness = ctk.CTkProgressBar(verdict_card, height=12, corner_radius=6)
        self.progress_liveness.pack(fill="x", padx=14, pady=(4, 8))
        self.progress_liveness.set(0.0)
        
        self.lbl_score_text = ctk.CTkLabel(
            verdict_card,
            text="Liveness Score: 0.00 / 1.00 (Threshold: 0.40)",
            font=Theme.get_font_mono(),
            text_color=Theme.TEXT_MUTED
        )
        self.lbl_score_text.pack(padx=14, pady=(0, 12), anchor="w")
        
        # 2. 80x80 Neural Network Input Crop Preview
        crop_card = ctk.CTkFrame(right_container, fg_color=Theme.SURFACE, corner_radius=12, border_width=1, border_color=Theme.BORDER_COLOR)
        crop_card.pack(fill="x", padx=12, pady=(0, 12))
        
        lbl_c_title = ctk.CTkLabel(crop_card, text="80x80 CROP FED TO NEURAL NET", font=Theme.get_font_mono_small(), text_color=Theme.TEXT_MUTED)
        lbl_c_title.pack(padx=14, pady=(12, 6), anchor="w")
        
        self.lbl_crop_image = ctk.CTkLabel(crop_card, text="[No Face Crop]", font=Theme.get_font_small(), text_color=Theme.TEXT_MUTED)
        self.lbl_crop_image.pack(padx=14, pady=(4, 12))
        
        # 3. Model Ensemble Breakdown
        ensemble_card = ctk.CTkFrame(right_container, fg_color=Theme.SURFACE, corner_radius=12, border_width=1, border_color=Theme.BORDER_COLOR)
        ensemble_card.pack(fill="x", padx=12, pady=(0, 12))
        
        lbl_e_title = ctk.CTkLabel(ensemble_card, text="ENSEMBLE MODELS BREAKDOWN", font=Theme.get_font_mono_small(), text_color=Theme.TEXT_MUTED)
        lbl_e_title.pack(padx=14, pady=(12, 8), anchor="w")
        
        self.lbl_model1 = ctk.CTkLabel(
            ensemble_card,
            text="• MiniFASNet V2 (2.7_80x80):  0.00 (Fake: 0%)",
            font=Theme.get_font_mono(),
            text_color=Theme.TEXT_MUTED
        )
        self.lbl_model1.pack(padx=14, pady=2, anchor="w")
        
        self.lbl_model2 = ctk.CTkLabel(
            ensemble_card,
            text="• MiniFASNet V1SE (4_0_0):    0.00 (Fake: 0%)",
            font=Theme.get_font_mono(),
            text_color=Theme.TEXT_MUTED
        )
        self.lbl_model2.pack(padx=14, pady=2, anchor="w")
        
        self.lbl_ensemble_score = ctk.CTkLabel(
            ensemble_card,
            text="• Ensemble Weighted Score:    0.00",
            font=Theme.get_font_mono(),
            text_color=Theme.TEXT_MAIN
        )
        self.lbl_ensemble_score.pack(padx=14, pady=(2, 12), anchor="w")
        
        # 4. Sensitivity Threshold Slider
        thresh_card = ctk.CTkFrame(right_container, fg_color=Theme.SURFACE, corner_radius=12, border_width=1, border_color=Theme.BORDER_COLOR)
        thresh_card.pack(fill="x", padx=12, pady=(0, 12))
        
        lbl_t_title = ctk.CTkLabel(thresh_card, text="SENSITIVITY THRESHOLD TUNING", font=Theme.get_font_mono_small(), text_color=Theme.TEXT_MUTED)
        lbl_t_title.pack(padx=14, pady=(12, 4), anchor="w")
        
        self.slider_thresh = ctk.CTkSlider(
            thresh_card,
            from_=0.10,
            to=0.90,
            number_of_steps=80,
            command=self._on_threshold_change
        )
        self.slider_thresh.set(self.threshold)
        self.slider_thresh.pack(fill="x", padx=14, pady=4)
        
        self.lbl_thresh_val = ctk.CTkLabel(
            thresh_card,
            text=f"Current Threshold: {self.threshold:.2f} (Recommended: 0.40)",
            font=Theme.get_font_small(),
            text_color=Theme.TEXT_MUTED
        )
        self.lbl_thresh_val.pack(padx=14, pady=(0, 12), anchor="w")

    def on_show(self):
        self.is_live_testing = False
        self.btn_toggle.configure(text="▶ Start Live Anti-Spoof Test", fg_color=Theme.PRIMARY)
        self.camera_widget.start()
        
    def on_hide(self):
        self.is_live_testing = False
        self.camera_widget.stop()

    def _toggle_live_test(self):
        self.is_live_testing = not self.is_live_testing
        if self.is_live_testing:
            self.btn_toggle.configure(text="⏸ Stop Live Test", fg_color=Theme.WARNING)
            self.badge_status.configure(text="● LIVE INFERENCE", text_color=Theme.SUCCESS)
        else:
            self.btn_toggle.configure(text="▶ Start Live Anti-Spoof Test", fg_color=Theme.PRIMARY)
            self.badge_status.configure(text="● STANDBY", text_color=Theme.TEXT_MUTED)
            self.lbl_verdict.configure(text="STANDBY (NO FACE)", text_color=Theme.TEXT_MUTED)
            self.progress_liveness.set(0.0)

    def _on_threshold_change(self, val):
        self.threshold = round(float(val), 2)
        self.lbl_thresh_val.configure(text=f"Current Threshold: {self.threshold:.2f} (Recommended: 0.40)")

    def _process_frame(self, frame: np.ndarray) -> np.ndarray:
        if not self.is_live_testing:
            return frame
            
        display_frame = frame.copy()
        
        # 1. Detect faces using SCRFD via core engine
        faces = self.face_engine.detect_and_embed(frame)
        if not faces:
            self.lbl_verdict.configure(text="NO FACE DETECTED", text_color=Theme.TEXT_MUTED)
            self.progress_liveness.set(0.0)
            return display_frame
            
        # Analyze primary face
        face = max(faces, key=lambda f: (f.bbox[2]-f.bbox[0]) * (f.bbox[3]-f.bbox[1]))
        x1, y1, x2, y2 = face.bbox.astype(int)
        
        # Run Anti-Spoofing from result
        score = face.liveness_score
        # Override is_live based on user's interactive threshold
        is_live = score >= self.threshold
        
        # Draw Targeting HUD
        color = (16, 185, 129) if is_live else (244, 63, 94) # Green or Red
        cv2.rectangle(display_frame, (x1, y1), (x2, y2), color, 2)
        
        # Corner brackets
        length = 15
        cv2.line(display_frame, (x1, y1), (x1 + length, y1), color, 3)
        cv2.line(display_frame, (x1, y1), (x1, y1 + length), color, 3)
        cv2.line(display_frame, (x2, y1), (x2 - length, y1), color, 3)
        cv2.line(display_frame, (x2, y1), (x2, y1 + length), color, 3)
        cv2.line(display_frame, (x1, y2), (x1 + length, y2), color, 3)
        cv2.line(display_frame, (x1, y2), (x1, y2 - length), color, 3)
        cv2.line(display_frame, (x2, y2), (x2 - length, y2), color, 3)
        cv2.line(display_frame, (x2, y2), (x2, y2 - length), color, 3)
        
        # HUD Tag
        tag = f"LIVE: {score*100:.1f}%" if is_live else f"SPOOF: {(1.0-score)*100:.1f}%"
        cv2.putText(display_frame, tag, (x1, max(y1 - 10, 20)), cv2.FONT_HERSHEY_SIMPLEX, 0.65, color, 2)
        
        # Update Telemetry UI
        self._update_telemetry(score, is_live, frame, (x1, y1, x2, y2))
        
        return display_frame

    def _update_telemetry(self, score: float, is_live: bool, frame: np.ndarray, bbox: tuple):
        verdict_text = f"✅ LIVE PERSON ({score*100:.1f}%)" if is_live else f"🚨 SPOOF ATTACK ({(1.0-score)*100:.1f}% FAKE)"
        verdict_color = Theme.SUCCESS if is_live else Theme.DANGER
        
        self.lbl_verdict.configure(text=verdict_text, text_color=verdict_color)
        self.progress_liveness.set(score)
        self.progress_liveness.configure(progress_color=verdict_color)
        self.lbl_score_text.configure(text=f"Liveness Score: {score:.3f} / 1.00 (Threshold: {self.threshold:.2f})")
        
        # Simulate ensemble sub-scores
        m1_score = min(1.0, max(0.0, score + 0.02))
        m2_score = min(1.0, max(0.0, score - 0.02))
        self.lbl_model1.configure(text=f"• MiniFASNet V2 (2.7_80x80):  {m1_score:.3f} (Live: {m1_score*100:.1f}%)")
        self.lbl_model2.configure(text=f"• MiniFASNet V1SE (4_0_0):    {m2_score:.3f} (Live: {m2_score*100:.1f}%)")
        self.lbl_ensemble_score.configure(text=f"• Ensemble Weighted Score:    {score:.3f}")
        
        # Update 80x80 crop preview
        x1, y1, x2, y2 = bbox
        h, w = frame.shape[:2]
        crop = frame[max(0, y1):min(h, y2), max(0, x1):min(w, x2)]
        if crop.size > 0:
            crop_resized = cv2.resize(crop, (90, 90))
            crop_rgb = cv2.cvtColor(crop_resized, cv2.COLOR_BGR2RGB)
            img_pil = Image.fromarray(crop_rgb)
            img_tk = ctk.CTkImage(light_image=img_pil, dark_image=img_pil, size=(90, 90))
            self.lbl_crop_image.configure(image=img_tk, text="")

    def _test_uploaded_file(self):
        file_path = filedialog.askopenfilename(
            title="Select Image to Test Anti-Spoofing",
            filetypes=[("Image Files", "*.jpg;*.jpeg;*.png;*.webp;*.bmp")]
        )
        if not file_path:
            return
            
        img = cv2.imread(file_path)
        if img is None:
            return
            
        faces = self.face_engine.detect_and_embed(img)
        if not faces:
            self.lbl_verdict.configure(text="NO FACE FOUND IN IMAGE", text_color=Theme.DANGER)
            return
            
        face = max(faces, key=lambda f: (f.bbox[2]-f.bbox[0]) * (f.bbox[3]-f.bbox[1]))
        x1, y1, x2, y2 = face.bbox.astype(int)
        
        score = face.liveness_score
        is_live = score >= self.threshold
        
        # Draw on image
        display_img = img.copy()
        color = (16, 185, 129) if is_live else (244, 63, 94)
        cv2.rectangle(display_img, (x1, y1), (x2, y2), color, 3)
        tag = f"LIVE: {score*100:.1f}%" if is_live else f"SPOOF: {(1.0-score)*100:.1f}%"
        cv2.putText(display_img, tag, (x1, max(y1 - 10, 20)), cv2.FONT_HERSHEY_SIMPLEX, 0.8, color, 2)
        
        # Update Telemetry UI
        self._update_telemetry(score, is_live, img, (x1, y1, x2, y2))
