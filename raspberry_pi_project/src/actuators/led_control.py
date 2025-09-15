"""
LED Control Module for Raspberry Pi
Supports RGB LEDs, individual LEDs, and various lighting patterns
"""

import time
import threading
import logging
from typing import List, Tuple, Optional, Callable
from src.gpio_control import GPIOController
from config.settings import GPIO_PINS

logger = logging.getLogger(__name__)

class LEDController:
    """Basic LED controller for individual LEDs"""
    
    def __init__(self, gpio_controller: GPIOController):
        """
        Initialize LED controller
        
        Args:
            gpio_controller (GPIOController): GPIO controller instance
        """
        self.gpio = gpio_controller
        self.leds = {}
        
        # Setup default LED pins
        self.setup_led('red', GPIO_PINS['LED_RED'])
        self.setup_led('green', GPIO_PINS['LED_GREEN'])
        self.setup_led('blue', GPIO_PINS['LED_BLUE'])
        
        logger.info("LED controller initialized")
    
    def setup_led(self, name: str, pin: int) -> bool:
        """
        Setup an LED
        
        Args:
            name (str): LED name
            pin (int): GPIO pin number
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            self.gpio.setup_pin(pin, 'out')
            self.leds[name] = pin
            logger.info(f"LED '{name}' setup on pin {pin}")
            return True
        except Exception as e:
            logger.error(f"Failed to setup LED '{name}': {e}")
            return False
    
    def turn_on(self, name: str) -> bool:
        """
        Turn on an LED
        
        Args:
            name (str): LED name
            
        Returns:
            bool: True if successful, False otherwise
        """
        if name not in self.leds:
            logger.error(f"LED '{name}' not found")
            return False
        
        return self.gpio.write_pin(self.leds[name], True)
    
    def turn_off(self, name: str) -> bool:
        """
        Turn off an LED
        
        Args:
            name (str): LED name
            
        Returns:
            bool: True if successful, False otherwise
        """
        if name not in self.leds:
            logger.error(f"LED '{name}' not found")
            return False
        
        return self.gpio.write_pin(self.leds[name], False)
    
    def toggle(self, name: str) -> bool:
        """
        Toggle an LED state
        
        Args:
            name (str): LED name
            
        Returns:
            bool: True if successful, False otherwise
        """
        if name not in self.leds:
            logger.error(f"LED '{name}' not found")
            return False
        
        current_state = self.gpio.read_pin(self.leds[name])
        return self.gpio.write_pin(self.leds[name], not current_state)
    
    def set_state(self, name: str, state: bool) -> bool:
        """
        Set LED state
        
        Args:
            name (str): LED name
            state (bool): True for on, False for off
            
        Returns:
            bool: True if successful, False otherwise
        """
        if name not in self.leds:
            logger.error(f"LED '{name}' not found")
            return False
        
        return self.gpio.write_pin(self.leds[name], state)
    
    def get_state(self, name: str) -> Optional[bool]:
        """
        Get LED state
        
        Args:
            name (str): LED name
            
        Returns:
            Optional[bool]: LED state or None if error
        """
        if name not in self.leds:
            logger.error(f"LED '{name}' not found")
            return None
        
        return self.gpio.read_pin(self.leds[name])
    
    def all_off(self):
        """Turn off all LEDs"""
        for name in self.leds:
            self.turn_off(name)
        logger.info("All LEDs turned off")
    
    def all_on(self):
        """Turn on all LEDs"""
        for name in self.leds:
            self.turn_on(name)
        logger.info("All LEDs turned on")

class RGBLED:
    """RGB LED controller with color mixing"""
    
    def __init__(self, gpio_controller: GPIOController, red_pin: int, green_pin: int, blue_pin: int):
        """
        Initialize RGB LED
        
        Args:
            gpio_controller (GPIOController): GPIO controller instance
            red_pin (int): Red LED pin
            green_pin (int): Green LED pin
            blue_pin (int): Blue LED pin
        """
        self.gpio = gpio_controller
        self.pins = {
            'red': red_pin,
            'green': green_pin,
            'blue': blue_pin
        }
        
        # Setup pins
        for color, pin in self.pins.items():
            self.gpio.setup_pin(pin, 'out')
        
        # Current color state
        self.current_color = (0, 0, 0)  # (R, G, B)
        
        logger.info(f"RGB LED initialized on pins R:{red_pin}, G:{green_pin}, B:{blue_pin}")
    
    def set_color(self, red: int, green: int, blue: int) -> bool:
        """
        Set RGB color
        
        Args:
            red (int): Red intensity (0-255)
            green (int): Green intensity (0-255)
            blue (int): Blue intensity (0-255)
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            # Clamp values to 0-255 range
            red = max(0, min(255, red))
            green = max(0, min(255, green))
            blue = max(0, min(255, blue))
            
            # Convert to 0-1 range for GPIO
            red_val = red / 255.0
            green_val = green / 255.0
            blue_val = blue / 255.0
            
            # Set pins (assuming common cathode - invert for common anode)
            self.gpio.write_pin(self.pins['red'], red_val > 0.5)
            self.gpio.write_pin(self.pins['green'], green_val > 0.5)
            self.gpio.write_pin(self.pins['blue'], blue_val > 0.5)
            
            self.current_color = (red, green, blue)
            logger.debug(f"RGB color set to ({red}, {green}, {blue})")
            return True
            
        except Exception as e:
            logger.error(f"Failed to set RGB color: {e}")
            return False
    
    def set_color_hex(self, hex_color: str) -> bool:
        """
        Set color from hex string
        
        Args:
            hex_color (str): Hex color string (e.g., '#FF0000' or 'FF0000')
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            # Remove # if present
            hex_color = hex_color.lstrip('#')
            
            # Convert to RGB
            red = int(hex_color[0:2], 16)
            green = int(hex_color[2:4], 16)
            blue = int(hex_color[4:6], 16)
            
            return self.set_color(red, green, blue)
            
        except Exception as e:
            logger.error(f"Failed to set hex color '{hex_color}': {e}")
            return False
    
    def get_color(self) -> Tuple[int, int, int]:
        """
        Get current color
        
        Returns:
            Tuple[int, int, int]: Current RGB color
        """
        return self.current_color
    
    def off(self):
        """Turn off RGB LED"""
        self.set_color(0, 0, 0)
    
    def on(self, red: int = 255, green: int = 255, blue: int = 255):
        """Turn on RGB LED with white color by default"""
        self.set_color(red, green, blue)

class LEDPattern:
    """LED pattern controller for animations and effects"""
    
    def __init__(self, led_controller: LEDController):
        """
        Initialize LED pattern controller
        
        Args:
            led_controller (LEDController): LED controller instance
        """
        self.leds = led_controller
        self.running = False
        self.thread = None
        
        logger.info("LED pattern controller initialized")
    
    def blink(self, name: str, duration: float = 1.0, count: int = 5) -> bool:
        """
        Blink an LED
        
        Args:
            name (str): LED name
            duration (float): Blink duration in seconds
            count (int): Number of blinks
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            for _ in range(count):
                self.leds.turn_on(name)
                time.sleep(duration / 2)
                self.leds.turn_off(name)
                time.sleep(duration / 2)
            
            logger.info(f"LED '{name}' blinked {count} times")
            return True
            
        except Exception as e:
            logger.error(f"Failed to blink LED '{name}': {e}")
            return False
    
    def start_breathing(self, name: str, duration: float = 2.0, min_brightness: float = 0.1, max_brightness: float = 1.0):
        """
        Start breathing effect for an LED
        
        Args:
            name (str): LED name
            duration (float): Breathing cycle duration in seconds
            min_brightness (float): Minimum brightness (0.0-1.0)
            max_brightness (float): Maximum brightness (0.0-1.0)
        """
        if self.running:
            self.stop_pattern()
        
        self.running = True
        self.thread = threading.Thread(
            target=self._breathing_effect,
            args=(name, duration, min_brightness, max_brightness)
        )
        self.thread.daemon = True
        self.thread.start()
        
        logger.info(f"Started breathing effect for LED '{name}'")
    
    def _breathing_effect(self, name: str, duration: float, min_brightness: float, max_brightness: float):
        """Internal breathing effect implementation"""
        import math
        
        while self.running:
            try:
                # Calculate breathing pattern using sine wave
                t = time.time() % duration
                phase = (t / duration) * 2 * math.pi
                brightness = (math.sin(phase) + 1) / 2  # 0 to 1
                brightness = min_brightness + (max_brightness - min_brightness) * brightness
                
                # For simple on/off LEDs, use PWM simulation
                if brightness > 0.5:
                    self.leds.turn_on(name)
                else:
                    self.leds.turn_off(name)
                
                time.sleep(0.05)  # 50ms update rate
                
            except Exception as e:
                logger.error(f"Error in breathing effect: {e}")
                break
    
    def start_rainbow(self, rgb_led: RGBLED, duration: float = 5.0):
        """
        Start rainbow effect for RGB LED
        
        Args:
            rgb_led (RGBLED): RGB LED instance
            duration (float): Rainbow cycle duration in seconds
        """
        if self.running:
            self.stop_pattern()
        
        self.running = True
        self.thread = threading.Thread(
            target=self._rainbow_effect,
            args=(rgb_led, duration)
        )
        self.thread.daemon = True
        self.thread.start()
        
        logger.info("Started rainbow effect")
    
    def _rainbow_effect(self, rgb_led: RGBLED, duration: float):
        """Internal rainbow effect implementation"""
        import math
        
        while self.running:
            try:
                # Calculate rainbow color
                t = time.time() % duration
                hue = (t / duration) * 360  # 0 to 360 degrees
                
                # Convert HSV to RGB
                h = hue / 60.0
                i = int(h)
                f = h - i
                
                if i == 0:
                    r, g, b = 1, f, 0
                elif i == 1:
                    r, g, b = 1-f, 1, 0
                elif i == 2:
                    r, g, b = 0, 1, f
                elif i == 3:
                    r, g, b = 0, 1-f, 1
                elif i == 4:
                    r, g, b = f, 0, 1
                else:
                    r, g, b = 1, 0, 1-f
                
                # Convert to 0-255 range
                red = int(r * 255)
                green = int(g * 255)
                blue = int(b * 255)
                
                rgb_led.set_color(red, green, blue)
                time.sleep(0.05)  # 50ms update rate
                
            except Exception as e:
                logger.error(f"Error in rainbow effect: {e}")
                break
    
    def stop_pattern(self):
        """Stop current pattern"""
        self.running = False
        if self.thread and self.thread.is_alive():
            self.thread.join(timeout=1.0)
        
        logger.info("Pattern stopped")