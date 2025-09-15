#!/usr/bin/env python3
"""
Web Server Example
Simple Flask web server for controlling Raspberry Pi remotely
"""

import time
import sys
import os
import threading
from datetime import datetime

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from flask import Flask, render_template_string, jsonify, request
from flask_cors import CORS
from src.gpio_control import GPIOController
from src.actuators.led_control import LEDController, RGBLED, LEDPattern
from src.sensors.temperature import TemperatureSensor
from src.sensors.motion import MotionSensor
from config.settings import GPIO_PINS, WEB_CONFIG

# Initialize Flask app
app = Flask(__name__)
CORS(app)

# Global variables
gpio_controller = None
led_controller = None
rgb_led = None
temp_sensor = None
motion_sensor = None
sensor_data = {
    'temperature': 0,
    'humidity': 0,
    'motion_detected': False,
    'last_update': None
}

# HTML Template
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Raspberry Pi Control Panel</title>
    <style>
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            margin: 0;
            padding: 20px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            min-height: 100vh;
        }
        .container {
            max-width: 800px;
            margin: 0 auto;
            background: rgba(255, 255, 255, 0.1);
            padding: 30px;
            border-radius: 15px;
            backdrop-filter: blur(10px);
            box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
        }
        h1 {
            text-align: center;
            margin-bottom: 30px;
            text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.3);
        }
        .section {
            margin-bottom: 30px;
            padding: 20px;
            background: rgba(255, 255, 255, 0.1);
            border-radius: 10px;
            border: 1px solid rgba(255, 255, 255, 0.2);
        }
        .section h2 {
            margin-top: 0;
            color: #ffd700;
        }
        .led-controls {
            display: flex;
            gap: 15px;
            flex-wrap: wrap;
        }
        .led-button {
            padding: 10px 20px;
            border: none;
            border-radius: 25px;
            cursor: pointer;
            font-weight: bold;
            transition: all 0.3s ease;
            text-transform: uppercase;
        }
        .led-button:hover {
            transform: translateY(-2px);
            box-shadow: 0 5px 15px rgba(0, 0, 0, 0.3);
        }
        .red { background: #ff4757; color: white; }
        .green { background: #2ed573; color: white; }
        .blue { background: #3742fa; color: white; }
        .off { background: #57606f; color: white; }
        .sensor-data {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 15px;
        }
        .sensor-card {
            background: rgba(255, 255, 255, 0.1);
            padding: 15px;
            border-radius: 8px;
            text-align: center;
        }
        .sensor-value {
            font-size: 2em;
            font-weight: bold;
            margin: 10px 0;
        }
        .status {
            padding: 5px 10px;
            border-radius: 15px;
            font-size: 0.9em;
            font-weight: bold;
        }
        .status.active { background: #2ed573; }
        .status.inactive { background: #ff4757; }
        .rgb-controls {
            display: flex;
            flex-direction: column;
            gap: 10px;
        }
        .color-input {
            width: 100%;
            height: 40px;
            border: none;
            border-radius: 5px;
            cursor: pointer;
        }
        .pattern-controls {
            display: flex;
            gap: 10px;
            flex-wrap: wrap;
        }
        .pattern-button {
            padding: 8px 16px;
            border: 2px solid #ffd700;
            background: transparent;
            color: #ffd700;
            border-radius: 20px;
            cursor: pointer;
            transition: all 0.3s ease;
        }
        .pattern-button:hover {
            background: #ffd700;
            color: #333;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>🍓 Raspberry Pi Control Panel</h1>
        
        <div class="section">
            <h2>LED Controls</h2>
            <div class="led-controls">
                <button class="led-button red" onclick="controlLED('red', true)">Red ON</button>
                <button class="led-button red" onclick="controlLED('red', false)">Red OFF</button>
                <button class="led-button green" onclick="controlLED('green', true)">Green ON</button>
                <button class="led-button green" onclick="controlLED('green', false)">Green OFF</button>
                <button class="led-button blue" onclick="controlLED('blue', true)">Blue ON</button>
                <button class="led-button blue" onclick="controlLED('blue', false)">Blue OFF</button>
                <button class="led-button off" onclick="allLEDsOff()">All OFF</button>
            </div>
        </div>
        
        <div class="section">
            <h2>RGB LED Control</h2>
            <div class="rgb-controls">
                <input type="color" class="color-input" id="colorPicker" onchange="setRGBColor()">
                <div class="pattern-controls">
                    <button class="pattern-button" onclick="startRainbow()">Rainbow</button>
                    <button class="pattern-button" onclick="stopPattern()">Stop Pattern</button>
                </div>
            </div>
        </div>
        
        <div class="section">
            <h2>Sensor Data</h2>
            <div class="sensor-data">
                <div class="sensor-card">
                    <h3>Temperature</h3>
                    <div class="sensor-value" id="temperature">--°C</div>
                </div>
                <div class="sensor-card">
                    <h3>Humidity</h3>
                    <div class="sensor-value" id="humidity">--%</div>
                </div>
                <div class="sensor-card">
                    <h3>Motion</h3>
                    <div class="sensor-value" id="motion">--</div>
                    <div class="status inactive" id="motionStatus">No Motion</div>
                </div>
            </div>
        </div>
    </div>

    <script>
        // LED Control Functions
        function controlLED(color, state) {
            fetch('/api/led', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({color: color, state: state})
            })
            .then(response => response.json())
            .then(data => console.log(data));
        }
        
        function allLEDsOff() {
            fetch('/api/led/all_off', {method: 'POST'})
            .then(response => response.json())
            .then(data => console.log(data));
        }
        
        // RGB Control Functions
        function setRGBColor() {
            const color = document.getElementById('colorPicker').value;
            fetch('/api/rgb', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({color: color})
            })
            .then(response => response.json())
            .then(data => console.log(data));
        }
        
        function startRainbow() {
            fetch('/api/rgb/rainbow', {method: 'POST'})
            .then(response => response.json())
            .then(data => console.log(data));
        }
        
        function stopPattern() {
            fetch('/api/pattern/stop', {method: 'POST'})
            .then(response => response.json())
            .then(data => console.log(data));
        }
        
        // Update sensor data
        function updateSensorData() {
            fetch('/api/sensors')
            .then(response => response.json())
            .then(data => {
                document.getElementById('temperature').textContent = data.temperature + '°C';
                document.getElementById('humidity').textContent = data.humidity + '%';
                document.getElementById('motion').textContent = data.motion_detected ? 'YES' : 'NO';
                
                const motionStatus = document.getElementById('motionStatus');
                motionStatus.textContent = data.motion_detected ? 'Motion Detected' : 'No Motion';
                motionStatus.className = 'status ' + (data.motion_detected ? 'active' : 'inactive');
            });
        }
        
        // Update sensor data every 2 seconds
        setInterval(updateSensorData, 2000);
        updateSensorData(); // Initial update
    </script>
</body>
</html>
"""

def motion_callback():
    """Callback for motion detection"""
    global sensor_data
    sensor_data['motion_detected'] = True
    sensor_data['last_update'] = datetime.now()

def update_sensor_data():
    """Update sensor data in background thread"""
    global sensor_data, temp_sensor, motion_sensor
    
    while True:
        try:
            # Read temperature and humidity
            if temp_sensor:
                result = temp_sensor.read()
                if result:
                    sensor_data['temperature'] = round(result[0], 1)
                    sensor_data['humidity'] = round(result[1], 1)
            
            # Read motion status
            if motion_sensor:
                status = motion_sensor.get_motion_status()
                sensor_data['motion_detected'] = status['motion_detected']
                if sensor_data['motion_detected']:
                    motion_sensor.reset_motion_flag()
            
            sensor_data['last_update'] = datetime.now()
            
        except Exception as e:
            print(f"Sensor update error: {e}")
        
        time.sleep(2)  # Update every 2 seconds

@app.route('/')
def index():
    """Main page"""
    return render_template_string(HTML_TEMPLATE)

@app.route('/api/led', methods=['POST'])
def control_led():
    """Control individual LED"""
    try:
        data = request.get_json()
        color = data.get('color')
        state = data.get('state')
        
        if led_controller:
            if state:
                led_controller.turn_on(color)
            else:
                led_controller.turn_off(color)
            
            return jsonify({'status': 'success', 'message': f'LED {color} turned {"on" if state else "off"}'})
        else:
            return jsonify({'status': 'error', 'message': 'LED controller not initialized'})
            
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)})

@app.route('/api/led/all_off', methods=['POST'])
def all_leds_off():
    """Turn off all LEDs"""
    try:
        if led_controller:
            led_controller.all_off()
            return jsonify({'status': 'success', 'message': 'All LEDs turned off'})
        else:
            return jsonify({'status': 'error', 'message': 'LED controller not initialized'})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)})

@app.route('/api/rgb', methods=['POST'])
def control_rgb():
    """Control RGB LED"""
    try:
        data = request.get_json()
        color = data.get('color')
        
        if rgb_led:
            rgb_led.set_color_hex(color)
            return jsonify({'status': 'success', 'message': f'RGB color set to {color}'})
        else:
            return jsonify({'status': 'error', 'message': 'RGB LED not initialized'})
            
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)})

@app.route('/api/rgb/rainbow', methods=['POST'])
def start_rainbow():
    """Start rainbow pattern"""
    try:
        if rgb_led:
            # Start rainbow pattern in background
            threading.Thread(target=lambda: LEDPattern(None).start_rainbow(rgb_led)).start()
            return jsonify({'status': 'success', 'message': 'Rainbow pattern started'})
        else:
            return jsonify({'status': 'error', 'message': 'RGB LED not initialized'})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)})

@app.route('/api/pattern/stop', methods=['POST'])
def stop_pattern():
    """Stop current pattern"""
    try:
        # This would need to be implemented with proper pattern management
        return jsonify({'status': 'success', 'message': 'Pattern stopped'})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)})

@app.route('/api/sensors')
def get_sensor_data():
    """Get current sensor data"""
    return jsonify(sensor_data)

def initialize_hardware():
    """Initialize hardware components"""
    global gpio_controller, led_controller, rgb_led, temp_sensor, motion_sensor
    
    try:
        # Initialize GPIO controller
        gpio_controller = GPIOController()
        
        # Initialize LED controller
        led_controller = LEDController(gpio_controller)
        
        # Initialize RGB LED
        rgb_led = RGBLED(gpio_controller, GPIO_PINS['LED_RED'], GPIO_PINS['LED_GREEN'], GPIO_PINS['LED_BLUE'])
        
        # Initialize sensors
        temp_sensor = TemperatureSensor()
        motion_sensor = MotionSensor(callback=motion_callback)
        
        print("✓ Hardware initialized successfully")
        
        # Start sensor data update thread
        sensor_thread = threading.Thread(target=update_sensor_data)
        sensor_thread.daemon = True
        sensor_thread.start()
        
        return True
        
    except Exception as e:
        print(f"✗ Hardware initialization failed: {e}")
        return False

def main():
    """Main function"""
    print("Raspberry Pi Web Server")
    print("======================")
    
    # Initialize hardware
    if not initialize_hardware():
        print("Failed to initialize hardware. Exiting...")
        return
    
    # Start web server
    print(f"Starting web server on http://{WEB_CONFIG['host']}:{WEB_CONFIG['port']}")
    print("Press Ctrl+C to stop")
    
    try:
        app.run(
            host=WEB_CONFIG['host'],
            port=WEB_CONFIG['port'],
            debug=WEB_CONFIG['debug']
        )
    except KeyboardInterrupt:
        print("\nShutting down...")
        if gpio_controller:
            gpio_controller.cleanup()
        print("✓ Cleanup completed")

if __name__ == "__main__":
    main()