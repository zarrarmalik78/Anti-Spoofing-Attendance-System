import customtkinter as ctk
import time
from src.gui.theme import Theme

class StatusBar(ctk.CTkFrame):
    """
    Bottom status bar showing system health and metrics.
    """
    def __init__(self, master, camera_manager, embedding_matcher, db_manager, **kwargs):
        super().__init__(master, height=30, fg_color=Theme.SURFACE, corner_radius=0, 
                         border_width=1, border_color=Theme.BORDER_COLOR, **kwargs)
        
        self.camera_manager = camera_manager
        self.embedding_matcher = embedding_matcher
        self.db_manager = db_manager
        
        self.grid_columnconfigure((0, 1, 2, 3, 4), weight=1)
        
        font = Theme.get_font_mono()
        
        self.lbl_camera = ctk.CTkLabel(self, text="Camera Status: ⚪ Disconnected", font=font)
        self.lbl_camera.grid(row=0, column=0, padx=10, pady=2, sticky="w")
        
        self.lbl_model = ctk.CTkLabel(self, text="Models Status: 🟢 SCRFD/ArcFace Loaded (Ver: 2.1)", font=font)
        self.lbl_model.grid(row=0, column=1, padx=10, pady=2)
        
        self.lbl_db = ctk.CTkLabel(self, text="Database Status: ⚪ Checking...", font=font)
        self.lbl_db.grid(row=0, column=2, padx=10, pady=2)
        
        self.lbl_students = ctk.CTkLabel(self, text="Registered Students: 0 Total", font=font)
        self.lbl_students.grid(row=0, column=3, padx=10, pady=2)
        
        self.lbl_fps = ctk.CTkLabel(self, text="Stable FPS: 0.0", font=font)
        self.lbl_fps.grid(row=0, column=4, padx=10, pady=2, sticky="e")
        
        self._update_loop()

    def _update_loop(self):
        # Update camera and FPS
        if self.camera_manager and self.camera_manager.is_connected():
            idx_str = str(self.camera_manager.index)
            if len(idx_str) > 10:
                idx_str = "IP Camera"
            else:
                idx_str = f"Index {idx_str}"
            self.lbl_camera.configure(text=f"Camera Status: 🟢 Connected ({idx_str})", text_color=Theme.TEXT)
            fps = self.camera_manager.get_current_fps()
            self.lbl_fps.configure(text=f"Live FPS: {fps:.1f}", text_color=Theme.SUCCESS if fps > 10 else Theme.WARNING)
        else:
            self.lbl_camera.configure(text="Camera Status: 🔴 Disconnected", text_color=Theme.DANGER)
            self.lbl_fps.configure(text="Live FPS: 0.0", text_color=Theme.TEXT_MUTED)
            
        # Update students
        count = self.embedding_matcher.student_count()
        self.lbl_students.configure(text=f"Registered Students: {count} Total")
        
        # Calculate Database Latency
        try:
            start_time = time.time()
            self.db_manager.student_exists("PING") # quick test query
            end_time = time.time()
            latency = int((end_time - start_time) * 1000)
            self.lbl_db.configure(text=f"Database Status: 🟢 Connected (SQLite, Latency: {latency}ms)", text_color=Theme.TEXT)
        except Exception:
            self.lbl_db.configure(text="Database Status: 🔴 Disconnected", text_color=Theme.DANGER)
            
        # Poll every 2 seconds
        self.after(2000, self._update_loop)
