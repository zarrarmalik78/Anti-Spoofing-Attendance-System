import customtkinter as ctk
import tkinter.messagebox as messagebox

from src.gui.theme import Theme

class SettingsPage(ctk.CTkFrame):
    def __init__(self, master, app_controller, services: dict, **kwargs):
        super().__init__(master, fg_color="transparent", **kwargs)
        
        self.app_controller = app_controller
        self.db_manager = services['db_manager']
        self.embedding_matcher = services['embedding_matcher']
        
        self.grid_rowconfigure(1, weight=0)
        self.grid_rowconfigure(2, weight=1)
        self.grid_columnconfigure(0, weight=1)
        
        self._build_ui()
        
    def _build_ui(self):
        # Header
        header_frame = ctk.CTkFrame(self, fg_color="transparent")
        header_frame.grid(row=0, column=0, sticky="ew", padx=20, pady=20)
        
        lbl_title = ctk.CTkLabel(header_frame, text="System Settings & Registered Students", font=Theme.get_font_title())
        lbl_title.pack(side="left")
        
        btn_refresh = ctk.CTkButton(header_frame, text="Refresh DB", width=100, command=self._refresh_data)
        btn_refresh.pack(side="right")

        # Settings Container (Camera Selection)
        settings_container = ctk.CTkFrame(self, fg_color=Theme.SURFACE, corner_radius=10, border_width=1, border_color=Theme.BORDER_COLOR)
        settings_container.grid(row=1, column=0, sticky="ew", padx=20, pady=(0, 20))
        
        # Row 1: USB Webcams
        lbl_cam = ctk.CTkLabel(settings_container, text="USB Webcam:", font=Theme.get_font_heading())
        lbl_cam.grid(row=0, column=0, padx=15, pady=10, sticky="w")
        
        cam_manager = self.app_controller.services['camera_manager']
        current_val = f"Camera {cam_manager.index}" if isinstance(cam_manager.index, int) else "IP Camera (RTSP)"
        self.camera_var = ctk.StringVar(value=current_val)
        self.camera_combo = ctk.CTkComboBox(settings_container, variable=self.camera_var, command=self._on_camera_change, state="readonly", width=180)
        self.camera_combo.grid(row=0, column=1, padx=10, pady=10, sticky="w")
        
        btn_refresh_cam = ctk.CTkButton(settings_container, text="Scan USB Cams", width=120, command=self._scan_cameras)
        btn_refresh_cam.grid(row=0, column=2, padx=10, pady=10, sticky="w")
        
        # Row 2: RTSP IP Camera
        lbl_rtsp = ctk.CTkLabel(settings_container, text="IP Cam (RTSP):", font=Theme.get_font_heading())
        lbl_rtsp.grid(row=1, column=0, padx=15, pady=10, sticky="w")
        
        # 101 = Main Stream (High Quality), 102 = Sub-Stream (Lower Quality, Faster)
        default_rtsp = "rtsp://admin:soec@78612@192.168.1.28:554/Streaming/Channels/102"
        self.rtsp_entry = ctk.CTkEntry(settings_container, width=450, placeholder_text="rtsp://user:pass@ip:port/...")
        self.rtsp_entry.insert(0, default_rtsp)
        self.rtsp_entry.grid(row=1, column=1, columnspan=2, padx=10, pady=10, sticky="w")
        
        btn_connect_rtsp = ctk.CTkButton(settings_container, text="Connect IP Cam", width=120, fg_color=Theme.SUCCESS, hover_color="#27ae60", command=self._connect_rtsp)
        btn_connect_rtsp.grid(row=1, column=3, padx=10, pady=10, sticky="w")
        
        # Initial scan
        self._scan_cameras()
        
        # Table Container
        table_container = ctk.CTkFrame(self, fg_color=Theme.SURFACE, corner_radius=10, border_width=1, border_color=Theme.BORDER_COLOR)
        table_container.grid(row=2, column=0, sticky="nsew", padx=20, pady=(0, 20))
        
        # Table Headers
        table_header = ctk.CTkFrame(table_container, fg_color=("gray85", "gray25"), corner_radius=10)
        table_header.pack(fill="x", padx=10, pady=10)
        
        cols = ["Student ID (DB)", "Roll Number", "Name", "Department", "Registration Date", "Actions"]
        self.weights = [1, 2, 3, 2, 2, 1]
        
        for i, (col, w) in enumerate(zip(cols, self.weights)):
            table_header.grid_columnconfigure(i, weight=w)
            lbl = ctk.CTkLabel(table_header, text=col, font=Theme.get_font_heading())
            lbl.grid(row=0, column=i, sticky="w", padx=10, pady=10)
            
        # Table Body
        self.scroll_body = ctk.CTkScrollableFrame(table_container, fg_color="transparent")
        self.scroll_body.pack(expand=True, fill="both", padx=10, pady=(0, 10))
        
    def on_show(self):
        self._refresh_data()
        
    def _scan_cameras(self):
        cam_manager = self.app_controller.services['camera_manager']
        import threading
        
        # Disable combo on the main thread before starting the scan
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
                    self._on_camera_change(values[0])
            
            # Update UI on main thread
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
            messagebox.showerror("Error", "Failed to connect to RTSP Camera Stream. Please check URL / network connection.")

    def _refresh_data(self):
        for widget in self.scroll_body.winfo_children():
            widget.destroy()
            
        students = self.db_manager.get_all_students()
        
        if not students:
            lbl_empty = ctk.CTkLabel(self.scroll_body, text="No students registered.", text_color=Theme.TEXT_MUTED)
            lbl_empty.pack(pady=40)
            return
            
        for student in students:
            row_frame = ctk.CTkFrame(self.scroll_body, fg_color="transparent")
            row_frame.pack(fill="x", pady=2)
            
            data = [
                str(student.id),
                student.roll_number,
                student.name,
                student.department,
                student.registration_date,
            ]
            
            for c_idx, (val, w) in enumerate(zip(data, self.weights[:-1])):
                row_frame.grid_columnconfigure(c_idx, weight=w)
                lbl = ctk.CTkLabel(row_frame, text=val, font=Theme.get_font_body())
                lbl.grid(row=0, column=c_idx, sticky="w", padx=10, pady=5)
                
            # Actions Column
            row_frame.grid_columnconfigure(5, weight=self.weights[-1])
            btn_delete = ctk.CTkButton(
                row_frame, 
                text="❌ Delete", 
                width=80, 
                fg_color=Theme.DANGER, 
                hover_color="#c0392b",
                command=lambda s_id=student.id, s_name=student.name: self._delete_student(s_id, s_name)
            )
            btn_delete.grid(row=0, column=5, sticky="w", padx=10, pady=5)
            
            # Separator
            sep = ctk.CTkFrame(self.scroll_body, height=1, fg_color=Theme.BORDER_COLOR)
            sep.pack(fill="x", padx=10)

    def _delete_student(self, student_id: int, student_name: str):
        confirm = messagebox.askyesno("Confirm Deletion", f"Are you sure you want to delete {student_name} and all their attendance records?")
        if confirm:
            success = self.db_manager.delete_student(student_id)
            if success:
                # Reload matcher so the person is no longer recognized
                self.embedding_matcher.load_students()
                self._refresh_data()
                messagebox.showinfo("Success", f"{student_name} deleted successfully.")
            else:
                messagebox.showerror("Error", "Failed to delete student.")
