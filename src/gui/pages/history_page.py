import customtkinter as ctk
import datetime
import csv
from tkinter import filedialog, messagebox

from src.gui.theme import Theme

class HistoryPage(ctk.CTkFrame):
    """
    Modern Attendance History & Log Audit Page with search, filtering, and CSV export.
    """
    def __init__(self, master, app_controller, services: dict, **kwargs):
        super().__init__(master, fg_color="transparent", **kwargs)
        
        self.app_controller = app_controller
        self.db_manager = services['db_manager']
        self.records = []
        
        self._build_ui()
        
    def _build_ui(self):
        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)
        
        # Header
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.grid(row=0, column=0, sticky="ew", padx=20, pady=(20, 12))
        
        left_head = ctk.CTkFrame(header, fg_color="transparent")
        left_head.pack(side="left")
        
        lbl_title = ctk.CTkLabel(left_head, text="🕒 Attendance Audit History", font=Theme.get_font_title())
        lbl_title.pack(anchor="w")
        
        self.lbl_subtitle = ctk.CTkLabel(
            left_head, 
            text="Local edge device verification logs stored in SQLite database", 
            font=Theme.get_font_small(), 
            text_color=Theme.TEXT_MUTED
        )
        self.lbl_subtitle.pack(anchor="w")
        
        right_head = ctk.CTkFrame(header, fg_color="transparent")
        right_head.pack(side="right")
        
        self.btn_export = ctk.CTkButton(
            right_head, 
            text="📥 Export CSV", 
            font=Theme.get_font_heading(),
            height=38,
            fg_color=Theme.SURFACE_HOVER,
            hover_color=Theme.BORDER_COLOR,
            text_color=Theme.TEXT_MAIN,
            command=self._export_csv
        )
        self.btn_export.pack(side="right", padx=(8, 0))
        
        self.btn_refresh = ctk.CTkButton(
            right_head, 
            text="🔄 Refresh", 
            font=Theme.get_font_heading(),
            height=38,
            fg_color=Theme.PRIMARY,
            hover_color=Theme.PRIMARY_HOVER,
            command=self._refresh_data
        )
        self.btn_refresh.pack(side="right")
        
        # Search Bar
        search_card = ctk.CTkFrame(self, fg_color=Theme.CARD_BG, corner_radius=12, border_width=1, border_color=Theme.BORDER_COLOR)
        search_card.grid(row=1, column=0, sticky="ew", padx=20, pady=(0, 10))
        
        self.entry_search = ctk.CTkEntry(
            search_card, 
            placeholder_text="🔍 Filter records by student name, roll number, or department...",
            font=Theme.get_font_body(),
            height=38
        )
        self.entry_search.pack(fill="x", padx=12, pady=10)
        self.entry_search.bind("<KeyRelease>", lambda e: self._filter_rows())
        
        # Table Container
        table_container = ctk.CTkFrame(
            self, 
            fg_color=Theme.CARD_BG, 
            corner_radius=16, 
            border_width=1, 
            border_color=Theme.BORDER_COLOR
        )
        table_container.grid(row=2, column=0, sticky="nsew", padx=20, pady=(0, 20))
        self.grid_rowconfigure(2, weight=1)
        
        # Table Header
        table_header = ctk.CTkFrame(table_container, fg_color=Theme.SURFACE_HOVER, corner_radius=8, height=34)
        table_header.pack(fill="x", padx=12, pady=12)
        
        cols = [("TIME MARKED", 2), ("ROLL NUMBER", 2), ("STUDENT NAME", 3), ("DEPARTMENT", 3), ("STATUS", 2)]
        for i, (col, w) in enumerate(cols):
            table_header.grid_columnconfigure(i, weight=w)
            lbl = ctk.CTkLabel(
                table_header, 
                text=col, 
                font=Theme.get_font_mono_small(), 
                text_color=Theme.TEXT_MUTED
            )
            lbl.grid(row=0, column=i, sticky="w", padx=10, pady=6)
            
        # Table Body (Scrollable)
        self.scroll_body = ctk.CTkScrollableFrame(table_container, fg_color="transparent")
        self.scroll_body.pack(expand=True, fill="both", padx=10, pady=(0, 10))
        
    def on_show(self):
        self._refresh_data()
        
    def _refresh_data(self):
        self.records = self.db_manager.get_today_attendance()
        self._filter_rows()

    def _filter_rows(self):
        for widget in self.scroll_body.winfo_children():
            widget.destroy()
            
        query = self.entry_search.get().strip().lower()
        filtered = [
            r for r in self.records 
            if not query or 
            query in str(r.name).lower() or 
            query in str(r.roll_number).lower() or 
            query in str(r.department).lower()
        ]
        
        if not filtered:
            lbl_empty = ctk.CTkLabel(
                self.scroll_body, 
                text="No matching attendance records found.", 
                font=Theme.get_font_body(),
                text_color=Theme.TEXT_MUTED
            )
            lbl_empty.pack(pady=40)
            return
            
        for r_idx, rec in enumerate(filtered):
            row_frame = ctk.CTkFrame(
                self.scroll_body, 
                fg_color=Theme.SURFACE if r_idx % 2 == 0 else Theme.CARD_BG, 
                corner_radius=8,
                height=38
            )
            row_frame.pack(fill="x", pady=2)
            
            row_frame.grid_columnconfigure(0, weight=2)
            row_frame.grid_columnconfigure(1, weight=2)
            row_frame.grid_columnconfigure(2, weight=3)
            row_frame.grid_columnconfigure(3, weight=3)
            row_frame.grid_columnconfigure(4, weight=2)
            
            try:
                time_obj = datetime.datetime.strptime(rec.marked_at, "%Y-%m-%d %H:%M:%S")
                time_str = time_obj.strftime("%I:%M:%S %p")
            except Exception:
                time_str = str(rec.marked_at)
                
            # Time
            ctk.CTkLabel(row_frame, text=time_str, font=Theme.get_font_mono_small(), text_color=Theme.TEXT_MUTED).grid(row=0, column=0, padx=10, sticky="w")
            
            # Roll No
            ctk.CTkLabel(row_frame, text=rec.roll_number, font=Theme.get_font_mono_small(), text_color=Theme.PRIMARY).grid(row=0, column=1, padx=10, sticky="w")
            
            # Name
            ctk.CTkLabel(row_frame, text=rec.name, font=Theme.get_font_body(), text_color=Theme.TEXT_MAIN).grid(row=0, column=2, padx=10, sticky="w")
            
            # Dept
            ctk.CTkLabel(row_frame, text=rec.department or "Computer Science", font=Theme.get_font_small(), text_color=Theme.TEXT_MUTED).grid(row=0, column=3, padx=10, sticky="w")
            
            # Status
            badge = ctk.CTkLabel(
                row_frame,
                text="✔ PRESENT",
                font=Theme.get_font_mono_small(),
                text_color=Theme.SUCCESS
            )
            badge.grid(row=0, column=4, padx=10, sticky="w")

    def _export_csv(self):
        if not self.records:
            messagebox.showinfo("Export", "No records available to export.")
            return
            
        file_path = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV Files", "*.csv")],
            initialfile=f"Attendance_Log_{datetime.date.today()}.csv"
        )
        if not file_path:
            return
            
        try:
            with open(file_path, "w", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)
                writer.writerow(["Student ID", "Roll Number", "Name", "Department", "Time Marked", "Session ID"])
                for r in self.records:
                    writer.writerow([r.student_id, r.roll_number, r.name, r.department, r.marked_at, r.session_id])
            messagebox.showinfo("Export Successful", f"Records successfully saved to:\n{file_path}")
        except Exception as e:
            messagebox.showerror("Export Failed", f"Could not save file: {e}")
