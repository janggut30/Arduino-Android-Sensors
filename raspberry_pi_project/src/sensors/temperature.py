"""
Temperature sensor module for DHT22
"""

import time
import logging
from typing import Optional, Tuple
import RPi.GPIO as GPIO
from config.settings import SENSOR_CONFIG

logger = logging.getLogger(__name__)

class TemperatureSensor:
    """DHT22 Temperature and Humidity Sensor"""
    
    def __init__(self, pin: Optional[int] = None):
        """
        Initialize temperature sensor
        
        Args:
            pin (int): GPIO pin number for DHT22 data pin
        """
        self.pin = pin or SENSOR_CONFIG['DHT22']['pin']
        self.retry_count = SENSOR_CONFIG['DHT22']['retry_count']
        self.delay = SENSOR_CONFIG['DHT22']['delay']
        
        # Setup GPIO pin
        GPIO.setup(self.pin, GPIO.OUT)
        GPIO.output(self.pin, GPIO.HIGH)
        time.sleep(0.1)
        
        logger.info(f"Temperature sensor initialized on pin {self.pin}")
    
    def read(self) -> Optional[Tuple[float, float]]:
        """
        Read temperature and humidity from DHT22
        
        Returns:
            Optional[Tuple[float, float]]: (temperature, humidity) or None if error
        """
        for attempt in range(self.retry_count):
            try:
                # Send start signal
                GPIO.output(self.pin, GPIO.LOW)
                time.sleep(0.018)  # 18ms low signal
                GPIO.output(self.pin, GPIO.HIGH)
                time.sleep(0.00004)  # 40μs high signal
                
                # Change to input mode
                GPIO.setup(self.pin, GPIO.IN)
                
                # Wait for response
                timeout = 0
                while GPIO.input(self.pin) == GPIO.LOW:
                    time.sleep(0.000001)
                    timeout += 1
                    if timeout > 100:
                        raise TimeoutError("DHT22 response timeout")
                
                timeout = 0
                while GPIO.input(self.pin) == GPIO.HIGH:
                    time.sleep(0.000001)
                    timeout += 1
                    if timeout > 100:
                        raise TimeoutError("DHT22 response timeout")
                
                # Read 40 bits of data
                data = []
                for i in range(40):
                    # Wait for start of bit
                    timeout = 0
                    while GPIO.input(self.pin) == GPIO.LOW:
                        time.sleep(0.000001)
                        timeout += 1
                        if timeout > 100:
                            raise TimeoutError("Bit start timeout")
                    
                    # Measure high time
                    start_time = time.time()
                    timeout = 0
                    while GPIO.input(self.pin) == GPIO.HIGH:
                        time.sleep(0.000001)
                        timeout += 1
                        if timeout > 100:
                            raise TimeoutError("Bit high timeout")
                    
                    duration = time.time() - start_time
                    data.append(1 if duration > 0.00005 else 0)  # 50μs threshold
                
                # Convert to bytes
                bytes_data = []
                for i in range(5):
                    byte = 0
                    for j in range(8):
                        byte |= (data[i * 8 + j] << (7 - j))
                    bytes_data.append(byte)
                
                # Verify checksum
                checksum = sum(bytes_data[:4]) & 0xFF
                if checksum != bytes_data[4]:
                    logger.warning(f"Checksum error: {checksum} != {bytes_data[4]}")
                    continue
                
                # Convert to temperature and humidity
                humidity = (bytes_data[0] << 8 | bytes_data[1]) / 10.0
                temperature = ((bytes_data[2] & 0x7F) << 8 | bytes_data[3]) / 10.0
                
                # Handle negative temperature
                if bytes_data[2] & 0x80:
                    temperature = -temperature
                
                # Validate ranges
                if not (0 <= humidity <= 100) or not (-40 <= temperature <= 80):
                    logger.warning(f"Invalid readings: temp={temperature}, humidity={humidity}")
                    continue
                
                logger.info(f"Temperature: {temperature}°C, Humidity: {humidity}%")
                return temperature, humidity
                
            except Exception as e:
                logger.warning(f"Attempt {attempt + 1} failed: {e}")
                if attempt < self.retry_count - 1:
                    time.sleep(self.delay)
                else:
                    logger.error("All attempts failed")
                    return None
            finally:
                # Reset pin
                GPIO.setup(self.pin, GPIO.OUT)
                GPIO.output(self.pin, GPIO.HIGH)
        
        return None
    
    def read_temperature(self) -> Optional[float]:
        """
        Read only temperature
        
        Returns:
            Optional[float]: Temperature in Celsius or None if error
        """
        result = self.read()
        return result[0] if result else None
    
    def read_humidity(self) -> Optional[float]:
        """
        Read only humidity
        
        Returns:
            Optional[float]: Humidity percentage or None if error
        """
        result = self.read()
        return result[1] if result else None