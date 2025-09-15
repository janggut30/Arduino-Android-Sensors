"""
GPIO Tests
Test cases for GPIO functionality
"""

import unittest
import sys
import os
from unittest.mock import Mock, patch

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.gpio_control import GPIOController, setup_led_pins, setup_button_pin

class TestGPIOController(unittest.TestCase):
    """Test cases for GPIOController class"""
    
    def setUp(self):
        """Set up test fixtures"""
        # Mock RPi.GPIO to avoid hardware dependency
        self.gpio_patcher = patch('src.gpio_control.GPIO')
        self.mock_gpio = self.gpio_patcher.start()
        
        # Create controller instance
        self.controller = GPIOController()
    
    def tearDown(self):
        """Clean up after tests"""
        self.gpio_patcher.stop()
    
    def test_initialization(self):
        """Test GPIO controller initialization"""
        self.assertTrue(self.controller.initialized)
        self.assertEqual(self.controller.mode, 'BCM')
        self.mock_gpio.setmode.assert_called_with(self.mock_gpio.BCM)
    
    def test_setup_pin_output(self):
        """Test setting up output pin"""
        result = self.controller.setup_pin(18, 'out')
        
        self.assertTrue(result)
        self.mock_gpio.setup.assert_called_with(18, self.mock_gpio.OUT)
        self.assertEqual(self.controller.pin_modes[18], 'out')
    
    def test_setup_pin_input(self):
        """Test setting up input pin"""
        result = self.controller.setup_pin(24, 'in')
        
        self.assertTrue(result)
        self.mock_gpio.setup.assert_called_with(24, self.mock_gpio.IN)
        self.assertEqual(self.controller.pin_modes[24], 'in')
    
    def test_setup_pin_input_with_pullup(self):
        """Test setting up input pin with pull-up resistor"""
        result = self.controller.setup_pin(25, 'in', 'PUD_UP')
        
        self.assertTrue(result)
        self.mock_gpio.setup.assert_called_with(25, self.mock_gpio.IN, pull_up_down=self.mock_gpio.PUD_UP)
        self.assertEqual(self.controller.pin_modes[25], 'in')
    
    def test_write_pin_success(self):
        """Test writing to pin successfully"""
        # Setup pin first
        self.controller.setup_pin(18, 'out')
        
        result = self.controller.write_pin(18, True)
        
        self.assertTrue(result)
        self.mock_gpio.output.assert_called_with(18, True)
    
    def test_write_pin_not_configured(self):
        """Test writing to pin that's not configured as output"""
        result = self.controller.write_pin(18, True)
        
        self.assertFalse(result)
        self.mock_gpio.output.assert_not_called()
    
    def test_read_pin_success(self):
        """Test reading from pin successfully"""
        # Setup pin first
        self.controller.setup_pin(24, 'in')
        self.mock_gpio.input.return_value = True
        
        result = self.controller.read_pin(24)
        
        self.assertTrue(result)
        self.mock_gpio.input.assert_called_with(24)
    
    def test_read_pin_not_configured(self):
        """Test reading from pin that's not configured as input"""
        result = self.controller.read_pin(24)
        
        self.assertIsNone(result)
        self.mock_gpio.input.assert_not_called()
    
    def test_create_pwm(self):
        """Test creating PWM object"""
        # Setup pin first
        self.controller.setup_pin(12, 'pwm')
        mock_pwm = Mock()
        self.mock_gpio.PWM.return_value = mock_pwm
        
        result = self.controller.create_pwm(12, 50)
        
        self.assertEqual(result, mock_pwm)
        self.mock_gpio.PWM.assert_called_with(12, 50)
    
    def test_cleanup(self):
        """Test GPIO cleanup"""
        self.controller.cleanup()
        
        self.mock_gpio.cleanup.assert_called_once()
        self.assertFalse(self.controller.initialized)
        self.assertEqual(len(self.controller.pin_modes), 0)
    
    def test_context_manager(self):
        """Test using GPIOController as context manager"""
        with GPIOController() as controller:
            self.assertTrue(controller.initialized)
        
        self.mock_gpio.cleanup.assert_called_once()

class TestConvenienceFunctions(unittest.TestCase):
    """Test cases for convenience functions"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.gpio_patcher = patch('src.gpio_control.GPIO')
        self.mock_gpio = self.gpio_patcher.start()
        
        self.controller = GPIOController()
    
    def tearDown(self):
        """Clean up after tests"""
        self.gpio_patcher.stop()
    
    def test_setup_led_pins(self):
        """Test setting up LED pins"""
        result = setup_led_pins(self.controller)
        
        self.assertTrue(result)
        # Should setup 3 LED pins
        self.assertEqual(self.mock_gpio.setup.call_count, 3)
    
    def test_setup_button_pin(self):
        """Test setting up button pin"""
        result = setup_button_pin(self.controller)
        
        self.assertTrue(result)
        self.mock_gpio.setup.assert_called_with(25, self.mock_gpio.IN, pull_up_down=self.mock_gpio.PUD_UP)

if __name__ == '__main__':
    unittest.main()