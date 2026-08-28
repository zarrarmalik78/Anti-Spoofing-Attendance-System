import customtkinter as ctk

class Theme:
    """
    Ultra-modern, high-tech dark theme configuration for CustomTkinter.
    Designed for professional Edge AI Biometric & University Attendance System.
    """
    
    # Core Surfaces (Modern Slate Dark & Light)
    BACKGROUND = ("#F8FAFC", "#0B0F19")       # Slate 50 / Dark Slate 950
    SIDEBAR_BG = ("#0F172A", "#060911")       # Slate 900 / Deep Slate 950
    SURFACE = ("#FFFFFF", "#131C2E")          # Pure White / Slate 900
    SURFACE_HOVER = ("#F1F5F9", "#1E293B")    # Slate 100 / Slate 800
    CARD_BG = ("#FFFFFF", "#162032")          # Card Body
    CARD_HOVER = ("#F8FAFC", "#1C283F")
    
    # Accent & Brand Colors
    PRIMARY = "#6366F1"                       # Vibrant Indigo 500
    PRIMARY_HOVER = "#4F46E5"                 # Indigo 600
    PRIMARY_LIGHT = ("#EEF2FF", "#1E1B4B")    # Indigo 50 / Indigo 950
    
    SECONDARY = "#818CF8"                     # Soft Indigo 400
    ACCENT_CYAN = "#06B6D4"                   # Cyan 500 (Tech Accent)
    
    # Functional / Status Colors
    SUCCESS = "#10B981"                       # Emerald 500 (Live / Verified)
    SUCCESS_HOVER = "#059669"
    SUCCESS_BG = ("#ECFDF5", "#064E3B")
    
    DANGER = "#F43F5E"                        # Rose 500 (Spoof / Error)
    DANGER_HOVER = "#E11D48"
    DANGER_BG = ("#FFF1F2", "#881337")
    
    WARNING = "#F59E0B"                       # Amber 500 (Late / Warning)
    WARNING_HOVER = "#D97706"
    WARNING_BG = ("#FFFBEB", "#78350F")
    
    # Typography Colors
    TEXT_MAIN = ("#0F172A", "#F8FAFC")        # Slate 900 / Slate 50
    TEXT = TEXT_MAIN
    TEXT_MUTED = ("#64748B", "#94A3B8")       # Slate 500 / Slate 400
    TEXT_DIM = ("#94A3B8", "#64748B")         # Slate 400 / Slate 500
    
    # Borders & Dividers
    BORDER_COLOR = ("#E2E8F0", "#1E293B")     # Slate 200 / Slate 800
    BORDER_SUBTLE = ("#F1F5F9", "#151F30")
    BORDER_ACCENT = "#6366F1"
    
    # HUD / Overlay Colors (for Camera & Anti-Spoof)
    HUD_GREEN = "#10B981"
    HUD_RED = "#F43F5E"
    HUD_CYAN = "#00F0FF"
    HUD_YELLOW = "#FBBF24"
    
    @classmethod
    def setup(cls, appearance_mode: str = "dark"):
        ctk.set_appearance_mode(appearance_mode)
        ctk.set_default_color_theme("blue")

    @classmethod
    def get_font_hero(cls) -> ctk.CTkFont:
        return ctk.CTkFont(family="Segoe UI", size=26, weight="bold")

    @classmethod
    def get_font_title(cls) -> ctk.CTkFont:
        return ctk.CTkFont(family="Segoe UI", size=20, weight="bold")
        
    @classmethod
    def get_font_heading(cls) -> ctk.CTkFont:
        return ctk.CTkFont(family="Segoe UI", size=15, weight="bold")

    @classmethod
    def get_font_subheading(cls) -> ctk.CTkFont:
        return ctk.CTkFont(family="Segoe UI", size=13, weight="bold")
        
    @classmethod
    def get_font_body(cls) -> ctk.CTkFont:
        return ctk.CTkFont(family="Segoe UI", size=12)
        
    @classmethod
    def get_font_small(cls) -> ctk.CTkFont:
        return ctk.CTkFont(family="Segoe UI", size=11)
        
    @classmethod
    def get_font_mono(cls) -> ctk.CTkFont:
        return ctk.CTkFont(family="Consolas", size=11, weight="bold")

    @classmethod
    def get_font_mono_small(cls) -> ctk.CTkFont:
        return ctk.CTkFont(family="Consolas", size=9)
