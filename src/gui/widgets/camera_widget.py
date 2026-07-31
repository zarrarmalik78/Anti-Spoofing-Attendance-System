import customtkinter as ctk
import cv2
from PIL import Image
from typing import Callable, Optional
import time

from src.core.camera_manager import CameraManager

class CameraWidget(ctk.CTkLabel):
    """
    Reusable widget to display a live camera feed.
    """
    def __init__(self, master, camera_manager: CameraManager, width: int = 640, height: int = 480, **kwargs):
        # Initialize as empty label
        super().__init__(master, text="Waiting for camera...", width=width, height=height, **kwargs)
        
        self.camera_manager = camera_manager
        self.target_width = width
        self.target_height = height
        
        self.overlay_callback: Optional[Callable] = None
        
        self.is_running = False
        self._fps_times = []
        self.current_fps = 0.0

    def start(self):
        """Starts the camera manager (if not started) and the frame polling loop."""
        if not self.camera_manager.is_connected():
            self.camera_manager.start()
            
        if not self.is_running:
            self.is_running = True
            self._update_frame()

    def stop(self):
        """Stops the frame polling loop and releases the camera hardware."""
        self.is_running = False
        if self.camera_manager and self.camera_manager.is_connected():
            self.camera_manager.stop()

    def set_overlay_callback(self, callback: Callable):
        """
        Sets a function that will be called with the BGR frame before it is displayed.
        The callback should return the modified frame (or same frame).
        """
        self.overlay_callback = callback

    def _update_frame(self):
        if not self.is_running:
            return

        frame = self.camera_manager.get_frame()
        
        if frame is not None:
            # Apply any custom overlays (bounding boxes, instructions, etc.)
            if self.overlay_callback:
                try:
                    frame = self.overlay_callback(frame)
                except Exception as e:
                    print(f"Error in overlay callback: {e}")

            # Convert BGR to RGB
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            
            # Resize for display
            # cv2 resize is much faster than PIL resize
            frame_resized = cv2.resize(frame_rgb, (self.target_width, self.target_height))

            # Convert to PIL Image then to CTkImage
            pil_image = Image.fromarray(frame_resized)
            ctk_image = ctk.CTkImage(light_image=pil_image, dark_image=pil_image, 
                                     size=(self.target_width, self.target_height))
            
            self.configure(image=ctk_image, text="") # Clear text, show image
            
            # Calculate FPS
            now = time.time()
            self._fps_times.append(now)
            # Keep last 30 frames
            if len(self._fps_times) > 30:
                self._fps_times.pop(0)
            if len(self._fps_times) > 1:
                elapsed = self._fps_times[-1] - self._fps_times[0]
                if elapsed > 0:
                    self.current_fps = (len(self._fps_times) - 1) / elapsed
                    
            # Draw FPS on frame
            fps_color = (0, 255, 0) if self.current_fps > 10 else (255, 0, 0) # Green if good, Red if bad (RGB format)
            cv2.putText(frame_rgb, f"FPS: {self.current_fps:.1f}", (15, 35), 
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 0), 3) # Outline
            cv2.putText(frame_rgb, f"FPS: {self.current_fps:.1f}", (15, 35), 
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, fps_color, 2)
        else:
            if not self.camera_manager.is_connected():
                self.configure(image=None, text="Camera Disconnected / Not Accessible\n\nCheck Windows Privacy & Security Settings -> Camera\nand ensure 'Let desktop apps access your camera' is ON.")
            else:
                self.configure(text="Waiting for camera frames...")
        
        # Schedule next update (aim for ~30 FPS UI refresh)
        if self.is_running:
            self.after(33, self._update_frame)
