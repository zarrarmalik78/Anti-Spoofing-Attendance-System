import cv2
import os
os.environ["OPENCV_LOG_LEVEL"] = "ERROR" # Suppress ugly C++ warnings (like DSHOW backend exceptions)

import threading
import time
import numpy as np
from typing import Optional, Union

from src.utils.logger import get_logger

logger = get_logger(__name__)

class CameraManager:
    """
    Manages OpenCV camera capture (USB webcam index or RTSP IP camera URL) in a background thread to prevent UI freezing.
    Maintains a buffer of the most recently captured frame.
    """
    def __init__(self, index: Union[int, str] = 0, width: int = 640, height: int = 480, fps: int = 30):
        self.index = index
        self.width = width
        self.height = height
        self.target_fps = fps
        
        self.capture: Optional[cv2.VideoCapture] = None
        self.current_frame: Optional[np.ndarray] = None
        
        self.current_fps: float = 0.0
        self._fps_start_time = 0.0
        self._fps_frame_count = 0
        
        self._thread: Optional[threading.Thread] = None
        self._lock = threading.Lock()
        self._stop_event = threading.Event()
        self._connected = False
        
    def start(self) -> bool:
        """Opens the camera and starts the background capture thread."""
        if self._thread and self._thread.is_alive() and self._connected:
            logger.warning("Camera thread is already running.")
            return True
            
        opened = False
        
        # If index is a string (e.g. RTSP URL), open directly
        if isinstance(self.index, str):
            # Force TCP for RTSP to prevent packet loss / smearing
            import os
            os.environ["OPENCV_FFMPEG_CAPTURE_OPTIONS"] = "rtsp_transport;tcp"
            
            cap = cv2.VideoCapture(self.index, cv2.CAP_FFMPEG)
            cap.set(cv2.CAP_PROP_BUFFERSIZE, 1) # Prevent OpenCV from caching frames and causing delay
            
            if cap.isOpened():
                ret, test_frame = cap.read()
                if ret and test_frame is not None:
                    self.capture = cap
                    opened = True
                    logger.info(f"Opened RTSP/IP camera stream: {self.index}")
                else:
                    cap.release()
        else:
            # Try backends on Windows for maximum compatibility (DSHOW, MSMF, default)
            backends = [cv2.CAP_DSHOW, cv2.CAP_MSMF, cv2.CAP_ANY]
            
            # First try configured index
            for backend in backends:
                cap = cv2.VideoCapture(self.index, backend)
                if cap.isOpened():
                    # Read a test frame to ensure it actually works
                    ret, test_frame = cap.read()
                    if ret and test_frame is not None:
                        self.capture = cap
                        opened = True
                        logger.info(f"Opened camera index {self.index} with backend {backend}")
                        break
                    cap.release()
                    
            # Fallback to other indices (0, 1, 2) if configured index failed
            if not opened:
                for fallback_idx in [0, 1, 2]:
                    if fallback_idx == self.index:
                        continue
                    for backend in backends:
                        cap = cv2.VideoCapture(fallback_idx, backend)
                        if cap.isOpened():
                            ret, test_frame = cap.read()
                            if ret and test_frame is not None:
                                self.capture = cap
                                self.index = fallback_idx
                                opened = True
                                logger.info(f"Opened fallback camera index {fallback_idx} with backend {backend}")
                                break
                            cap.release()
                    if opened:
                        break

        if not opened or self.capture is None or not self.capture.isOpened():
            logger.error(f"Failed to open camera on source {self.index}.")
            self._connected = False
            return False
            
        # Try to set properties (Only for USB cams usually, won't hurt RTSP)
        self.capture.set(cv2.CAP_PROP_FRAME_WIDTH, self.width)
        self.capture.set(cv2.CAP_PROP_FRAME_HEIGHT, self.height)
        self.capture.set(cv2.CAP_PROP_FPS, self.target_fps)
        
        self._connected = True
        self._stop_event.clear()
        
        self._fps_start_time = time.time()
        self._fps_frame_count = 0
        self.current_fps = 0.0
        
        self._thread = threading.Thread(target=self._update_frame, daemon=True)
        self._thread.start()
        
        logger.info(f"Camera started successfully on index {self.index}")
        return True
        
    def _update_frame(self) -> None:
        """Background thread loop that continuously reads frames."""
        # Calculate delay to respect target FPS (mostly for file inputs, but good practice)
        sleep_delay = 1.0 / self.target_fps
        fail_count = 0
        
        while not self._stop_event.is_set():
            if self.capture and self.capture.isOpened():
                ret, frame = self.capture.read()
                if ret:
                    fail_count = 0
                    with self._lock:
                        self.current_frame = frame
                    
                    # Calculate FPS
                    self._fps_frame_count += 1
                    elapsed = time.time() - self._fps_start_time
                    if elapsed >= 1.0:
                        self.current_fps = self._fps_frame_count / elapsed
                        self._fps_start_time = time.time()
                        self._fps_frame_count = 0
                else:
                    fail_count += 1
                    if fail_count % 30 == 1:
                        logger.warning(f"Failed to read frame from camera. (Failed {fail_count} times consecutively)")
                    time.sleep(0.1) # backoff if camera hiccups
            time.sleep(sleep_delay)
            
    def get_current_fps(self) -> float:
        """Returns the current calculated FPS of the camera stream."""
        return self.current_fps

    def get_frame(self) -> Optional[np.ndarray]:
        """Returns the most recent frame."""
        with self._lock:
            if self.current_frame is not None:
                return self.current_frame.copy()
        return None
        
    def is_connected(self) -> bool:
        """Returns whether the camera is currently opened and capturing."""
        return self._connected
        
    def stop(self) -> None:
        """Stops the capture thread and releases the camera."""
        if self._connected:
            logger.info("Stopping camera...")
            self._stop_event.set()
            if self._thread:
                self._thread.join(timeout=2.0)
            
            if self.capture:
                self.capture.release()
                
            self._connected = False
            with self._lock:
                self.current_frame = None
            logger.info("Camera stopped.")

    def set_camera_index(self, index: Union[int, str]) -> bool:
        """Dynamically switches the camera to the specified index or RTSP URL."""
        if self.index == index:
            return True
            
        logger.info(f"Switching camera from {self.index} to {index}")
        was_connected = self._connected
        
        if was_connected:
            self.stop()
            
        self.index = index
        
        if was_connected:
            return self.start()
        return True

    @staticmethod
    def get_available_cameras(max_tested=3) -> list[int]:
        """Returns a list of available camera indices."""
        available = []
        backends = [cv2.CAP_DSHOW, cv2.CAP_MSMF, cv2.CAP_ANY]
        for i in range(max_tested):
            for backend in backends:
                try:
                    cap = cv2.VideoCapture(i, backend)
                    if cap.isOpened():
                        ret, frame = cap.read()
                        if ret and frame is not None:
                            available.append(i)
                            cap.release()
                            break
                        cap.release()
                except Exception as e:
                    logger.debug(f"Exception while probing camera index {i} with backend {backend}: {e}")
        return available

    def __enter__(self):
        self.start()
        return self
        
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.stop()
