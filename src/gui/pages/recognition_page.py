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
    def __init__(self, master, app_controller, services: dict, **kwargs):
        super().__init__(master, fg_color="transparent", **kwargs)
        
        self.app_controller = app_controller
        self.camera_manager = services['camera_manager']
        self.ai_engine = services['ai_engine']
        self.attendance_engine = services['attendance_engine']
        self.db_manager = services['db_manager']
        
        self.sim_threshold = self.app_controller.config.get("recognition", {}).get("similarity_threshold", 0.45)
        
        self.is_recognizing = False
        self._last_face_ids = set() # To track when faces are lost
        
        self._build_ui()
        
    def _build_ui(self):
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=2)
        self.grid_columnconfigure(1, weight=1)
        
        # Left Panel - Camera
        left_frame = ctk.CTkFrame(self, fg_color=Theme.SURFACE, corner_radius=10, border_width=1, border_color=Theme.BORDER_COLOR)
        left_frame.grid(row=0, column=0, sticky="nsew", padx=(20, 10), pady=20)
        
        top_bar = ctk.CTkFrame(left_frame, fg_color="transparent")
        top_bar.pack(fill="x", padx=15, pady=15)
        
        lbl_title = ctk.CTkLabel(top_bar, text="Live Recognition", font=Theme.get_font_heading())
        lbl_title.pack(side="left")
        
        self.btn_toggle = ctk.CTkButton(top_bar, text="Start Recognition", command=self._toggle_recognition, width=150)
        self.btn_toggle.pack(side="right")
        
        self.camera_widget = CameraWidget(left_frame, self.camera_manager, width=800, height=600)
        self.camera_widget.set_overlay_callback(self._process_frame)
        self.camera_widget.pack(expand=True, fill="both", padx=15, pady=(0, 15))
        
        # Right Panel - Live Log
        right_frame = ctk.CTkFrame(self, fg_color=Theme.SURFACE, corner_radius=10, border_width=1, border_color=Theme.BORDER_COLOR)
        right_frame.grid(row=0, column=1, sticky="nsew", padx=(10, 20), pady=20)
        
        lbl_log = ctk.CTkLabel(right_frame, text="Recognized Today", font=Theme.get_font_heading())
        lbl_log.pack(pady=15, padx=15, anchor="w")
        
        self.scrollable_log = ctk.CTkScrollableFrame(right_frame, fg_color="transparent")
        self.scrollable_log.pack(expand=True, fill="both", padx=5, pady=5)
        
    def on_show(self):
        self.camera_widget.start()
        self._refresh_log()
        
    def on_hide(self):
        self.camera_widget.stop()
        if self.is_recognizing:
            self._toggle_recognition() # Turn off when navigating away

    def _toggle_recognition(self):
        self.is_recognizing = not self.is_recognizing
        if self.is_recognizing:
            self.btn_toggle.configure(text="Stop", fg_color=Theme.DANGER, hover_color="#c0392b")
        else:
            self.btn_toggle.configure(text="Start Recognition", fg_color=Theme.PRIMARY, hover_color=Theme.PRIMARY_HOVER)
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
                # Mock a face object for _draw_spoof which expects an object with liveness_score
                from collections import namedtuple
                FaceMock = namedtuple('FaceMock', ['liveness_score'])
                face = FaceMock(event.liveness_score)
                self._draw_spoof(display_frame, x1, y1, x2, y2, face)
                continue
                
            if event.event_type == EventType.UNKNOWN:
                self._draw_unknown(display_frame, x1, y1, x2, y2)
                self.attendance_engine.process_event(event)
                continue
                
            if event.event_type == EventType.RECOGNIZED:
                current_face_ids.add(event.student_id)
                # Recognized
                status, progress = self.attendance_engine.process_event(event)
                
                # Mock a student object for _draw_recognized
                from collections import namedtuple
                StudentMock = namedtuple('StudentMock', ['id', 'name', 'roll_number'])
                student = StudentMock(event.student_id, event.student_name, event.student_roll)
                
                self._draw_recognized(display_frame, x1, y1, x2, y2, student, event.recognition_confidence, status, progress)
                
                if status == AttendanceStatus.NEWLY_MARKED:
                    self.after(0, self._refresh_log)
                    
        # Check for lost faces to reset timers
        lost_faces = self._last_face_ids - current_face_ids
        for face_id in lost_faces:
            self.attendance_engine.on_face_lost(face_id)
            
        self._last_face_ids = current_face_ids
        
        return display_frame
        
    def _draw_spoof(self, frame, x1, y1, x2, y2, face):
        color = (0, 0, 255) # Red
        cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)
        
        fake_prob = (1.0 - getattr(face, 'liveness_score', 0.0)) * 100
        label = f"Spoof Detected | FAKE: {fake_prob:.1f}%"
        
        font = cv2.FONT_HERSHEY_SIMPLEX
        font_scale = 0.55
        thickness = 1
        (w, h), _ = cv2.getTextSize(label, font, font_scale, thickness)
        
        box_y2 = y1 - 4
        box_y1 = box_y2 - h - 12
        text_y = y1 - 8
        if box_y1 < 0:
            box_y1 = y2 + 4
            box_y2 = box_y1 + h + 12
            text_y = box_y1 + h + 6
            
        cv2.rectangle(frame, (x1, box_y1), (x1 + w + 16, box_y2), (20, 20, 20), -1)
        cv2.rectangle(frame, (x1, box_y1), (x1 + 5, box_y2), color, -1)
        cv2.putText(frame, label, (x1 + 10, text_y), font, font_scale, (255, 255, 255), thickness, cv2.LINE_AA)

    def _draw_unknown(self, frame, x1, y1, x2, y2):
        color = (0, 0, 255) # Red (BGR)
        cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)
        
        label = "Unknown"
        font = cv2.FONT_HERSHEY_SIMPLEX
        font_scale = 0.55
        thickness = 1
        (w, h), _ = cv2.getTextSize(label, font, font_scale, thickness)
        
        box_y2 = y1 - 4
        box_y1 = box_y2 - h - 12
        text_y = y1 - 8
        if box_y1 < 0:
            box_y1 = y2 + 4
            box_y2 = box_y1 + h + 12
            text_y = box_y1 + h + 6
            
        cv2.rectangle(frame, (x1, box_y1), (x1 + w + 16, box_y2), (20, 20, 20), -1)
        cv2.rectangle(frame, (x1, box_y1), (x1 + 5, box_y2), color, -1)
        cv2.putText(frame, label, (x1 + 10, text_y), font, font_scale, (255, 255, 255), thickness, cv2.LINE_AA)

    def _draw_recognized(self, frame, x1, y1, x2, y2, student, score, status, progress):
        if status == AttendanceStatus.ALREADY_MARKED:
            color = (0, 200, 0)
        elif status == AttendanceStatus.NEWLY_MARKED:
            color = (0, 255, 0)
        else: # STABILIZING
            color = (0, 255, 255)
            
        cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)
        
        if status == AttendanceStatus.STABILIZING:
            center = (int((x1+x2)/2), int((y1+y2)/2))
            radius = int(max(x2-x1, y2-y1) * 0.4)
            end_angle = int(360 * progress)
            if end_angle > 0:
                cv2.ellipse(frame, center, (radius, radius), 270, 0, end_angle, color, 4)
                
        label = f"ID: {student.roll_number} | {student.name} | Conf: {score*100:.1f}%"
        if status == AttendanceStatus.ALREADY_MARKED:
            label += " [Marked ✓]"
            
        font = cv2.FONT_HERSHEY_SIMPLEX
        font_scale = 0.55
        thickness = 1
        (w, h), _ = cv2.getTextSize(label, font, font_scale, thickness)
        
        box_y2 = y1 - 4
        box_y1 = box_y2 - h - 12
        text_y = y1 - 8
        if box_y1 < 0:
            box_y1 = y2 + 4
            box_y2 = box_y1 + h + 12
            text_y = box_y1 + h + 6

        cv2.rectangle(frame, (x1, box_y1), (x1 + w + 16, box_y2), (20, 20, 20), -1)
        cv2.rectangle(frame, (x1, box_y1), (x1 + 5, box_y2), color, -1)
        cv2.putText(frame, label, (x1 + 10, text_y), font, font_scale, (255, 255, 255), thickness, cv2.LINE_AA)

    def _refresh_log(self):
        for widget in self.scrollable_log.winfo_children():
            widget.destroy()
            
        records = self.db_manager.get_session_attendance(self.attendance_engine.session_id)
        
        if not records:
            lbl = ctk.CTkLabel(self.scrollable_log, text="No attendees yet.", text_color=Theme.TEXT_MUTED)
            lbl.pack(pady=20)
            return
            
        for rec in records:
            frame = ctk.CTkFrame(self.scrollable_log, fg_color=("gray90", "gray15"), corner_radius=5)
            frame.pack(fill="x", pady=2, padx=5)
            
            # Left side
            left = ctk.CTkFrame(frame, fg_color="transparent")
            left.pack(side="left", padx=10, pady=5)
            
            lbl_name = ctk.CTkLabel(left, text=rec.name, font=Theme.get_font_heading())
            lbl_name.pack(anchor="w")
            lbl_roll = ctk.CTkLabel(left, text=rec.roll_number, font=Theme.get_font_body(), text_color=Theme.TEXT_MUTED)
            lbl_roll.pack(anchor="w")
            
            # Right side (time)
            time_obj = datetime.datetime.strptime(rec.marked_at, "%Y-%m-%d %H:%M:%S")
            time_str = time_obj.strftime("%I:%M:%S %p")
            
            lbl_time = ctk.CTkLabel(frame, text=time_str, font=Theme.get_font_mono(), text_color=Theme.SUCCESS)
            lbl_time.pack(side="right", padx=10)
