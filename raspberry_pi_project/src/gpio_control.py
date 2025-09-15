"""
GPIO Control Module for Raspberry Pi
Handles basic GPIO operations with error handling and logging
"""

import RPi.GPIO as GPIO
import time
import logging
from typing import Union, List, Dict, Optional
from config.settings import GPIO_PINS

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class GPIOController:
    """Main GPIO controller class"""
    
    def __init__(self, mode: str = 'BCM'):
        """
        Initialize GPIO controller
        
        Args:
            mode (str): GPIO numbering mode ('BCM' or 'BOARD')
        """
        self.mode = mode
        self.pin_modes = {}  # Track pin configurations
        self.initialized = False
        
        try:
            if mode.upper() == 'BCM':
                GPIO.setmode(GPIO.BCM)
            else:
                GPIO.setmode(GPIO.BOARD)
            self.initialized = True
            logger.info(f"GPIO initialized in {mode} mode")
        except Exception as e:
            logger.error(f"Failed to initialize GPIO: {e}")
            raise
    
    def setup_pin(self, pin: int, mode: str, pull_up_down: Optional[str] = None) -> bool:
        """
        Setup a GPIO pin
        
        Args:
            pin (int): GPIO pin number
            mode (str): 'in', 'out', or 'pwm'
            pull_up_down (str): 'PUD_UP', 'PUD_DOWN', or None
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            if mode.lower() == 'in':
                if pull_up_down:
                    pud = getattr(GPIO, pull_up_down)
                    GPIO.setup(pin, GPIO.IN, pull_up_down=pud)
                else:
                    GPIO.setup(pin, GPIO.IN)
            elif mode.lower() == 'out':
                GPIO.setup(pin, GPIO.OUT)
            elif mode.lower() == 'pwm':
                GPIO.setup(pin, GPIO.OUT)
                # PWM will be created separately
            else:
                raise ValueError(f"Invalid mode: {mode}")
            
            self.pin_modes[pin] = mode
            logger.info(f"Pin {pin} setup as {mode}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to setup pin {pin}: {e}")
            return False
    
    def write_pin(self, pin: int, value: Union[bool, int]) -> bool:
        """
        Write value to GPIO pin
        
        Args:
            pin (int): GPIO pin number
            value (Union[bool, int]): Value to write (True/1 or False/0)
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            if pin not in self.pin_modes or self.pin_modes[pin] != 'out':
                logger.warning(f"Pin {pin} not configured as output")
                return False
            
            GPIO.output(pin, value)
            logger.debug(f"Pin {pin} set to {value}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to write to pin {pin}: {e}")
            return False
    
    def read_pin(self, pin: int) -> Optional[bool]:
        """
        Read value from GPIO pin
        
        Args:
            pin (int): GPIO pin number
            
        Returns:
            Optional[bool]: Pin value or None if error
        """
        try:
            if pin not in self.pin_modes or self.pin_modes[pin] != 'in':
                logger.warning(f"Pin {pin} not configured as input")
                return None
            
            value = GPIO.input(pin)
            logger.debug(f"Pin {pin} reads {value}")
            return bool(value)
            
        except Exception as e:
            logger.error(f"Failed to read pin {pin}: {e}")
            return None
    
    def create_pwm(self, pin: int, frequency: int = 50) -> Optional[GPIO.PWM]:
        """
        Create PWM object for a pin
        
        Args:
            pin (int): GPIO pin number
            frequency (int): PWM frequency in Hz
            
        Returns:
            Optional[GPIO.PWM]: PWM object or None if error
        """
        try:
            if pin not in self.pin_modes or self.pin_modes[pin] not in ['out', 'pwm']:
                logger.warning(f"Pin {pin} not configured for PWM")
                return None
            
            pwm = GPIO.PWM(pin, frequency)
            logger.info(f"PWM created for pin {pin} at {frequency}Hz")
            return pwm
            
        except Exception as e:
            logger.error(f"Failed to create PWM for pin {pin}: {e}")
            return None
    
    def cleanup(self):
        """Cleanup GPIO resources"""
        try:
            GPIO.cleanup()
            self.pin_modes.clear()
            self.initialized = False
            logger.info("GPIO cleanup completed")
        except Exception as e:
            logger.error(f"Error during GPIO cleanup: {e}")
    
    def get_pin_status(self) -> Dict[int, str]:
        """
        Get status of all configured pins
        
        Returns:
            Dict[int, str]: Dictionary of pin numbers and their modes
        """
        return self.pin_modes.copy()
    
    def __enter__(self):
        """Context manager entry"""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        self.cleanup()

# Convenience functions
def setup_led_pins(controller: GPIOController) -> bool:
    """Setup LED pins for common use"""
    try:
        controller.setup_pin(GPIO_PINS['LED_RED'], 'out')
        controller.setup_pin(GPIO_PINS['LED_GREEN'], 'out')
        controller.setup_pin(GPIO_PINS['LED_BLUE'], 'out')
        logger.info("LED pins setup completed")
        return True
    except Exception as e:
        logger.error(f"Failed to setup LED pins: {e}")
        return False

def setup_button_pin(controller: GPIOController) -> bool:
    """Setup button pin with pull-up resistor"""
    try:
        controller.setup_pin(GPIO_PINS['BUTTON'], 'in', 'PUD_UP')
        logger.info("Button pin setup completed")
        return True
    except Exception as e:
        logger.error(f"Failed to setup button pin: {e}")
        return False