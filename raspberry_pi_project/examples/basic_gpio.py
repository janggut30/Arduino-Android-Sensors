#!/usr/bin/env python3
"""
Basic GPIO Example
Demonstrates basic GPIO operations with LEDs and buttons
"""

import time
import sys
import os

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.gpio_control import GPIOController, setup_led_pins, setup_button_pin
from src.actuators.led_control import LEDController, LEDPattern
from config.settings import GPIO_PINS

def main():
    """Main example function"""
    print("Raspberry Pi Basic GPIO Example")
    print("===============================")
    
    # Initialize GPIO controller
    with GPIOController() as gpio:
        print("✓ GPIO controller initialized")
        
        # Setup LEDs
        if setup_led_pins(gpio):
            print("✓ LED pins configured")
        else:
            print("✗ Failed to setup LED pins")
            return
        
        # Setup button
        if setup_button_pin(gpio):
            print("✓ Button pin configured")
        else:
            print("✗ Failed to setup button pin")
            return
        
        # Initialize LED controller
        leds = LEDController(gpio)
        patterns = LEDPattern(leds)
        
        print("\nLED Control Examples:")
        print("1. Individual LED control")
        
        # Test individual LEDs
        for color in ['red', 'green', 'blue']:
            print(f"   Turning on {color} LED...")
            leds.turn_on(color)
            time.sleep(1)
            leds.turn_off(color)
            time.sleep(0.5)
        
        print("\n2. LED blinking pattern")
        patterns.blink('red', duration=0.5, count=3)
        patterns.blink('green', duration=0.3, count=5)
        patterns.blink('blue', duration=0.8, count=2)
        
        print("\n3. Button interaction")
        print("   Press the button to toggle LEDs (Ctrl+C to exit)")
        
        try:
            button_pressed = False
            while True:
                # Read button state
                button_state = gpio.read_pin(GPIO_PINS['BUTTON'])
                
                # Detect button press (LOW when pressed due to pull-up)
                if not button_state and not button_pressed:
                    button_pressed = True
                    print("   Button pressed!")
                    
                    # Toggle all LEDs
                    for color in ['red', 'green', 'blue']:
                        leds.toggle(color)
                        time.sleep(0.1)
                
                elif button_state and button_pressed:
                    button_pressed = False
                    print("   Button released!")
                
                time.sleep(0.01)  # Small delay to prevent excessive CPU usage
                
        except KeyboardInterrupt:
            print("\n\nExiting...")
            leds.all_off()
            print("✓ All LEDs turned off")

if __name__ == "__main__":
    main()