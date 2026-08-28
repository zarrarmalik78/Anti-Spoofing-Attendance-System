import customtkinter as ctk
import cv2
import numpy as np
import datetime
import math

from src.gui.theme import Theme
from src.gui.widgets.camera_widget import CameraWidget
from src.core.attendance_engine import AttendanceStatus
from src.core.events import EventType

class RecognitionPage(ctk.CTkFrame):
    """
    Dedicated Full-Screen Live Recognition Page with high-tech HUD and live telemetry log.
    """
    def __init__(self, master, app_controller, services: dict, **kwargs):
        super().__init__(master, fg_color="transparent", **kwargs)
        
        self.app_controller = app_controller
        self.camera_manager = services['camera_manager']
        self.ai_engine = services['ai_engine']
        self.attendance_engine = services['attendance_engine']
        self.db_manager = services['db_manager']
        
        self.sim_threshold = self.app_controller.config.get("recognition", {}).get("similarity_threshold", 0.45)
        
        self.is_recognizing = False
        self._last_face_ids = set()
        
        self._build_ui()
        
    def _build_ui(self):
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=3) # Camera
        self.grid_columnconfigure(1, weight=2) # Live Telemetry Log
        
        # Left Panel - Camera
        left_frame = ctk.CTkFrame(
            self, 
            fg_color=Theme.CARD_BG, 
            corner_radius=16, 
            border_width=1, 
            border_color=Theme.BORDER_COLOR
        )
        left_frame.grid(row=0, column=0, sticky="nsew", padx=(20, 10), pady=20)
        
        top_bar = ctk.CTkFrame(left_frame, fg_color="transparent")
        top_bar.pack(fill="x", padx=16, pady=(16, 8))
        
        lbl_title = ctk.CTkLabel(
            top_bar, 
            text="📷 Live AI Facial Recognition Feed", 
            font=Theme.get_font_heading()
        )
        lbl_title.pack(side="left")
        
        self.btn_toggle = ctk.CTkButton(
            top_bar, 
            text="▶ Start Recognition", 
            font=Theme.get_font_heading(),
            height=38,
            fg_color=Theme.PRIMARY,
            hover_color=Theme.PRIMARY_HOVER,
            command=self._toggle_recognition, 
            width=160
        )
        self.btn_toggle.pack(side="right")
        
        self.camera_widget = CameraWidget(left_frame, self.camera_manager, width=640, height=480)
        self.camera_widget.set_overlay_callback(self._process_frame)
        self.camera_widget.pack(expand=True, fill="both", padx=16, pady=(4, 16))
        
        # Right Panel - Live Log
        right_frame = ctk.CTkFrame(
            self, 
            fg_color=Theme.CARD_BG, 
            corner_radius=16, 
            border_width=1, 
            border_color=Theme.BORDER_COLOR
        )
        right_frame.grid(row=0, column=1, sticky="nsew", padx=(10, 20), pady=20)
        
        header_right = ctk.CTkFrame(right_frame, fg_color="transparent")
        header_right.pack(fill="x", padx=16, pady=(16, 8))
        
        lbl_log = ctk.CTkLabel(
            header_right, 
            text="🕒 Live Detection Stream", 
            font=Theme.get_font_heading()
        )
        lbl_log.pack(side="left")
        
        self.lbl_stream_count = ctk.CTkLabel(
            header_right,
            text="0 Events",
            font=Theme.get_font_mono_small(),
            text_color=Theme.TEXT_MUTED
        )
        self.lbl_stream_count.pack(side="right")
        
        self.scrollable_log = ctk.CTkScrollableFrame(right_frame, fg_color="transparent")
        self.scrollable_log.pack(expand=True, fill="both", padx=12, pady=(0, 14))
        
    def on_show(self):
        self.camera_widget.start()
        self._refresh_log()
        
    def on_hide(self):
        self.camera_widget.stop()
        if self.is_recognizing:
            self._toggle_recognition()

    def _toggle_recognition(self):
        self.is_recognizing = not self.is_recognizing
        if self.is_recognizing:
            self.btn_toggle.configure(text="⏸ Pause Feed", fg_color=Theme.WARNING)
        else:
            self.btn_toggle.configure(text="▶ Start Recognition", fg_color=Theme.PRIMARY)
            self._last_face_ids.clear()

    def _process_frame(self, frame: np.ndarray) -> np.ndarray:
        if not self.is_recognizing:
            return frame
            
        display_frame = frame.copy()
        events = self.ai_engine.process_frame(frame)
        current_face_ids = set()
        
        for event in events:
            x1, y1, x2, y2 = event.bbox
            
            if event.event_type == EventType.SPOOF:
                label = f"SPOOF ATTACK | {(1.0 - event.liveness_score)*100:.0f}% FAKE"
                self._draw_overlay(display_frame, x1, y1, x2, y2, label, 0.0, (244, 63, 94))
                # Log spoof to firestore
                self.attendance_engine.process_event(event)
                continue
                
            if event.event_type == EventType.UNKNOWN:
                self._draw_overlay(display_frame, x1, y1, x2, y2, "UNKNOWN SUBJECT", event.recognition_confidence, (245, 158, 11))
                # Log unknown to firestore
                self.attendance_engine.process_event(event)
                continue
                
            if event.event_type == EventType.RECOGNIZED:
                student_id = event.student_id
                if student_id is not None:
                    current_face_ids.add(student_id)
                    
                    status, progress = self.attendance_engine.process_event(event)
                    
                    label = f"{event.student_name} ({event.student_roll}) | Match: {event.recognition_confidence*100:.0f}% | Live: {event.liveness_score*100:.0f}%"
                    if status == AttendanceStatus.NEWLY_MARKED:
                        self._draw_overlay(display_frame, x1, y1, x2, y2, f"✔ MARKED: {label}", 0.0, (16, 185, 129))
                        self.after(0, self._refresh_log)
                    elif status == AttendanceStatus.ALREADY_MARKED:
                        self._draw_overlay(display_frame, x1, y1, x2, y2, label, 0.0, (16, 185, 129))
                    else: # STABILIZING
                        pct = int(progress * 100)
                        self._draw_overlay(display_frame, x1, y1, x2, y2, f"Verifying... {pct}% | {label}", 0.0, (245, 158, 11))
                    
        # Reset lost stability timers
        lost_faces = self._last_face_ids - current_face_ids
        for fid in lost_faces:
            self.attendance_engine.on_face_lost(fid)
        self._last_face_ids = current_face_ids
        
        return display_frame

    def _draw_overlay(self, frame: np.ndarray, x1: int, y1: int, x2: int, y2: int, text: str, conf: float, color: tuple):
        cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)
        length = 14
        cv2.line(frame, (x1, y1), (x1 + length, y1), color, 3)
        cv2.line(frame, (x1, y1), (x1, y1 + length), color, 3)
        cv2.line(frame, (x2, y1), (x2 - length, y1), color, 3)
        cv2.line(frame, (x2, y1), (x2, y1 + length), color, 3)
        cv2.line(frame, (x1, y2), (x1 + length, y2), color, 3)
        cv2.line(frame, (x1, y2), (x1, y2 - length), color, 3)
        cv2.line(frame, (x2, y2), (x2 - length, y2), color, 3)
        cv2.line(frame, (x2, y2), (x2, y2 - length), color, 3)
        
        conf_str = f" [{conf*100:.0f}%]" if conf > 0 else ""
        full_text = f"{text}{conf_str}"
        cv2.putText(frame, full_text, (x1, max(y1 - 10, 20)), cv2.FONT_HERSHEY_SIMPLEX, 0.65, color, 2)

    def _refresh_log(self):
        records = self.db_manager.get_today_attendance()
        self.lbl_stream_count.configure(text=f"{len(records)} Events")
        
        for widget in self.scrollable_log.winfo_children():
            widget.destroy()
            
        for rec in reversed(records):
            try:
                time_str = rec.marked_at.split(" ")[-1][:5]
            except Exception:
                time_str = "Now"
            card = ctk.CTkFrame(self.scrollable_log, fg_color=Theme.SURFACE, corner_radius=10, border_width=1, border_color=Theme.BORDER_COLOR)
            card.pack(fill="x", pady=4, padx=2)
            
            top_row = ctk.CTkFrame(card, fg_color="transparent")
            top_row.pack(fill="x", padx=10, pady=(8, 2))
            
            ctk.CTkLabel(top_row, text=rec.name, font=Theme.get_font_subheading(), text_color=Theme.TEXT_MAIN).pack(side="left")
            ctk.CTkLabel(top_row, text=f"✔ {time_str}", font=Theme.get_font_mono_small(), text_color=Theme.SUCCESS).pack(side="right")
            
            bot_row = ctk.CTkFrame(card, fg_color="transparent")
            bot_row.pack(fill="x", padx=10, pady=(0, 8))
            
            ctk.CTkLabel(bot_row, text=rec.roll_number, font=Theme.get_font_mono_small(), text_color=Theme.PRIMARY).pack(side="left")
            ctk.CTkLabel(bot_row, text="99.0% Match", font=Theme.get_font_mono_small(), text_color=Theme.TEXT_MUTED).pack(side="right")
