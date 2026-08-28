import customtkinter as ctk
import time
import webbrowser
from typing import Dict, Any

from src.gui.theme import Theme
from src.gui.widgets.status_bar import StatusBar
from src.gui.pages.dashboard_page import DashboardPage
from src.gui.pages.register_page import RegisterPage
from src.gui.pages.antispoof_page import AntiSpoofPage
from src.gui.pages.recognition_page import RecognitionPage
from src.gui.pages.history_page import HistoryPage
from src.gui.pages.settings_page import SettingsPage

from src.database.db_manager import DatabaseManager
from src.core.camera_manager import CameraManager
from src.core.face_engine import FaceEngine
from src.core.embedding_matcher import EmbeddingMatcher
from src.core.attendance_engine import AttendanceEngine
from src.core.ai_engine import AIEngine
from src.core.student_registrar import StudentRegistrar
from src.firebase.firebase_service import FirebaseService
from src.utils.logger import get_logger

logger = get_logger(__name__)

class App(ctk.CTk):
    """
    Main application shell with high-tech dark navigation, telemetry header, and shared AI services.
    """
    def __init__(self, config: Dict[str, Any]):
        super().__init__()
        
        self.config = config
        
        # Setup Window & Modern Appearance
        Theme.setup(appearance_mode=self.config.get("gui", {}).get("theme", "dark"))
        self.title(self.config.get("gui", {}).get("window_title", "Edge AI Biometric Attendance System"))
        w = self.config.get("gui", {}).get("window_width", 1320)
        h = self.config.get("gui", {}).get("window_height", 820)
        self.geometry(f"{w}x{h}")
        self.minsize(1100, 680)
        
        # Window Background
        self.configure(fg_color=Theme.BACKGROUND)
        
        # Handle close gracefully
        self.protocol("WM_DELETE_WINDOW", self._on_closing)
        
        # Initialize Services
        self._init_services()
        
        # Build UI Layout
        self.grid_rowconfigure(0, weight=1) # Main content
        self.grid_rowconfigure(1, weight=0) # Status bar
        self.grid_columnconfigure(0, weight=0) # Sidebar
        self.grid_columnconfigure(1, weight=1) # Main view
        
        self._build_sidebar()
        self._build_status_bar()
        self._build_main_area()
        
        # Show default page
        self.show_page("Dashboard")

    def _init_services(self):
        """Initialize all backend services once and pass them to pages."""
        logger.info("Initializing Edge AI services...")
        
        # DB
        db_path = self.config.get("database", {}).get("path", "data/attendance.db")
        self.db_manager = DatabaseManager(db_path)
        self.db_manager.initialize()
        
        # Camera
        cam_cfg = self.config.get("camera", {})
        self.camera_manager = CameraManager(
            index=cam_cfg.get("index", 0),
            width=cam_cfg.get("frame_width", 640),
            height=cam_cfg.get("frame_height", 480),
            fps=cam_cfg.get("fps", 30)
        )
        
        # InsightFace
        mod_cfg = self.config.get("models", {})
        self.face_engine = FaceEngine(
            config=self.config,
            model_root=mod_cfg.get("root", "models"),
            pack_name=mod_cfg.get("pack_name", "buffalo_l"),
            providers=mod_cfg.get("providers", ["CPUExecutionProvider"])
        )
        
        # Matcher
        self.embedding_matcher = EmbeddingMatcher(self.db_manager)
        
        # AI Engine
        sim_threshold = self.config.get("recognition", {}).get("similarity_threshold", 0.45)
        self.ai_engine = AIEngine(self.face_engine, self.embedding_matcher, sim_threshold)
        
        # Firebase integration with offline queue fallback
        self.firebase_service = FirebaseService()
        self.firebase_service.attach_db_manager(self.db_manager)
        
        # Attendance logic
        stab_sec = self.config.get("recognition", {}).get("stability_seconds", 1.0)
        self.attendance_engine = AttendanceEngine(self.db_manager, self.firebase_service, stab_sec)
        
        # Registrar
        self.student_registrar = StudentRegistrar(
            self.face_engine, 
            self.db_manager, 
            self.embedding_matcher,
            self.firebase_service
        )
        
        # Bundle for pages
        self.services = {
            'db_manager': self.db_manager,
            'camera_manager': self.camera_manager,
            'face_engine': self.face_engine,
            'embedding_matcher': self.embedding_matcher,
            'ai_engine': self.ai_engine,
            'firebase_service': self.firebase_service,
            'attendance_engine': self.attendance_engine,
            'student_registrar': self.student_registrar
        }
        logger.info("Services initialized successfully.")

    def _build_sidebar(self):
        self.sidebar = ctk.CTkFrame(
            self, 
            fg_color=Theme.SIDEBAR_BG, 
            corner_radius=0, 
            width=230,
            border_width=1,
            border_color=Theme.BORDER_COLOR
        )
        self.sidebar.grid(row=0, column=0, sticky="nsew")
        self.sidebar.grid_rowconfigure(8, weight=1) # Spacer to push web portal button down
        
        # Brand Logo Banner
        brand_frame = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        brand_frame.grid(row=0, column=0, padx=20, pady=(24, 28), sticky="ew")
        
        lbl_brand_tag = ctk.CTkLabel(
            brand_frame, 
            text="EDGE AI • BIOMETRICS", 
            font=Theme.get_font_mono_small(), 
            text_color=Theme.PRIMARY
        )
        lbl_brand_tag.pack(anchor="w")
        
        lbl_brand = ctk.CTkLabel(
            brand_frame, 
            text="Attendance OS", 
            font=Theme.get_font_hero(), 
            text_color=Theme.TEXT_MAIN
        )
        lbl_brand.pack(anchor="w")
        
        # Navigation Items
        self.nav_buttons = {}
        
        nav_items = [
            ("Dashboard", "⊞  Dashboard"), 
            ("Register Student", "👤  Register Student"), 
            ("Anti-Spoof Test", "🛡️  Anti-Spoof Lab"),
            ("Live Recognition", "📷  Live Recognition"), 
            ("Attendance History", "🕒  Attendance History"),
            ("System Settings", "⚙️  System Settings")
        ]
        
        for i, (item_id, text) in enumerate(nav_items):
            btn = ctk.CTkButton(
                self.sidebar, 
                text=text, 
                fg_color="transparent", 
                text_color=Theme.TEXT_MUTED,
                hover_color=Theme.SURFACE_HOVER,
                anchor="w",
                font=Theme.get_font_heading(),
                height=42,
                corner_radius=10,
                command=lambda name=item_id: self.show_page(name)
            )
            btn.grid(row=i+1, column=0, padx=14, pady=4, sticky="ew")
            self.nav_buttons[item_id] = btn

        # Bottom "Open Web Portal" Button
        bottom_frame = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        bottom_frame.grid(row=9, column=0, padx=14, pady=20, sticky="ew")
        
        btn_web = ctk.CTkButton(
            bottom_frame,
            text="🌐 Open Web Portal",
            font=Theme.get_font_subheading(),
            height=44,
            fg_color=Theme.PRIMARY,
            hover_color=Theme.PRIMARY_HOVER,
            command=self._open_web_portal
        )
        btn_web.pack(fill="x")
        
        lbl_edge_status = ctk.CTkLabel(
            bottom_frame,
            text="● NODE-01 • ONLINE",
            font=Theme.get_font_mono_small(),
            text_color=Theme.SUCCESS
        )
        lbl_edge_status.pack(pady=(8, 0))

    def _open_web_portal(self):
        webbrowser.open("http://localhost:5173")

    def _build_status_bar(self):
        self.status_bar = StatusBar(self, self.camera_manager, self.embedding_matcher, self.db_manager)
        self.status_bar.grid(row=1, column=0, columnspan=2, sticky="ew")

    def _build_main_area(self):
        """Builds the header and the page container."""
        self.main_area = ctk.CTkFrame(self, fg_color="transparent")
        self.main_area.grid(row=0, column=1, sticky="nsew")
        self.main_area.grid_rowconfigure(1, weight=1)
        self.main_area.grid_columnconfigure(0, weight=1)
        
        # Header
        self.header_frame = ctk.CTkFrame(
            self.main_area, 
            fg_color=Theme.SURFACE, 
            corner_radius=0, 
            height=64,
            border_width=1,
            border_color=Theme.BORDER_COLOR
        )
        self.header_frame.grid(row=0, column=0, sticky="ew")
        
        left_h = ctk.CTkFrame(self.header_frame, fg_color="transparent")
        left_h.pack(side="left", padx=24, pady=12)
        
        self.lbl_page_title = ctk.CTkLabel(left_h, text="Dashboard", font=Theme.get_font_title(), text_color=Theme.TEXT_MAIN)
        self.lbl_page_title.pack(anchor="w")
        
        # Header Right Side (Date/Time & Web Button)
        right_header = ctk.CTkFrame(self.header_frame, fg_color="transparent")
        right_header.pack(side="right", padx=24)
        
        self.lbl_datetime = ctk.CTkLabel(
            right_header, 
            text="--/--/----, --:-- --", 
            font=Theme.get_font_mono(),
            text_color=Theme.TEXT_MUTED,
            justify="right"
        )
        self.lbl_datetime.pack(side="right")
        
        self._update_time_loop()
        self._init_pages()

    def _update_time_loop(self):
        from src.utils.time_utils import get_current_time
        now = get_current_time()
        time_str = now.strftime("%b %d, %Y  •  %I:%M:%S %p")
        self.lbl_datetime.configure(text=time_str)
        self.after(1000, self._update_time_loop)

    def _init_pages(self):
        self.pages = {}
        
        # Container for pages
        self.page_container = ctk.CTkFrame(self.main_area, fg_color="transparent")
        self.page_container.grid(row=1, column=0, sticky="nsew")
        self.page_container.grid_rowconfigure(0, weight=1)
        self.page_container.grid_columnconfigure(0, weight=1)
        
        # Instantiate pages
        self.pages["Dashboard"] = DashboardPage(self.page_container, self, self.services)
        self.pages["Register Student"] = RegisterPage(self.page_container, self, self.services)
        self.pages["Anti-Spoof Test"] = AntiSpoofPage(self.page_container, self, self.services)
        self.pages["Live Recognition"] = RecognitionPage(self.page_container, self, self.services)
        self.pages["Attendance History"] = HistoryPage(self.page_container, self, self.services)
        self.pages["System Settings"] = SettingsPage(self.page_container, self, self.services)
        
        self.current_page = None

    def show_page(self, page_name: str):
        """Switches the visible page in the main content area."""
        if self.current_page == page_name:
            return
            
        # Update sidebar button styles and header title
        for name, btn in self.nav_buttons.items():
            if name == page_name:
                btn.configure(
                    fg_color=Theme.PRIMARY_LIGHT, 
                    text_color=Theme.PRIMARY
                )
                self.lbl_page_title.configure(text=name)
            else:
                btn.configure(
                    fg_color="transparent", 
                    text_color=Theme.TEXT_MUTED
                )
                
        # Hide old page
        if self.current_page:
            self.pages[self.current_page].grid_forget()
            if hasattr(self.pages[self.current_page], "on_hide"):
                self.pages[self.current_page].on_hide()
                
        # Show new page
        page = self.pages[page_name]
        page.grid(row=0, column=0, sticky="nsew")
        if hasattr(page, "on_show"):
            page.on_show()
            
        self.current_page = page_name

    def _on_closing(self):
        """Clean up resources before exiting."""
        logger.info("Application shutting down...")
        if self.current_page and hasattr(self.pages[self.current_page], "on_hide"):
            self.pages[self.current_page].on_hide()
            
        if self.camera_manager:
            self.camera_manager.stop()
            
        self.destroy()
