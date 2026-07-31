import customtkinter as ctk
import datetime

from src.gui.theme import Theme

class HistoryPage(ctk.CTkFrame):
    def __init__(self, master, app_controller, services: dict, **kwargs):
        super().__init__(master, fg_color="transparent", **kwargs)
        
        self.app_controller = app_controller
        self.db_manager = services['db_manager']
        
        self._build_ui()
        
    def _build_ui(self):
        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)
        
        # Header
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.grid(row=0, column=0, sticky="ew", padx=20, pady=20)
        
        lbl_title = ctk.CTkLabel(header, text="Attendance History (Today)", font=Theme.get_font_title())
        lbl_title.pack(side="left")
        
        self.btn_refresh = ctk.CTkButton(header, text="Refresh", command=self._refresh_data, width=100)
        self.btn_refresh.pack(side="right")
        
        # Table Container
        table_container = ctk.CTkFrame(self, fg_color=Theme.SURFACE, corner_radius=10, border_width=1, border_color=Theme.BORDER_COLOR)
        table_container.grid(row=1, column=0, sticky="nsew", padx=20, pady=(0, 20))
        
        # Table Header
        table_header = ctk.CTkFrame(table_container, fg_color=("gray85", "gray25"), corner_radius=10)
        table_header.pack(fill="x", padx=10, pady=10)
        
        cols = ["Name", "Roll Number", "Department", "Time Marked", "Session ID"]
        weights = [2, 1, 1, 1, 2]
        
        for i, (col, w) in enumerate(zip(cols, weights)):
            table_header.grid_columnconfigure(i, weight=w)
            lbl = ctk.CTkLabel(table_header, text=col, font=Theme.get_font_heading())
            lbl.grid(row=0, column=i, sticky="w", padx=10, pady=10)
            
        # Table Body (Scrollable)
        self.scroll_body = ctk.CTkScrollableFrame(table_container, fg_color="transparent")
        self.scroll_body.pack(expand=True, fill="both", padx=10, pady=(0, 10))
        
        # Empty state
        self.lbl_empty = ctk.CTkLabel(self.scroll_body, text="No attendance records for today.", text_color=Theme.TEXT_MUTED)
        
    def on_show(self):
        self._refresh_data()
        
    def on_hide(self):
        pass

    def _refresh_data(self):
        # Clear body
        for widget in self.scroll_body.winfo_children():
            widget.destroy()
            
        records = self.db_manager.get_today_attendance()
        
        if not records:
            self.lbl_empty = ctk.CTkLabel(self.scroll_body, text="No attendance records for today.", text_color=Theme.TEXT_MUTED)
            self.lbl_empty.pack(pady=40)
            return
            
        weights = [2, 1, 1, 1, 2]
            
        for r_idx, rec in enumerate(records):
            row_frame = ctk.CTkFrame(self.scroll_body, fg_color="transparent")
            row_frame.pack(fill="x", pady=2)
            
            time_obj = datetime.datetime.strptime(rec.marked_at, "%Y-%m-%d %H:%M:%S")
            time_str = time_obj.strftime("%I:%M:%S %p")
            
            data = [rec.name, rec.roll_number, rec.department, time_str, rec.session_id]
            
            for c_idx, (val, w) in enumerate(zip(data, weights)):
                row_frame.grid_columnconfigure(c_idx, weight=w)
                lbl = ctk.CTkLabel(row_frame, text=val, font=Theme.get_font_body())
                lbl.grid(row=0, column=c_idx, sticky="w", padx=10, pady=5)
                
            # Separator line
            sep = ctk.CTkFrame(self.scroll_body, height=1, fg_color=Theme.BORDER_COLOR)
            sep.pack(fill="x", padx=10)
