import customtkinter as ctk
from src.gui.theme import Theme

class AnalyticsCard(ctk.CTkFrame):
    """
    Modern glass-styled KPI card with icon indicator, trend badge, and glow accent.
    """
    def __init__(self, master, title: str, value: str = "0", subtitle: str = None, icon: str = "📊", color: str = None, trend: str = None, **kwargs):
        super().__init__(
            master, 
            fg_color=Theme.CARD_BG, 
            corner_radius=14, 
            border_width=1, 
            border_color=Theme.BORDER_COLOR, 
            **kwargs
        )
        
        self.grid_columnconfigure(0, weight=1)
        
        # Header Row (Title + Icon Pill)
        header_frame = ctk.CTkFrame(self, fg_color="transparent")
        header_frame.pack(fill="x", padx=16, pady=(14, 4))
        
        lbl_title = ctk.CTkLabel(
            header_frame, 
            text=title.upper(), 
            font=Theme.get_font_mono_small(), 
            text_color=Theme.TEXT_MUTED
        )
        lbl_title.pack(side="left")
        
        if icon:
            icon_badge = ctk.CTkLabel(
                header_frame,
                text=icon,
                font=Theme.get_font_heading(),
                text_color=color if color else Theme.PRIMARY
            )
            icon_badge.pack(side="right")
        
        # Big Value Row
        val_color = color if color else Theme.TEXT_MAIN
        self.value_label = ctk.CTkLabel(
            self, 
            text=str(value), 
            font=ctk.CTkFont(family="Segoe UI", size=28, weight="bold"), 
            text_color=val_color
        )
        self.value_label.pack(padx=16, pady=(2, 6), anchor="w")
        
        # Subtitle / Trend Row
        if subtitle or trend:
            footer_frame = ctk.CTkFrame(self, fg_color="transparent")
            footer_frame.pack(fill="x", padx=16, pady=(0, 12))
            
            if subtitle:
                self.subtitle_label = ctk.CTkLabel(
                    footer_frame,
                    text=subtitle,
                    font=Theme.get_font_small(),
                    text_color=Theme.TEXT_MUTED
                )
                self.subtitle_label.pack(side="left")
                
            if trend:
                trend_badge = ctk.CTkLabel(
                    footer_frame,
                    text=trend,
                    font=Theme.get_font_mono_small(),
                    text_color=Theme.SUCCESS
                )
                trend_badge.pack(side="right")

    def set_value(self, value: str):
        self.value_label.configure(text=str(value))
