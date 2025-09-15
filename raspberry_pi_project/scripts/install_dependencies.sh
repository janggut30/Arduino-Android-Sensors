#!/bin/bash

# Install Dependencies Script
# Installs additional dependencies for specific Raspberry Pi features

echo "📦 Installing Additional Dependencies"
echo "====================================="

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "❌ Virtual environment not found. Run setup.sh first."
    exit 1
fi

# Activate virtual environment
source venv/bin/activate

echo "🔧 Installing camera dependencies..."
pip install picamera

echo "🔧 Installing audio dependencies..."
pip install pyaudio

echo "🔧 Installing computer vision dependencies..."
pip install opencv-python pillow

echo "🔧 Installing I2C/SPI dependencies..."
pip install smbus2 spidev

echo "🔧 Installing additional sensor libraries..."
pip install adafruit-circuitpython-dht
pip install adafruit-circuitpython-mcp9808

echo "🔧 Installing development tools..."
pip install pytest pytest-cov
pip install black flake8

echo "🔧 Installing web framework dependencies..."
pip install flask flask-cors

echo "🔧 Installing data processing libraries..."
pip install numpy pandas

echo "🔧 Installing utility libraries..."
pip install python-dotenv schedule

echo ""
echo "✅ Additional dependencies installed successfully!"
echo ""
echo "You can now use:"
echo "- Camera: from picamera import PiCamera"
echo "- Audio: import pyaudio"
echo "- Computer Vision: import cv2"
echo "- I2C/SPI: import smbus2, spidev"
echo "- More sensors: from adafruit_circuitpython_dht import DHT22"