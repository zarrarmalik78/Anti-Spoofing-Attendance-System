import customtkinter as ctk
import time
import numpy as np
import cv2
from tkinter import messagebox
import threading

from src.gui.theme import Theme
from src.gui.widgets.camera_widget import CameraWidget
from src.core.student_registrar import POSE_INSTRUCTIONS

class RegisterPage(ctk.CTkFrame):
    def __init__(self, master, app_controller, services: dict, **kwargs):
        super().__init__(master, fg_color="transparent", **kwargs)
        
        self.app_controller = app_controller
        self.camera_manager = services['camera_manager']
        self.student_registrar = services['student_registrar']
        
        self.num_samples = self.app_controller.config.get("registration", {}).get("num_samples", 10)
        self.sample_delay_ms = self.app_controller.config.get("registration", {}).get("sample_delay_ms", 800)
        
        self.capturing = False
        self.current_sample = 0
        self.embeddings = []
        self.last_capture_time = 0
        
        self._build_ui()
        
    def _build_ui(self):
        # Split into left (Form) and right (Camera)
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=2)
        
        # Left Panel - Form
        form_frame = ctk.CTkFrame(self, fg_color=Theme.SURFACE, corner_radius=10, border_width=1, border_color=Theme.BORDER_COLOR)
        form_frame.grid(row=0, column=0, sticky="nsew", padx=(20, 10), pady=20)
        
        lbl_title = ctk.CTkLabel(form_frame, text="Register New Student", font=Theme.get_font_title())
        lbl_title.pack(pady=(20, 30), padx=20, anchor="w")
        
        self.entry_name = ctk.CTkEntry(form_frame, placeholder_text="Full Name", font=Theme.get_font_body(), height=40)
        self.entry_name.pack(fill="x", padx=20, pady=(0, 15))
        
        self.entry_roll = ctk.CTkEntry(form_frame, placeholder_text="Roll Number (e.g. CS-24-001)", font=Theme.get_font_body(), height=40)
        self.entry_roll.pack(fill="x", padx=20, pady=(0, 15))
        
        self.entry_dept = ctk.CTkEntry(form_frame, placeholder_text="Department", font=Theme.get_font_body(), height=40)
        self.entry_dept.pack(fill="x", padx=20, pady=(0, 30))
        
        self.btn_start = ctk.CTkButton(form_frame, text="Start Capture", font=Theme.get_font_heading(), height=50, command=self._start_capture)
        self.btn_start.pack(fill="x", padx=20, pady=(0, 10))
        
        self.btn_clear = ctk.CTkButton(form_frame, text="Clear Form", fg_color="transparent", border_width=1, text_color=Theme.TEXT_MAIN, command=self._clear_form)
        self.btn_clear.pack(fill="x", padx=20)
        
        # Right Panel - Camera & Progress
        cam_frame = ctk.CTkFrame(self, fg_color=Theme.SURFACE, corner_radius=10, border_width=1, border_color=Theme.BORDER_COLOR)
        cam_frame.grid(row=0, column=1, sticky="nsew", padx=(10, 20), pady=20)
        
        # Instruction header
        self.lbl_instruction_title = ctk.CTkLabel(cam_frame, text="Ready to capture", font=Theme.get_font_heading())
        self.lbl_instruction_title.pack(pady=(15, 0))
        self.lbl_instruction_desc = ctk.CTkLabel(cam_frame, text="Fill the form and click Start Capture.", font=Theme.get_font_body(), text_color=Theme.TEXT_MUTED)
        self.lbl_instruction_desc.pack(pady=(0, 15))
        
        self.camera_widget = CameraWidget(cam_frame, self.camera_manager, width=640, height=480)
        self.camera_widget.set_overlay_callback(self._process_frame_overlay)
        self.camera_widget.pack(expand=True, fill="both", padx=20, pady=5)
        
        # Progress area
        prog_frame = ctk.CTkFrame(cam_frame, fg_color="transparent")
        prog_frame.pack(fill="x", padx=20, pady=15)
        
        self.lbl_progress = ctk.CTkLabel(prog_frame, text=f"0 / {self.num_samples} captured", font=Theme.get_font_body())
        self.lbl_progress.pack(side="left")
        
        self.progress_bar = ctk.CTkProgressBar(prog_frame)
        self.progress_bar.pack(side="right", fill="x", expand=True, padx=(15, 0))
        self.progress_bar.set(0)

    def on_show(self):
        self.camera_widget.start()
        
    def on_hide(self):
        self.camera_widget.stop()
        self._reset_capture_state()

    def _start_capture(self):
        name = self.entry_name.get().strip()
        roll = self.entry_roll.get().strip()
        dept = self.entry_dept.get().strip()
        
        if not name or not roll or not dept:
            messagebox.showerror("Validation Error", "Please fill all fields.")
            return
            
        if self.student_registrar.db_manager.student_exists(roll):
            messagebox.showerror("Error", f"Roll number {roll} is already registered.")
            return

        self._reset_capture_state()
        self.capturing = True
        
        # Disable inputs
        self.entry_name.configure(state="disabled")
        self.entry_roll.configure(state="disabled")
        self.entry_dept.configure(state="disabled")
        self.btn_start.configure(state="disabled")
        
        self._update_instruction_ui()

    def _reset_capture_state(self):
        self.capturing = False
        self.current_sample = 0
        self.embeddings = []
        self.progress_bar.set(0)
        self.lbl_progress.configure(text=f"0 / {self.num_samples} captured")
        self.lbl_instruction_title.configure(text="Ready to capture")
        self.lbl_instruction_desc.configure(text="Fill the form and click Start Capture.")
        
        self.entry_name.configure(state="normal")
        self.entry_roll.configure(state="normal")
        self.entry_dept.configure(state="normal")
        self.btn_start.configure(state="normal")

    def _clear_form(self):
        self._reset_capture_state()
        self.entry_name.delete(0, 'end')
        self.entry_roll.delete(0, 'end')
        self.entry_dept.delete(0, 'end')

    def _update_instruction_ui(self):
        if self.current_sample < self.num_samples:
            idx = min(self.current_sample, len(POSE_INSTRUCTIONS) - 1)
            title, desc = POSE_INSTRUCTIONS[idx]
            self.lbl_instruction_title.configure(text=f"Sample {self.current_sample + 1} / {self.num_samples}: {title}")
            self.lbl_instruction_desc.configure(text=desc)
        else:
            self.lbl_instruction_title.configure(text="Processing...")
            self.lbl_instruction_desc.configure(text="Saving to database")

    def _process_frame_overlay(self, frame: np.ndarray) -> np.ndarray:
        """
        Called by CameraWidget before rendering.
        If capturing is active, we attempt to extract a sample.
        """
        display_frame = frame.copy()
        
        if not self.capturing:
            return display_frame

        current_time = time.time() * 1000
        if current_time - self.last_capture_time < self.sample_delay_ms:
            # Add visual indicator of wait
            cv2.circle(display_frame, (30, 30), 10, (0, 165, 255), -1) # Orange circle
            return display_frame

        # Try to capture
        success, msg, emb = self.student_registrar.capture_sample(frame)
        
        if success and emb is not None:
            self.embeddings.append(emb)
            self.current_sample += 1
            self.last_capture_time = current_time
            
            # Show success flash
            cv2.rectangle(display_frame, (0, 0), (display_frame.shape[1], display_frame.shape[0]), (0, 255, 0), 10)
            
            # Schedule UI updates on main thread
            self.after(0, self._on_sample_captured)
        else:
            # Show warning message on frame
            cv2.putText(display_frame, msg, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
            
        return display_frame

    def _on_sample_captured(self):
        # Update progress
        progress = self.current_sample / self.num_samples
        self.progress_bar.set(progress)
        self.lbl_progress.configure(text=f"{self.current_sample} / {self.num_samples} captured")
        
        if self.current_sample >= self.num_samples:
            self.capturing = False
            self._update_instruction_ui()
            # Run registration in background to not freeze UI
            threading.Thread(target=self._finalize_registration, daemon=True).start()
        else:
            self._update_instruction_ui()

    def _finalize_registration(self):
        try:
            name = self.entry_name.get().strip()
            roll = self.entry_roll.get().strip()
            dept = self.entry_dept.get().strip()
            
            self.student_registrar.register_student(name, roll, dept, self.embeddings)
            
            # Show success on main thread
            self.after(0, lambda: self._registration_success(name))
        except Exception as e:
            # Show error on main thread
            self.after(0, lambda: messagebox.showerror("Registration Failed", str(e)))
            self.after(0, self._reset_capture_state)

    def _registration_success(self, name: str):
        messagebox.showinfo("Success", f"Successfully registered {name}.")
        self._clear_form()
