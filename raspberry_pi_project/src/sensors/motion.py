"""
Motion sensor module for PIR (Passive Infrared) sensor
"""

import time
import logging
from typing import Optional, Callable
import RPi.GPIO as GPIO
from config.settings import SENSOR_CONFIG

logger = logging.getLogger(__name__)

class MotionSensor:
    """PIR Motion Sensor"""
    
    def __init__(self, pin: Optional[int] = None, callback: Optional[Callable] = None):
        """
        Initialize motion sensor
        
        Args:
            pin (int): GPIO pin number for PIR sensor
            callback (Callable): Function to call when motion is detected
        """
        self.pin = pin or SENSOR_CONFIG['PIR']['pin']
        self.callback = callback
        self.warmup_time = SENSOR_CONFIG['PIR']['warmup_time']
        self.motion_detected = False
        self.last_motion_time = 0
        
        # Setup GPIO pin
        GPIO.setup(self.pin, GPIO.IN)
        
        # Setup interrupt for motion detection
        GPIO.add_event_detect(self.pin, GPIO.RISING, callback=self._motion_callback)
        
        logger.info(f"Motion sensor initialized on pin {self.pin}")
        logger.info(f"Warming up for {self.warmup_time} seconds...")
        
        # Warmup period
        time.sleep(self.warmup_time)
        logger.info("Motion sensor ready")
    
    def _motion_callback(self, channel):
        """Internal callback for motion detection"""
        current_time = time.time()
        
        # Debounce: ignore if motion detected within last 2 seconds
        if current_time - self.last_motion_time < 2:
            return
        
        self.motion_detected = True
        self.last_motion_time = current_time
        
        logger.info("Motion detected!")
        
        if self.callback:
            try:
                self.callback()
            except Exception as e:
                logger.error(f"Error in motion callback: {e}")
    
    def is_motion_detected(self) -> bool:
        """
        Check if motion is currently detected
        
        Returns:
            bool: True if motion detected, False otherwise
        """
        return GPIO.input(self.pin) == GPIO.HIGH
    
    def get_motion_status(self) -> dict:
        """
        Get detailed motion status
        
        Returns:
            dict: Motion status information
        """
        current_time = time.time()
        time_since_motion = current_time - self.last_motion_time if self.last_motion_time > 0 else None
        
        return {
            'motion_detected': self.motion_detected,
            'current_state': self.is_motion_detected(),
            'last_motion_time': self.last_motion_time,
            'time_since_motion': time_since_motion,
            'pin': self.pin
        }
    
    def reset_motion_flag(self):
        """Reset the motion detected flag"""
        self.motion_detected = False
        logger.debug("Motion flag reset")
    
    def set_callback(self, callback: Callable):
        """
        Set or update the motion detection callback
        
        Args:
            callback (Callable): Function to call when motion is detected
        """
        self.callback = callback
        logger.info("Motion callback updated")
    
    def cleanup(self):
        """Cleanup motion sensor resources"""
        try:
            GPIO.remove_event_detect(self.pin)
            logger.info("Motion sensor cleanup completed")
        except Exception as e:
            logger.error(f"Error during motion sensor cleanup: {e}")

class MotionDetector:
    """Advanced motion detector with multiple features"""
    
    def __init__(self, pin: int, sensitivity: float = 0.5, timeout: float = 30.0):
        """
        Initialize advanced motion detector
        
        Args:
            pin (int): GPIO pin number
            sensitivity (float): Motion sensitivity (0.0 to 1.0)
            timeout (float): Timeout in seconds before considering motion ended
        """
        self.pin = pin
        self.sensitivity = max(0.0, min(1.0, sensitivity))
        self.timeout = timeout
        self.motion_start_time = None
        self.motion_end_time = None
        self.motion_count = 0
        
        # Setup GPIO
        GPIO.setup(self.pin, GPIO.IN)
        GPIO.add_event_detect(self.pin, GPIO.RISING, callback=self._on_motion_start)
        GPIO.add_event_detect(self.pin, GPIO.FALLING, callback=self._on_motion_end)
        
        logger.info(f"Advanced motion detector initialized on pin {self.pin}")
    
    def _on_motion_start(self, channel):
        """Handle motion start"""
        current_time = time.time()
        
        # Check if this is a new motion event
        if self.motion_start_time is None or current_time - self.motion_end_time > 1.0:
            self.motion_start_time = current_time
            self.motion_count += 1
            logger.info(f"Motion started (count: {self.motion_count})")
    
    def _on_motion_end(self, channel):
        """Handle motion end"""
        current_time = time.time()
        self.motion_end_time = current_time
        
        if self.motion_start_time:
            duration = current_time - self.motion_start_time
            logger.info(f"Motion ended after {duration:.2f} seconds")
    
    def get_motion_stats(self) -> dict:
        """
        Get motion statistics
        
        Returns:
            dict: Motion statistics
        """
        current_time = time.time()
        
        return {
            'motion_count': self.motion_count,
            'is_active': self.is_motion_active(),
            'current_duration': current_time - self.motion_start_time if self.motion_start_time else 0,
            'last_motion_duration': self.motion_end_time - self.motion_start_time if self.motion_start_time and self.motion_end_time else 0,
            'sensitivity': self.sensitivity,
            'timeout': self.timeout
        }
    
    def is_motion_active(self) -> bool:
        """
        Check if motion is currently active
        
        Returns:
            bool: True if motion is active, False otherwise
        """
        if self.motion_start_time is None:
            return False
        
        current_time = time.time()
        
        # Check if motion has timed out
        if self.motion_end_time and current_time - self.motion_end_time > self.timeout:
            return False
        
        # Check if motion is currently detected
        return GPIO.input(self.pin) == GPIO.HIGH
    
    def cleanup(self):
        """Cleanup motion detector resources"""
        try:
            GPIO.remove_event_detect(self.pin)
            logger.info("Motion detector cleanup completed")
        except Exception as e:
            logger.error(f"Error during motion detector cleanup: {e}")