#!/usr/bin/env python3
"""
Sensor Reading Example
Demonstrates reading from various sensors
"""

import time
import sys
import os

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.gpio_control import GPIOController
from src.sensors.temperature import TemperatureSensor
from src.sensors.motion import MotionSensor, MotionDetector
from config.settings import GPIO_PINS

def motion_callback():
    """Callback function for motion detection"""
    print("🔔 Motion detected!")

def main():
    """Main example function"""
    print("Raspberry Pi Sensor Reading Example")
    print("===================================")
    
    # Initialize GPIO controller
    with GPIOController() as gpio:
        print("✓ GPIO controller initialized")
        
        # Initialize temperature sensor
        print("\n1. Temperature and Humidity Sensor (DHT22)")
        try:
            temp_sensor = TemperatureSensor()
            print("✓ DHT22 sensor initialized")
            
            # Read temperature and humidity
            for i in range(5):
                result = temp_sensor.read()
                if result:
                    temperature, humidity = result
                    print(f"   Reading {i+1}: {temperature:.1f}°C, {humidity:.1f}%")
                else:
                    print(f"   Reading {i+1}: Failed to read sensor")
                time.sleep(2)
                
        except Exception as e:
            print(f"✗ DHT22 sensor error: {e}")
        
        # Initialize motion sensor
        print("\n2. Motion Sensor (PIR)")
        try:
            motion_sensor = MotionSensor(callback=motion_callback)
            print("✓ PIR sensor initialized")
            
            print("   Monitoring for motion (30 seconds)...")
            start_time = time.time()
            
            while time.time() - start_time < 30:
                status = motion_sensor.get_motion_status()
                if status['motion_detected']:
                    print(f"   Motion detected at {time.ctime(status['last_motion_time'])}")
                    motion_sensor.reset_motion_flag()
                
                time.sleep(0.1)
            
            motion_sensor.cleanup()
            
        except Exception as e:
            print(f"✗ PIR sensor error: {e}")
        
        # Advanced motion detector
        print("\n3. Advanced Motion Detector")
        try:
            motion_detector = MotionDetector(GPIO_PINS['PIR_SENSOR'])
            print("✓ Advanced motion detector initialized")
            
            print("   Monitoring motion with statistics (20 seconds)...")
            start_time = time.time()
            
            while time.time() - start_time < 20:
                stats = motion_detector.get_motion_stats()
                
                if stats['is_active']:
                    print(f"   Motion active - Duration: {stats['current_duration']:.1f}s")
                elif stats['motion_count'] > 0:
                    print(f"   Motion count: {stats['motion_count']}")
                
                time.sleep(1)
            
            # Final statistics
            final_stats = motion_detector.get_motion_stats()
            print(f"\n   Final Statistics:")
            print(f"   - Total motion events: {final_stats['motion_count']}")
            print(f"   - Last motion duration: {final_stats['last_motion_duration']:.1f}s")
            
            motion_detector.cleanup()
            
        except Exception as e:
            print(f"✗ Advanced motion detector error: {e}")
        
        print("\n✓ Sensor reading example completed")

if __name__ == "__main__":
    main()