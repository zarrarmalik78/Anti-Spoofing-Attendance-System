import customtkinter as ctk
import datetime
import cv2
import numpy as np

from src.gui.theme import Theme
from src.gui.widgets.camera_widget import CameraWidget
from src.gui.widgets.analytics_card import AnalyticsCard
from src.core.attendance_engine import AttendanceStatus
from src.core.events import EventType
from src.utils.time_utils import get_current_time

class DashboardPage(ctk.CTkFrame):
    def __init__(self, master, app_controller, services: dict, **kwargs):
        super().__init__(master, fg_color="transparent", **kwargs)
        
        self.app_controller = app_controller
        self.db_manager = services['db_manager']
        self.camera_manager = services['camera_manager']
        self.embedding_matcher = services['embedding_matcher']
        self.ai_engine = services['ai_engine']
        self.attendance_engine = services['attendance_engine']
        
        self.sim_threshold = self.app_controller.config.get("recognition", {}).get("similarity_threshold", 0.45)
        
        self.is_recognizing = False
        self._last_face_ids = set()
        
        self.grid_rowconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=0)
        self.grid_columnconfigure(0, weight=1)
        
        self._build_top_area()
        self._build_bottom_area()
        self._update_loop()
        
    def _build_top_area(self):
        top_frame = ctk.CTkFrame(self, fg_color="transparent")
        top_frame.grid(row=0, column=0, sticky="nsew", padx=20, pady=20)
        
        top_frame.grid_rowconfigure(0, weight=1)
        top_frame.grid_columnconfigure(0, weight=4) # Camera gets more space
        top_frame.grid_columnconfigure(1, weight=5) # Table gets slightly more space for columns
        
        # --- Camera Section ---
        cam_container = ctk.CTkFrame(top_frame, fg_color=Theme.SURFACE, corner_radius=10, border_width=1, border_color=Theme.BORDER_COLOR)
        cam_container.grid(row=0, column=0, sticky="nsew", padx=(0, 10))
        
        lbl_cam_title = ctk.CTkLabel(cam_container, text="Live Camera Feed", font=Theme.get_font_heading())
        lbl_cam_title.pack(pady=10, padx=15, anchor="w")
        
        # Camera Controls (Pack bottom FIRST so expand=True on camera_widget won't hide it)
        controls_frame = ctk.CTkFrame(cam_container, fg_color="transparent")
        controls_frame.pack(side="bottom", fill="x", padx=15, pady=10)
        
        self.btn_toggle_cam = ctk.CTkButton(controls_frame, text="▶ Start Recognition", width=160, command=self._toggle_camera)
        self.btn_toggle_cam.pack(side="left")

        self.camera_widget = CameraWidget(cam_container, self.camera_manager, width=400, height=300)
        self.camera_widget.set_overlay_callback(self._process_frame)
        self.camera_widget.pack(expand=True, fill="both", padx=15, pady=5)
        
        # --- Table Section ---
        list_container = ctk.CTkFrame(top_frame, fg_color=Theme.SURFACE, corner_radius=10, border_width=1, border_color=Theme.BORDER_COLOR)
        list_container.grid(row=0, column=1, sticky="nsew", padx=(10, 0))
        
        header_frame = ctk.CTkFrame(list_container, fg_color="transparent")
        header_frame.pack(fill="x", padx=15, pady=10)
        
        lbl_list_title = ctk.CTkLabel(header_frame, text="Today's Attendance", font=Theme.get_font_heading())
        lbl_list_title.pack(side="left")
        
        self.btn_verify = ctk.CTkButton(header_frame, text="Verify Selected", width=120)
        self.btn_verify.pack(side="right")
        
        # Table Headers
        table_header = ctk.CTkFrame(list_container, fg_color=("gray85", "gray25"), corner_radius=5)
        table_header.pack(fill="x", padx=15, pady=5)
        
        cols = [("Time-In", 1), ("Photo", 1), ("Student ID", 1), ("Name", 2), ("Accuracy", 1), ("Status", 1), ("Actions", 1)]
        for i, (col, w) in enumerate(cols):
            table_header.grid_columnconfigure(i, weight=w)
            lbl = ctk.CTkLabel(table_header, text=col, font=Theme.get_font_body())
            lbl.grid(row=0, column=i, sticky="w", padx=5, pady=5)
            
        self.scrollable_list = ctk.CTkScrollableFrame(list_container, fg_color="transparent")
        self.scrollable_list.pack(expand=True, fill="both", padx=10, pady=5)
        
    def _build_bottom_area(self):
        bottom_frame = ctk.CTkFrame(self, fg_color="transparent")
        bottom_frame.grid(row=1, column=0, sticky="ew", padx=20, pady=(0, 20))
        
        lbl_analytics = ctk.CTkLabel(bottom_frame, text="Analytics", font=Theme.get_font_heading())
        lbl_analytics.pack(anchor="w", pady=(0, 10))
        
        cards_frame = ctk.CTkFrame(bottom_frame, fg_color="transparent")
        cards_frame.pack(fill="x")
        
        cards_frame.grid_columnconfigure((0, 1, 2), weight=1, uniform="card")
        
        self.card_present = AnalyticsCard(cards_frame, title="Present Today", color=Theme.PRIMARY)
        self.card_present.grid(row=0, column=0, sticky="ew", padx=(0, 5))
        
        self.card_registered = AnalyticsCard(cards_frame, title="Registered Students")
        self.card_registered.grid(row=0, column=1, sticky="ew", padx=5)
        
        self.card_unknown = AnalyticsCard(cards_frame, title="Unknown Faces", color=Theme.WARNING)
        self.card_unknown.grid(row=0, column=2, sticky="ew", padx=(5, 0))
        
        # Add Manage button to unknown card
        btn_manage = ctk.CTkButton(self.card_unknown, text="Review & Manage", width=120, fg_color="transparent", border_width=1, border_color=Theme.BORDER_COLOR, text_color=Theme.TEXT)
        btn_manage.pack(pady=(10, 0))

    def _toggle_camera(self):
        self.is_recognizing = not self.is_recognizing
        if self.is_recognizing:
            self.btn_toggle_cam.configure(text="⏸ Pause Recognition", fg_color=Theme.WARNING)
            self._last_face_ids.clear()
        else:
            self.btn_toggle_cam.configure(text="▶ Start Recognition", fg_color=Theme.PRIMARY)

    def on_show(self):
        self.is_recognizing = False
        self.btn_toggle_cam.configure(text="▶ Start Recognition", fg_color=Theme.PRIMARY)
        self.camera_widget.start()
        self._refresh_data()
        
    def on_hide(self):
        self.is_recognizing = False
        self.camera_widget.stop()

    def _process_frame(self, frame: np.ndarray) -> np.ndarray:
        if not self.is_recognizing:
            return frame
            
        display_frame = frame.copy()

        events = self.ai_engine.process_frame(frame)
        current_face_ids = set()
        
        for event in events:
            x1, y1, x2, y2 = event.bbox
            
            if event.event_type == EventType.SPOOF:
                label = f"Spoof Detected | FAKE: {(1.0 - event.liveness_score)*100:.1f}%"
                self._draw_overlay(display_frame, x1, y1, x2, y2, label, 0.0, (0, 0, 255))
                continue
                
            if event.event_type == EventType.UNKNOWN:
                self._draw_overlay(display_frame, x1, y1, x2, y2, "Unknown", event.recognition_confidence, (0, 0, 255))
                self.attendance_engine.process_event(event)
                continue
                
            if event.event_type == EventType.RECOGNIZED:
                current_face_ids.add(event.student_id)
                status, progress = self.attendance_engine.process_event(event)
                
                color = (0, 255, 0) if status in [AttendanceStatus.ALREADY_MARKED, AttendanceStatus.NEWLY_MARKED] else (0, 255, 255)
                label = f"ID: {event.student_roll} | {event.student_name} | Conf: {event.recognition_confidence*100:.1f}%"
                self._draw_overlay(display_frame, x1, y1, x2, y2, label, event.recognition_confidence, color, status, progress)
                
                if status == AttendanceStatus.NEWLY_MARKED:
                    self.after(0, self._refresh_data)
                    
        lost_faces = self._last_face_ids - current_face_ids
        for face_id in lost_faces:
            self.attendance_engine.on_face_lost(face_id)
            
        self._last_face_ids = current_face_ids
        return display_frame

    def _draw_overlay(self, frame, x1, y1, x2, y2, label, score, color, status=None, progress=0):
        # Bounding box around face
        cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)
        
        # Stability Arc
        if status == AttendanceStatus.STABILIZING:
            center = (int((x1+x2)/2), int((y1+y2)/2))
            radius = int(max(x2-x1, y2-y1) * 0.4)
            end_angle = int(360 * progress)
            if end_angle > 0:
                cv2.ellipse(frame, center, (radius, radius), 270, 0, end_angle, color, 4)
                
        # Label styling with dark charcoal box for high contrast readability
        font = cv2.FONT_HERSHEY_SIMPLEX
        font_scale = 0.55
        thickness = 1
        (w, h), _ = cv2.getTextSize(label, font, font_scale, thickness)
        
        # Box bounds above the face box
        box_y2 = y1 - 4
        box_y1 = box_y2 - h - 12
        box_x1 = x1
        box_x2 = x1 + w + 16
        
        if box_y1 < 0:
            box_y1 = y2 + 4
            box_y2 = box_y1 + h + 12
            text_y = box_y1 + h + 6
        else:
            text_y = y1 - 8

        # 1. Dark charcoal solid background box
        cv2.rectangle(frame, (box_x1, box_y1), (box_x2, box_y2), (20, 20, 20), -1)
        # 2. Colored accent bar on the left edge
        cv2.rectangle(frame, (box_x1, box_y1), (box_x1 + 5, box_y2), color, -1)
        # 3. High-contrast anti-aliased white text
        cv2.putText(frame, label, (box_x1 + 10, text_y), font, font_scale, (255, 255, 255), thickness, cv2.LINE_AA)

    def _refresh_data(self):
        # Update Analytics
        self.card_present.set_value(str(self.attendance_engine.get_present_count()))
        self.card_registered.set_value(str(self.embedding_matcher.student_count()))
        self.card_unknown.set_value(str(self.attendance_engine.get_unknown_count()))
        
        # Update Table
        for widget in self.scrollable_list.winfo_children():
            widget.destroy()
            
        records = self.db_manager.get_today_attendance()
        weights = [1, 1, 1, 2, 1, 1, 1]
        
        for r_idx, rec in enumerate(records):
            row_frame = ctk.CTkFrame(self.scrollable_list, fg_color=("gray95", "gray15"), corner_radius=5)
            row_frame.pack(fill="x", pady=2, padx=5)
            
            time_obj = datetime.datetime.strptime(rec.marked_at, "%Y-%m-%d %H:%M:%S")
            time_str = time_obj.strftime("%I:%M %p")
            
            # Data array: Time, Photo (placeholder), ID, Name, Accuracy, Status, Actions
            data = [
                time_str, 
                "👤", 
                rec.roll_number, 
                rec.name, 
                "99.0%", # Mocking accuracy for table since we don't store it yet
                "✅ Verified", 
                "👁️ 🔔"
            ]
            
            for c_idx, (val, w) in enumerate(zip(data, weights)):
                row_frame.grid_columnconfigure(c_idx, weight=w)
                color = Theme.SUCCESS if "Verified" in val else Theme.TEXT
                lbl = ctk.CTkLabel(row_frame, text=val, font=Theme.get_font_body(), text_color=color)
                lbl.grid(row=0, column=c_idx, sticky="w", padx=5, pady=8)

    def _update_loop(self):
        if self.winfo_ismapped():
            self._refresh_data()
        self.after(5000, self._update_loop)
