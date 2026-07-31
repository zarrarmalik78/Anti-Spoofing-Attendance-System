import os
import sys

# Suppress OpenCV C++ backend warnings (DSHOW, MSMF) before any cv2 imports happen globally
os.environ["OPENCV_LOG_LEVEL"] = "ERROR"
os.environ["OPENCV_VIDEOIO_MSMF_ENABLE_HW_TRANSFORMS"] = "0"
from src.utils.config_loader import load_config
from src.utils.logger import setup_logging, get_logger
from src.gui.app import App

def main():
    try:
        # 1. Load config
        config = load_config()
        
        # 2. Setup logging
        log_cfg = config.get("logging", {})
        setup_logging(
            level=log_cfg.get("level", "INFO"),
            file=log_cfg.get("file", "logs/app.log"),
            max_bytes=log_cfg.get("max_bytes", 5242880),
            backup_count=log_cfg.get("backup_count", 3)
        )
        
        logger = get_logger(__name__)
        logger.info("Starting Edge AI Attendance System")
        
        # 3. Launch App
        app = App(config)
        app.mainloop()
        
    except Exception as e:
        print(f"Fatal error during startup: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
