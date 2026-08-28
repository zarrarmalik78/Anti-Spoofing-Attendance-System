import customtkinter as ctk
import time
import numpy as np
import cv2
from tkinter import messagebox
import tkinter.filedialog as filedialog
from PIL import Image, ImageTk
import threading

from src.gui.theme import Theme
from src.gui.widgets.camera_widget import CameraWidget
from src.core.student_registrar import POSE_INSTRUCTIONS

class RegisterPage(ctk.CTkFrame):
    """
    Modern Student Biometric Enrollment Page with 'Capture First, Details Later' workflow.
    """
    def __init__(self, master, app_controller, services: dict, **kwargs):
        super().__init__(master, fg_color="transparent", **kwargs)
        
        self.app_controller = app_controller
        self.camera_manager = services['camera_manager']
        self.student_registrar = services['student_registrar']
        self.face_engine = services['face_engine']
        
        self.num_samples = 5 # 5 clean samples
        self.capturing = False
        self.captured_crops = [] # list of numpy crop images
        self.captured_embeddings = []
        self.last_capture_time = 0
        
        self._build_ui()
        
    def _build_ui(self):
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=3) # Camera / Capture Viewport
        self.grid_columnconfigure(1, weight=2) # Details Form & Gallery
        
        # ==========================================
        # LEFT PANEL: Camera Viewport & Capture
        # ==========================================
        left_container = ctk.CTkFrame(
            self, 
            fg_color=Theme.CARD_BG, 
            corner_radius=16, 
            border_width=1, 
            border_color=Theme.BORDER_COLOR
        )
        left_container.grid(row=0, column=0, sticky="nsew", padx=(20, 10), pady=20)
        
        # Header with Instruction Badge
        header_frame = ctk.CTkFrame(left_container, fg_color="transparent")
        header_frame.pack(fill="x", padx=18, pady=(14, 6))
        
        lbl_title = ctk.CTkLabel(
            header_frame, 
            text="👤 Biometric Facial Enrollment", 
            font=Theme.get_font_heading()
        )
        lbl_title.pack(side="left")
        
        self.badge_mode = ctk.CTkLabel(
            header_frame,
            text="⚡ STEP 1: CAPTURE FACE",
            font=Theme.get_font_mono_small(),
            text_color=Theme.PRIMARY
        )
        self.badge_mode.pack(side="right")
        
        # Camera Feed with fixed aspect height to fit control buttons cleanly
        self.camera_widget = CameraWidget(left_container, self.camera_manager, width=480, height=320)
        self.camera_widget.set_overlay_callback(self._process_frame_overlay)
        self.camera_widget.pack(expand=False, fill="x", padx=16, pady=4)
        
        # Capture Progress Bar & Pose Guide
        guide_frame = ctk.CTkFrame(left_container, fg_color=Theme.SURFACE, corner_radius=12, border_width=1, border_color=Theme.BORDER_COLOR)
        guide_frame.pack(fill="x", padx=16, pady=6)
        
        self.lbl_instruction = ctk.CTkLabel(
            guide_frame, 
            text="Align face in center frame and click 'Start Face Capture'", 
            font=Theme.get_font_subheading(),
            text_color=Theme.TEXT_MAIN
        )
        self.lbl_instruction.pack(padx=12, pady=(8, 2), anchor="w")
        
        prog_row = ctk.CTkFrame(guide_frame, fg_color="transparent")
        prog_row.pack(fill="x", padx=12, pady=(2, 8))
        
        self.lbl_progress_count = ctk.CTkLabel(
            prog_row, 
            text="0 / 5 Samples Captured", 
            font=Theme.get_font_mono_small(),
            text_color=Theme.TEXT_MUTED
        )
        self.lbl_progress_count.pack(side="left")
        
        self.progress_bar = ctk.CTkProgressBar(prog_row, height=10, corner_radius=5)
        self.progress_bar.pack(side="right", fill="x", expand=True, padx=(12, 0))
        self.progress_bar.set(0)
        
        # Bottom Control Buttons (Prominently visible)
        btn_row = ctk.CTkFrame(left_container, fg_color="transparent")
        btn_row.pack(fill="x", padx=16, pady=(6, 16))
        
        self.btn_capture = ctk.CTkButton(
            btn_row, 
            text="📸 Start Face Capture", 
            font=Theme.get_font_heading(),
            height=46, 
            fg_color=Theme.PRIMARY,
            hover_color=Theme.PRIMARY_HOVER,
            command=self._toggle_capture
        )
        self.btn_capture.pack(side="left", fill="x", expand=True, padx=(0, 6))
        
        self.btn_reset_cam = ctk.CTkButton(
            btn_row, 
            text="🔄 Retake Photos", 
            font=Theme.get_font_body(),
            height=46, 
            fg_color=Theme.SURFACE_HOVER,
            hover_color=Theme.BORDER_COLOR,
            text_color=Theme.TEXT_MAIN,
            command=self._reset_capture
        )
        self.btn_reset_cam.pack(side="right", padx=(6, 0))

        # ==========================================
        # RIGHT PANEL: Captured Gallery & Student Details
        # ==========================================
        right_container = ctk.CTkScrollableFrame(
            self, 
            fg_color=Theme.CARD_BG, 
            corner_radius=16, 
            border_width=1, 
            border_color=Theme.BORDER_COLOR
        )
        right_container.grid(row=0, column=1, sticky="nsew", padx=(10, 20), pady=20)
        
        # Step 2 Header
        lbl_s2 = ctk.CTkLabel(
            right_container, 
            text="📝 STEP 2: STUDENT DETAILS & LINKAGE", 
            font=Theme.get_font_mono_small(), 
            text_color=Theme.TEXT_MUTED
        )
        lbl_s2.pack(padx=14, pady=(12, 4), anchor="w")
        
        # Select Existing University Student Card
        lookup_card = ctk.CTkFrame(right_container, fg_color=Theme.SURFACE, corner_radius=12, border_width=1, border_color=Theme.BORDER_COLOR)
        lookup_card.pack(fill="x", padx=12, pady=(0, 10))
        
        lbl_lookup = ctk.CTkLabel(lookup_card, text="🔍 Select Existing University Student", font=Theme.get_font_subheading(), text_color=Theme.PRIMARY)
        lbl_lookup.pack(padx=14, pady=(10, 2), anchor="w")
        
        lookup_row = ctk.CTkFrame(lookup_card, fg_color="transparent")
        lookup_row.pack(fill="x", padx=14, pady=(0, 10))
        
        self.combo_lookup = ctk.CTkComboBox(
            lookup_row,
            values=["-- Select Pre-Registered Student --"],
            height=36,
            font=Theme.get_font_body(),
            command=self._on_select_existing_student
        )
        self.combo_lookup.pack(side="left", fill="x", expand=True, padx=(0, 6))
        
        self.btn_refresh_students = ctk.CTkButton(
            lookup_row,
            text="🔄 Load",
            width=70,
            height=36,
            fg_color=Theme.PRIMARY,
            command=self._load_unregistered_students
        )
        self.btn_refresh_students.pack(side="right")
        
        # Captured Gallery Row
        self.gallery_frame = ctk.CTkFrame(right_container, fg_color=Theme.SURFACE, corner_radius=12, border_width=1, border_color=Theme.BORDER_COLOR)
        self.gallery_frame.pack(fill="x", padx=12, pady=(0, 14))
        
        lbl_g_title = ctk.CTkLabel(self.gallery_frame, text="Captured Face Samples:", font=Theme.get_font_small(), text_color=Theme.TEXT_MUTED)
        lbl_g_title.pack(padx=10, pady=(8, 4), anchor="w")
        
        self.gallery_thumbnails_row = ctk.CTkFrame(self.gallery_frame, fg_color="transparent")
        self.gallery_thumbnails_row.pack(padx=10, pady=(0, 10), fill="x")
        
        self.thumbnail_labels = []
        for i in range(self.num_samples):
            lbl_slot = ctk.CTkLabel(
                self.gallery_thumbnails_row,
                text=f"Sample {i+1}",
                width=54,
                height=54,
                fg_color=Theme.SURFACE_HOVER,
                corner_radius=8,
                font=Theme.get_font_mono_small(),
                text_color=Theme.TEXT_MUTED
            )
            lbl_slot.pack(side="left", padx=4)
            self.thumbnail_labels.append(lbl_slot)
            
        # Form Fields
        form_card = ctk.CTkFrame(right_container, fg_color=Theme.SURFACE, corner_radius=12, border_width=1, border_color=Theme.BORDER_COLOR)
        form_card.pack(fill="x", padx=12, pady=(0, 14))
        
        lbl_name = ctk.CTkLabel(form_card, text="Full Name", font=Theme.get_font_subheading())
        lbl_name.pack(padx=14, pady=(12, 2), anchor="w")
        self.entry_name = ctk.CTkEntry(form_card, placeholder_text="e.g. Darrell Steward", font=Theme.get_font_body(), height=38)
        self.entry_name.pack(fill="x", padx=14, pady=(0, 10))
        
        lbl_roll = ctk.CTkLabel(form_card, text="Roll Number", font=Theme.get_font_subheading())
        lbl_roll.pack(padx=14, pady=(0, 2), anchor="w")
        self.entry_roll = ctk.CTkEntry(form_card, placeholder_text="e.g. FA23-BCS-001", font=Theme.get_font_mono(), height=38)
        self.entry_roll.pack(fill="x", padx=14, pady=(0, 10))
        
        lbl_dept = ctk.CTkLabel(form_card, text="Department", font=Theme.get_font_subheading())
        lbl_dept.pack(padx=14, pady=(0, 2), anchor="w")
        self.dept_combo = ctk.CTkComboBox(
            form_card, 
            values=["Department of Computer Science", "Department of Software Engineering", "Department of AI & Data Science", "Department of Cyber Security", "Department of Electrical Engineering", "Department of Management Sciences"],
            height=38,
            font=Theme.get_font_body()
        )
        self.dept_combo.pack(fill="x", padx=14, pady=(0, 10))
        
        row_sem = ctk.CTkFrame(form_card, fg_color="transparent")
        row_sem.pack(fill="x", padx=14, pady=(0, 14))
        
        col_s1 = ctk.CTkFrame(row_sem, fg_color="transparent")
        col_s1.pack(side="left", fill="x", expand=True, padx=(0, 4))
        lbl_sem = ctk.CTkLabel(col_s1, text="Semester", font=Theme.get_font_subheading())
        lbl_sem.pack(anchor="w")
        self.combo_sem = ctk.CTkComboBox(col_s1, values=["1", "2", "3", "4", "5", "6", "7", "8"], height=36)
        self.combo_sem.set("6")
        self.combo_sem.pack(fill="x")
        
        col_s2 = ctk.CTkFrame(row_sem, fg_color="transparent")
        col_s2.pack(side="right", fill="x", expand=True, padx=(4, 0))
        lbl_sec = ctk.CTkLabel(col_s2, text="Section", font=Theme.get_font_subheading())
        lbl_sec.pack(anchor="w")
        self.combo_sec = ctk.CTkComboBox(col_s2, values=["A", "B", "C"], height=36)
        self.combo_sec.set("A")
        self.combo_sec.pack(fill="x")

        # Save Button
        self.btn_save = ctk.CTkButton(
            right_container,
            text="💾 Complete & Save Registration",
            font=Theme.get_font_heading(),
            height=46,
            fg_color=Theme.SUCCESS,
            hover_color=Theme.SUCCESS_HOVER,
            command=self._save_student
        )
        self.btn_save.pack(fill="x", padx=12, pady=(0, 10))

    def on_show(self):
        self.camera_widget.start()
        self._load_unregistered_students()

    def _load_unregistered_students(self):
        def _worker():
            try:
                if not hasattr(self.student_registrar, 'firebase_service') or not self.student_registrar.firebase_service:
                    return
                docs = self.student_registrar.firebase_service.list_documents('students', page_size=200)
                options = ["-- Select Pre-Registered Student --"]
                self._firestore_students_map = {}
                for doc in docs:
                    s_id = doc.get('studentId') or doc.get('rollNumber') or doc.get('_id')
                    s_name = doc.get('name') or 'Student'
                    status = doc.get('faceEnrollmentStatus', 'NOT_ENROLLED')
                    tag = "✔ Enrolled" if status == "ENROLLED" else "🟡 Pending"
                    opt_text = f"{s_name} ({s_id}) [{tag}]"
                    options.append(opt_text)
                    self._firestore_students_map[opt_text] = doc
                
                self.after(0, lambda: self.combo_lookup.configure(values=options))
            except Exception as e:
                print("Failed to load student list:", e)
        threading.Thread(target=_worker, daemon=True).start()

    def _on_select_existing_student(self, choice):
        if not hasattr(self, '_firestore_students_map') or choice not in self._firestore_students_map:
            return
        doc = self._firestore_students_map[choice]
        self.entry_name.delete(0, 'end')
        self.entry_name.insert(0, doc.get('name', ''))
        
        roll = doc.get('rollNumber') or doc.get('studentId') or ''
        self.entry_roll.delete(0, 'end')
        self.entry_roll.insert(0, roll)
        
        dept = doc.get('departmentId') or doc.get('department', '')
        if "Computer Science" in dept or "dept-cs" in dept:
            self.dept_combo.set("Department of Computer Science")
        elif "Software" in dept or "dept-se" in dept:
            self.dept_combo.set("Department of Software Engineering")
        elif "AI" in dept or "dept-ai" in dept:
            self.dept_combo.set("Department of AI & Data Science")
        
    def on_hide(self):
        self.camera_widget.stop()
        self._reset_capture()

    def _toggle_capture(self):
        if not self.capturing:
            self.capturing = True
            self.btn_capture.configure(text="⏸ Capturing...", fg_color=Theme.WARNING)
            self.lbl_instruction.configure(text="Look directly at the camera (Capturing samples...)")
        else:
            self.capturing = False
            self.btn_capture.configure(text="📸 Resume Capture", fg_color=Theme.PRIMARY)

    def _reset_capture(self):
        self.capturing = False
        self.captured_crops = []
        self.captured_embeddings = []
        self.progress_bar.set(0)
        self.lbl_progress_count.configure(text=f"0 / {self.num_samples} Samples Captured")
        self.lbl_instruction.configure(text="Align face in center frame and click 'Start Face Capture'")
        self.btn_capture.configure(text="📸 Start Face Capture", fg_color=Theme.PRIMARY, state="normal")
        self.badge_mode.configure(text="⚡ STEP 1: CAPTURE FACE", text_color=Theme.PRIMARY)
        
        for lbl in self.thumbnail_labels:
            lbl.configure(image="", text="Sample")

    def _process_frame_overlay(self, frame: np.ndarray) -> np.ndarray:
        display_frame = frame.copy()
        
        # Only run face detection models while user is actively capturing!
        if not self.capturing:
            return display_frame
            
        # Detect and embed face
        faces = self.face_engine.detect_and_embed(frame)
        if faces:
            face = max(faces, key=lambda f: (f.bbox[2]-f.bbox[0]) * (f.bbox[3]-f.bbox[1]))
            x1, y1, x2, y2 = face.bbox.astype(int)
            
            # Corner targeting HUD
            color = (99, 102, 241) # Brand Indigo
            cv2.rectangle(display_frame, (x1, y1), (x2, y2), color, 2)
            
            # Auto-capture logic
            now = time.time()
            if self.capturing and len(self.captured_crops) < self.num_samples and (now - self.last_capture_time > 0.6):
                self.last_capture_time = now
                h, w = frame.shape[:2]
                crop = frame[max(0, y1):min(h, y2), max(0, x1):min(w, x2)]
                
                # Embedding is pre-computed in face.embedding
                feat = face.embedding
                if feat is not None and crop.size > 0:
                    self.captured_crops.append(crop)
                    self.captured_embeddings.append(feat)
                    self._update_gallery_ui()
                elif feat is None and crop.size > 0:
                    # Face is not live or liveness check failed
                    self.lbl_instruction.configure(
                        text="⚠️ Liveness check failed! Ensure real subject face.",
                        text_color=Theme.DANGER
                    )
                    
        return display_frame

    def _update_gallery_ui(self):
        count = len(self.captured_crops)
        self.progress_bar.set(count / self.num_samples)
        self.lbl_progress_count.configure(text=f"{count} / {self.num_samples} Samples Captured")
        
        # Update thumbnail
        if count <= len(self.thumbnail_labels):
            idx = count - 1
            crop = self.captured_crops[idx]
            crop_resized = cv2.resize(crop, (50, 50))
            crop_rgb = cv2.cvtColor(crop_resized, cv2.COLOR_BGR2RGB)
            img_pil = Image.fromarray(crop_rgb)
            img_tk = ctk.CTkImage(light_image=img_pil, dark_image=img_pil, size=(50, 50))
            self.thumbnail_labels[idx].configure(image=img_tk, text="")
            
        if count >= self.num_samples:
            self.capturing = False
            self.btn_capture.configure(text="✅ Photos Ready", fg_color=Theme.SUCCESS, state="disabled")
            self.badge_mode.configure(text="⚡ STEP 2: FILL DETAILS & SAVE", text_color=Theme.SUCCESS)
            self.lbl_instruction.configure(text="Photos captured successfully! Now fill in the student details on the right.")

    def _save_student(self):
        name = self.entry_name.get().strip()
        roll = self.entry_roll.get().strip().upper()
        dept = self.dept_combo.get().strip()
        
        if not name or not roll or not dept:
            messagebox.showerror("Missing Information", "Please enter Student Name and Roll Number.")
            return
            
        if len(self.captured_embeddings) == 0:
            messagebox.showerror("No Photos Captured", "Please click 'Start Face Capture' to take student face samples first.")
            return
            
        # Average embeddings to get high-fidelity 512D template
        avg_embedding = np.mean(self.captured_embeddings, axis=0)
        norm = np.linalg.norm(avg_embedding)
        if norm > 0:
            avg_embedding = avg_embedding / norm
            
        # Save or update SQLite and Cloud Firestore via StudentRegistrar
        try:
            success = self.student_registrar.register_student(name, roll, dept, self.captured_embeddings)
            if success:
                messagebox.showinfo(
                    "Enrollment Successful", 
                    f"Student {name} ({roll}) has been registered!\n\n• Biometric Embedding: 512D ArcFace Vector Saved\n• Firestore Status: ENROLLED\n• Synced with Edge Engine"
                )
                self._reset_capture()
                self.entry_name.delete(0, 'end')
                self.entry_roll.delete(0, 'end')
        except Exception as e:
            messagebox.showerror("Registration Error", f"Could not register student {roll}: {e}")
