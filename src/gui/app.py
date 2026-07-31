import customtkinter as ctk
import time
from typing import Dict, Any

from src.gui.theme import Theme
from src.gui.widgets.status_bar import StatusBar
from src.gui.pages.dashboard_page import DashboardPage
from src.gui.pages.register_page import RegisterPage
from src.gui.pages.recognition_page import RecognitionPage
from src.gui.pages.history_page import HistoryPage
from src.gui.pages.settings_page import SettingsPage

from src.database.db_manager import DatabaseManager
from src.core.camera_manager import CameraManager
from src.core.face_engine import FaceEngine
from src.core.embedding_matcher import EmbeddingMatcher
from src.core.attendance_manager import AttendanceManager
from src.core.student_registrar import StudentRegistrar
from src.utils.logger import get_logger

logger = get_logger(__name__)

class App(ctk.CTk):
    """
    Main application shell containing navigation and shared services.
    """
    def __init__(self, config: Dict[str, Any]):
        super().__init__()
        
        self.config = config
        
        # Setup Window
        Theme.setup(appearance_mode=self.config.get("gui", {}).get("theme", "light"))
        self.title(self.config.get("gui", {}).get("window_title", "Edge AI Attendance System"))
        w = self.config.get("gui", {}).get("window_width", 1280)
        h = self.config.get("gui", {}).get("window_height", 780)
        self.geometry(f"{w}x{h}")
        self.minsize(1024, 600)
        
        # Handle close gracefully
        self.protocol("WM_DELETE_WINDOW", self._on_closing)
        
        # Initialize Services
        self._init_services()
        
        # Build UI Structure
        self.grid_rowconfigure(0, weight=1) # Main content area
        self.grid_rowconfigure(1, weight=0) # Status bar
        self.grid_columnconfigure(0, weight=0) # Sidebar
        self.grid_columnconfigure(1, weight=1) # Pages area
        
        self._build_sidebar()
        self._build_status_bar()
        self._build_main_area()
        
        # Show default page
        self.show_page("Dashboard")

    def _init_services(self):
        """Initialize all backend services once and pass them to pages."""
        logger.info("Initializing services...")
        
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
        # Don't start camera here, let pages manage it to save CPU when not needed
        
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
        
        # Attendance logic
        stab_sec = self.config.get("recognition", {}).get("stability_seconds", 1.0)
        self.attendance_manager = AttendanceManager(self.db_manager, stab_sec)
        
        # Registrar
        self.student_registrar = StudentRegistrar(self.face_engine, self.db_manager, self.embedding_matcher)
        
        # Bundle for pages
        self.services = {
            'db_manager': self.db_manager,
            'camera_manager': self.camera_manager,
            'face_engine': self.face_engine,
            'embedding_matcher': self.embedding_matcher,
            'attendance_manager': self.attendance_manager,
            'student_registrar': self.student_registrar
        }
        logger.info("Services initialized.")

    def _build_sidebar(self):
        self.sidebar = ctk.CTkFrame(self, fg_color=Theme.PRIMARY, corner_radius=0, width=200)
        self.sidebar.grid(row=0, column=0, sticky="nsew")
        self.sidebar.grid_rowconfigure(5, weight=1) # Spacer
        
        lbl_brand = ctk.CTkLabel(self.sidebar, text="Edge AI\nAttendance", font=Theme.get_font_title(), text_color="#ffffff")
        lbl_brand.grid(row=0, column=0, padx=20, pady=(30, 40))
        
        self.nav_buttons = {}
        
        # Using Unicode icons for simplicity as requested
        nav_items = [
            ("Dashboard", "⊞ Dashboard"), 
            ("Register Student", "👤 Register Student"), 
            ("Live Recognition", "📷 Live Recognition"), 
            ("Attendance History", "🕒 Attendance History"),
            ("System Settings", "⚙️ System Settings")
        ]
        
        for i, (item_id, text) in enumerate(nav_items):
            btn = ctk.CTkButton(
                self.sidebar, 
                text=text, 
                fg_color="transparent", 
                text_color="#ffffff",
                hover_color=Theme.PRIMARY_HOVER,
                anchor="w",
                font=Theme.get_font_heading(),
                command=lambda name=item_id: self.show_page(name)
            )
            btn.grid(row=i+1, column=0, padx=10, pady=5, sticky="ew")
            self.nav_buttons[item_id] = btn

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
        self.header_frame = ctk.CTkFrame(self.main_area, fg_color=Theme.SURFACE, corner_radius=0, height=60)
        self.header_frame.grid(row=0, column=0, sticky="ew")
        
        self.lbl_page_title = ctk.CTkLabel(self.header_frame, text="System Dashboard", font=Theme.get_font_title())
        self.lbl_page_title.pack(side="left", padx=20, pady=15)
        
        # Header Right Side (Date/Time)
        right_header = ctk.CTkFrame(self.header_frame, fg_color="transparent")
        right_header.pack(side="right", padx=20)
        
        self.lbl_datetime = ctk.CTkLabel(right_header, text="Current Date/Time\n--/--/----, --:-- --", justify="right")
        self.lbl_datetime.pack(side="right")
        
        self._update_time_loop()
        
        self._init_pages()

    def _update_time_loop(self):
        from src.utils.time_utils import get_current_time
        now = get_current_time()
        time_str = now.strftime("%m/%d/%Y, %I:%M %p")
        self.lbl_datetime.configure(text=f"Current Date/Time\n{time_str}")
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
                btn.configure(fg_color=Theme.PRIMARY_HOVER)
                self.lbl_page_title.configure(text=name)
            else:
                btn.configure(fg_color="transparent")
                
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
        # Stop any active page
        if self.current_page and hasattr(self.pages[self.current_page], "on_hide"):
            self.pages[self.current_page].on_hide()
            
        # Stop camera
        if self.camera_manager:
            self.camera_manager.stop()
            
        self.destroy()
