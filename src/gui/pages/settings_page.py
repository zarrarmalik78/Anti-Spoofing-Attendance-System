import customtkinter as ctk
import tkinter.messagebox as messagebox
import threading
import webbrowser

from src.gui.theme import Theme

class SettingsPage(ctk.CTkFrame):
    """
    Modern Settings & Edge Hardware Configuration Page.
    """
    def __init__(self, master, app_controller, services: dict, **kwargs):
        super().__init__(master, fg_color="transparent", **kwargs)
        
        self.app_controller = app_controller
        self.db_manager = services['db_manager']
        self.embedding_matcher = services['embedding_matcher']
        
        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)
        
        self._build_ui()
        
    def _build_ui(self):
        # Header
        header_frame = ctk.CTkFrame(self, fg_color="transparent")
        header_frame.grid(row=0, column=0, sticky="ew", padx=20, pady=(20, 12))
        
        left_h = ctk.CTkFrame(header_frame, fg_color="transparent")
        left_h.pack(side="left")
        
        lbl_title = ctk.CTkLabel(left_h, text="⚙️ Edge AI Configuration & Registry", font=Theme.get_font_title())
        lbl_title.pack(anchor="w")
        
        lbl_sub = ctk.CTkLabel(left_h, text="Hardware input routing, anti-spoof thresholds, and SQLite local database", font=Theme.get_font_small(), text_color=Theme.TEXT_MUTED)
        lbl_sub.pack(anchor="w")
        
        btn_refresh = ctk.CTkButton(header_frame, text="🔄 Reload Matcher", font=Theme.get_font_heading(), height=38, fg_color=Theme.PRIMARY, hover_color=Theme.PRIMARY_HOVER, command=self._refresh_data)
        btn_refresh.pack(side="right")

        # Top Grid: 2 Configuration Cards
        config_grid = ctk.CTkFrame(self, fg_color="transparent")
        config_grid.grid(row=1, column=0, sticky="nsew", padx=20, pady=(0, 10))
        config_grid.grid_rowconfigure(1, weight=1)
        config_grid.grid_columnconfigure(0, weight=1)
        
        top_cards = ctk.CTkFrame(config_grid, fg_color="transparent")
        top_cards.grid(row=0, column=0, sticky="ew", pady=(0, 12))
        top_cards.grid_columnconfigure((0, 1), weight=1)
        
        # 1. Camera Routing Card
        cam_card = ctk.CTkFrame(top_cards, fg_color=Theme.CARD_BG, corner_radius=16, border_width=1, border_color=Theme.BORDER_COLOR)
        cam_card.grid(row=0, column=0, sticky="nsew", padx=(0, 6))
        
        lbl_c_h = ctk.CTkLabel(cam_card, text="📹 Video Input Source", font=Theme.get_font_heading())
        lbl_c_h.pack(padx=16, pady=(14, 8), anchor="w")
        
        # USB Camera Row
        row1 = ctk.CTkFrame(cam_card, fg_color="transparent")
        row1.pack(fill="x", padx=16, pady=(0, 8))
        
        ctk.CTkLabel(row1, text="USB Webcam:", font=Theme.get_font_subheading()).pack(side="left")
        
        cam_manager = self.app_controller.services['camera_manager']
        current_val = f"Camera {cam_manager.index}" if isinstance(cam_manager.index, int) else "IP Camera (RTSP)"
        self.camera_var = ctk.StringVar(value=current_val)
        self.camera_combo = ctk.CTkComboBox(row1, variable=self.camera_var, command=self._on_camera_change, state="readonly", width=140)
        self.camera_combo.pack(side="left", padx=10)
        
        btn_scan = ctk.CTkButton(row1, text="Scan USB", width=80, fg_color=Theme.SURFACE_HOVER, hover_color=Theme.BORDER_COLOR, text_color=Theme.TEXT_MAIN, command=self._scan_cameras)
        btn_scan.pack(side="left")
        
        # RTSP Camera Row
        row2 = ctk.CTkFrame(cam_card, fg_color="transparent")
        row2.pack(fill="x", padx=16, pady=(0, 14))
        
        default_rtsp = "rtsp://admin:soec@78612@192.168.1.28:554/Streaming/Channels/102"
        self.rtsp_entry = ctk.CTkEntry(row2, placeholder_text="rtsp://user:pass@ip:port/...", font=Theme.get_font_small())
        self.rtsp_entry.insert(0, default_rtsp)
        self.rtsp_entry.pack(side="left", fill="x", expand=True, padx=(0, 8))
        
        btn_rtsp = ctk.CTkButton(row2, text="Connect RTSP", width=100, fg_color=Theme.SUCCESS, hover_color=Theme.SUCCESS_HOVER, command=self._connect_rtsp)
        btn_rtsp.pack(side="right")
        
        # 2. AI Model Thresholds Card
        ai_card = ctk.CTkFrame(top_cards, fg_color=Theme.CARD_BG, corner_radius=16, border_width=1, border_color=Theme.BORDER_COLOR)
        ai_card.grid(row=0, column=1, sticky="nsew", padx=(6, 0))
        
        lbl_a_h = ctk.CTkLabel(ai_card, text="🎯 Biometric Sensitivity & Thresholds", font=Theme.get_font_heading())
        lbl_a_h.pack(padx=16, pady=(14, 8), anchor="w")
        
        # Similarity Threshold
        self.lbl_sim = ctk.CTkLabel(ai_card, text="Face Match Threshold: 0.45 (Cosine Similarity)", font=Theme.get_font_small(), text_color=Theme.TEXT_MUTED)
        self.lbl_sim.pack(padx=16, pady=(0, 2), anchor="w")
        
        self.slider_sim = ctk.CTkSlider(ai_card, from_=0.20, to=0.80, number_of_steps=60, command=self._on_sim_change)
        self.slider_sim.set(0.45)
        self.slider_sim.pack(fill="x", padx=16, pady=(0, 8))
        
        # Anti-Spoofing Threshold
        self.lbl_spoof = ctk.CTkLabel(ai_card, text="Anti-Spoofing Liveness Threshold: 0.40", font=Theme.get_font_small(), text_color=Theme.TEXT_MUTED)
        self.lbl_spoof.pack(padx=16, pady=(0, 2), anchor="w")
        
        self.slider_spoof = ctk.CTkSlider(ai_card, from_=0.10, to=0.90, number_of_steps=80, command=self._on_spoof_change)
        self.slider_spoof.set(0.40)
        self.slider_spoof.pack(fill="x", padx=16, pady=(0, 14))

        # Bottom Registered Students Table
        table_container = ctk.CTkFrame(config_grid, fg_color=Theme.CARD_BG, corner_radius=16, border_width=1, border_color=Theme.BORDER_COLOR)
        table_container.grid(row=1, column=0, sticky="nsew", pady=(0, 10))
        
        table_header = ctk.CTkFrame(table_container, fg_color=Theme.SURFACE_HOVER, corner_radius=8, height=34)
        table_header.pack(fill="x", padx=12, pady=12)
        
        cols = [("ID", 1), ("ROLL NUMBER", 2), ("STUDENT NAME", 3), ("DEPARTMENT", 3), ("REGISTRATION DATE", 2), ("ACTION", 1)]
        self.weights = [1, 2, 3, 3, 2, 1]
        
        for i, ((col, _), w) in enumerate(zip(cols, self.weights)):
            table_header.grid_columnconfigure(i, weight=w)
            lbl = ctk.CTkLabel(table_header, text=col, font=Theme.get_font_mono_small(), text_color=Theme.TEXT_MUTED)
            lbl.grid(row=0, column=i, sticky="w", padx=8, pady=6)
            
        self.scroll_body = ctk.CTkScrollableFrame(table_container, fg_color="transparent")
        self.scroll_body.pack(expand=True, fill="both", padx=10, pady=(0, 10))
        
        self._scan_cameras()

    def on_show(self):
        self._refresh_data()

    def _on_sim_change(self, val):
        v = round(float(val), 2)
        self.lbl_sim.configure(text=f"Face Match Threshold: {v:.2f} (Cosine Similarity)")
        self.app_controller.ai_engine.similarity_threshold = v

    def _on_spoof_change(self, val):
        v = round(float(val), 2)
        self.lbl_spoof.configure(text=f"Anti-Spoofing Liveness Threshold: {v:.2f}")

    def _scan_cameras(self):
        cam_manager = self.app_controller.services['camera_manager']
        self.camera_combo.configure(state="disabled")
        
        def scan():
            available = cam_manager.get_available_cameras()
            def update_ui():
                values = [f"Camera {i}" for i in available]
                if not values:
                    values = ["Camera 0"]
                self.camera_combo.configure(values=values, state="readonly")
                current = f"Camera {cam_manager.index}"
                if current in values:
                    self.camera_var.set(current)
                else:
                    self.camera_var.set(values[0])
            self.after(0, update_ui)
            
        threading.Thread(target=scan, daemon=True).start()

    def _on_camera_change(self, choice: str):
        try:
            idx = int(choice.split(" ")[-1])
            cam_manager = self.app_controller.services['camera_manager']
            success = cam_manager.set_camera_index(idx)
            if not success:
                messagebox.showerror("Error", f"Failed to connect to Camera {idx}")
        except Exception as e:
            messagebox.showerror("Error", f"Could not switch camera: {e}")

    def _connect_rtsp(self):
        url = self.rtsp_entry.get().strip()
        if not url:
            messagebox.showerror("Error", "Please enter a valid RTSP URL.")
            return
            
        cam_manager = self.app_controller.services['camera_manager']
        success = cam_manager.set_camera_index(url)
        if success:
            self.camera_var.set("IP Camera (RTSP)")
            messagebox.showinfo("Success", "Successfully connected to RTSP IP Camera!")
        else:
            messagebox.showerror("Error", "Failed to connect to RTSP Camera Stream.")

    def _refresh_data(self):
        for widget in self.scroll_body.winfo_children():
            widget.destroy()
            
        students = self.db_manager.get_all_students()
        if not students:
            lbl_empty = ctk.CTkLabel(self.scroll_body, text="No students registered.", text_color=Theme.TEXT_MUTED)
            lbl_empty.pack(pady=40)
            return
            
        for s_idx, student in enumerate(students):
            row_frame = ctk.CTkFrame(self.scroll_body, fg_color=Theme.SURFACE if s_idx % 2 == 0 else Theme.CARD_BG, corner_radius=8, height=38)
            row_frame.pack(fill="x", pady=2)
            
            for i, w in enumerate(self.weights):
                row_frame.grid_columnconfigure(i, weight=w)
                
            ctk.CTkLabel(row_frame, text=str(student.id), font=Theme.get_font_mono_small(), text_color=Theme.TEXT_MUTED).grid(row=0, column=0, padx=8, sticky="w")
            ctk.CTkLabel(row_frame, text=student.roll_number, font=Theme.get_font_mono_small(), text_color=Theme.PRIMARY).grid(row=0, column=1, padx=8, sticky="w")
            ctk.CTkLabel(row_frame, text=student.name, font=Theme.get_font_body(), text_color=Theme.TEXT_MAIN).grid(row=0, column=2, padx=8, sticky="w")
            ctk.CTkLabel(row_frame, text=student.department or "Computer Science", font=Theme.get_font_small(), text_color=Theme.TEXT_MUTED).grid(row=0, column=3, padx=8, sticky="w")
            ctk.CTkLabel(row_frame, text=str(student.registration_date), font=Theme.get_font_mono_small(), text_color=Theme.TEXT_MUTED).grid(row=0, column=4, padx=8, sticky="w")
            
            btn_del = ctk.CTkButton(
                row_frame,
                text="❌",
                width=36,
                height=26,
                fg_color=Theme.DANGER,
                hover_color=Theme.DANGER_HOVER,
                command=lambda s_id=student.id, s_name=student.name: self._delete_student(s_id, s_name)
            )
            btn_del.grid(row=0, column=5, padx=8, sticky="w")

    def _delete_student(self, student_id: int, student_name: str):
        if messagebox.askyesno("Confirm Deletion", f"Delete student {student_name} from local database?"):
            if self.db_manager.delete_student(student_id):
                self.embedding_matcher.load_students()
                self._refresh_data()
                messagebox.showinfo("Success", f"{student_name} deleted.")
