import os
import logging
from logging.handlers import RotatingFileHandler

_logger_initialized = False

def setup_logging(level: str, file: str, max_bytes: int, backup_count: int) -> None:
    """
    Sets up application-wide logging with both console and rotating file handlers.
    Should be called once at application startup.
    """
    global _logger_initialized
    if _logger_initialized:
        return

    # Ensure log directory exists
    log_dir = os.path.dirname(file)
    if log_dir and not os.path.exists(log_dir):
        os.makedirs(log_dir)

    numeric_level = getattr(logging, level.upper(), logging.INFO)

    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(numeric_level)
    
    # Clear any existing handlers
    if root_logger.hasHandlers():
        root_logger.handlers.clear()

    formatter = logging.Formatter(
        fmt='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )

    # Console Handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(numeric_level)
    console_handler.setFormatter(formatter)
    root_logger.addHandler(console_handler)

    # File Handler
    try:
        file_handler = RotatingFileHandler(
            filename=file,
            maxBytes=max_bytes,
            backupCount=backup_count,
            encoding='utf-8'
        )
        file_handler.setLevel(numeric_level)
        file_handler.setFormatter(formatter)
        root_logger.addHandler(file_handler)
    except Exception as e:
        print(f"Failed to setup file logging at {file}: {e}")

    _logger_initialized = True

def get_logger(name: str) -> logging.Logger:
    """
    Returns a configured logger for the given module name.
    """
    return logging.getLogger(name)
