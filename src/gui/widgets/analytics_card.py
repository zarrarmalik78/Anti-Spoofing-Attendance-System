import customtkinter as ctk
from src.gui.theme import Theme

class AnalyticsCard(ctk.CTkFrame):
    """
    A simple card widget for the dashboard displaying a KPI.
    """
    def __init__(self, master, title: str, value: str = "0", color: str = None, **kwargs):
        super().__init__(master, fg_color=Theme.SURFACE, corner_radius=8, border_width=1, border_color=Theme.BORDER_COLOR, **kwargs)
        
        self.title_label = ctk.CTkLabel(
            self, 
            text=title, 
            font=Theme.get_font_body(), 
            text_color=Theme.TEXT_MUTED
        )
        self.title_label.pack(padx=15, pady=(15, 0), anchor="w")
        
        val_color = color if color else Theme.TEXT_MAIN
        self.value_label = ctk.CTkLabel(
            self, 
            text=str(value), 
            font=ctk.CTkFont(family="Inter", size=32, weight="bold"), 
            text_color=val_color
        )
        self.value_label.pack(padx=15, pady=(5, 15), anchor="w")

    def set_value(self, value: str):
        self.value_label.configure(text=str(value))
