import customtkinter as ctk

class Theme:
    """
    Centralized theme configuration for CustomTkinter.
    Provides consistent colors, fonts, and styles across the app.
    """
    
    # Colors
    PRIMARY = "#1e4c7a"
    PRIMARY_HOVER = "#2a629c"
    SUCCESS = "#2ecc71"
    DANGER = "#e74c3c"
    WARNING = "#f1c40f"
    TEXT_MAIN = ("#1a1a1a", "#f2f2f2") # Light mode / Dark mode
    TEXT = TEXT_MAIN
    TEXT_MUTED = ("#666666", "#a0a0a0")
    SURFACE = ("#ffffff", "#2b2b2b")
    BACKGROUND = ("#f5f6f8", "#1e1e1e")
    
    # Border
    BORDER_COLOR = ("#e0e0e0", "#3a3a3a")
    
    @classmethod
    def setup(cls, appearance_mode: str = "light"):
        ctk.set_appearance_mode(appearance_mode)
        ctk.set_default_color_theme("blue")

    @classmethod
    def get_font_title(cls) -> ctk.CTkFont:
        return ctk.CTkFont(family="Inter", size=24, weight="bold")
        
    @classmethod
    def get_font_heading(cls) -> ctk.CTkFont:
        return ctk.CTkFont(family="Inter", size=18, weight="bold")
        
    @classmethod
    def get_font_body(cls) -> ctk.CTkFont:
        return ctk.CTkFont(family="Inter", size=14)
        
    @classmethod
    def get_font_mono(cls) -> ctk.CTkFont:
        return ctk.CTkFont(family="Consolas", size=12)
