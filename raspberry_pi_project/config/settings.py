"""
Configuration settings for Raspberry Pi project
"""

import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# GPIO Pin Configuration
GPIO_PINS = {
    'LED_RED': 18,
    'LED_GREEN': 23,
    'LED_BLUE': 24,
    'BUTTON': 25,
    'DHT22_DATA': 4,
    'PIR_SENSOR': 17,
    'SERVO_PWM': 12,
    'BUZZER': 16
}

# Sensor Configuration
SENSOR_CONFIG = {
    'DHT22': {
        'pin': GPIO_PINS['DHT22_DATA'],
        'retry_count': 3,
        'delay': 2
    },
    'PIR': {
        'pin': GPIO_PINS['PIR_SENSOR'],
        'warmup_time': 10
    }
}

# Web Server Configuration
WEB_CONFIG = {
    'host': '0.0.0.0',
    'port': 5000,
    'debug': True
}

# Database Configuration
DATABASE_CONFIG = {
    'path': 'data/sensor_data.db',
    'backup_interval': 3600  # seconds
}

# Logging Configuration
LOGGING_CONFIG = {
    'level': 'INFO',
    'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    'file': 'logs/raspberry_pi.log'
}

# API Configuration
API_CONFIG = {
    'version': 'v1',
    'prefix': '/api'
}

# Environment Variables
ENV_VARS = {
    'DEBUG': os.getenv('DEBUG', 'False').lower() == 'true',
    'LOG_LEVEL': os.getenv('LOG_LEVEL', 'INFO'),
    'DATABASE_URL': os.getenv('DATABASE_URL', 'sqlite:///data/sensor_data.db')
}