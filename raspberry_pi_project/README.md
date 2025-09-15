# Raspberry Pi Project

Project ini berisi berbagai contoh dan tools untuk development Raspberry Pi menggunakan Python.

## Struktur Project

```
raspberry_pi_project/
├── README.md
├── requirements.txt
├── config/
│   ├── __init__.py
│   └── settings.py
├── src/
│   ├── __init__.py
│   ├── gpio_control.py
│   ├── sensors/
│   │   ├── __init__.py
│   │   ├── temperature.py
│   │   ├── humidity.py
│   │   └── motion.py
│   ├── actuators/
│   │   ├── __init__.py
│   │   ├── led_control.py
│   │   └── servo_control.py
│   └── utils/
│       ├── __init__.py
│       └── logger.py
├── examples/
│   ├── basic_gpio.py
│   ├── sensor_reading.py
│   ├── led_blink.py
│   └── web_server.py
├── tests/
│   ├── __init__.py
│   └── test_gpio.py
└── scripts/
    ├── setup.sh
    └── install_dependencies.sh
```

## Instalasi

1. Clone atau download project ini
2. Jalankan setup script:
   ```bash
   chmod +x scripts/setup.sh
   ./scripts/setup.sh
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Penggunaan

### Basic GPIO Control
```python
from src.gpio_control import GPIOController

gpio = GPIOController()
gpio.setup_pin(18, 'out')  # LED pin
gpio.write_pin(18, True)   # Turn on LED
```

### Sensor Reading
```python
from src.sensors.temperature import TemperatureSensor

temp_sensor = TemperatureSensor()
temperature = temp_sensor.read()
print(f"Temperature: {temperature}°C")
```

## Hardware Requirements

- Raspberry Pi (3B+, 4B, atau Zero W)
- Breadboard
- Jumper wires
- LED dan resistor
- Sensor (DHT22, PIR, dll)
- Servo motor (opsional)

## Pin Configuration

| Component | GPIO Pin | Physical Pin |
|-----------|----------|--------------|
| LED Red   | 18       | 12           |
| LED Green | 23       | 16           |
| Button    | 24       | 18           |
| DHT22     | 4        | 7            |
| PIR       | 17       | 11           |

## Troubleshooting

1. **Permission denied**: Tambahkan user ke grup gpio:
   ```bash
   sudo usermod -a -G gpio $USER
   ```

2. **Module not found**: Pastikan semua dependencies terinstall:
   ```bash
   pip install -r requirements.txt
   ```

3. **GPIO error**: Pastikan script dijalankan dengan Python 3 dan GPIO library terinstall.

## License

MIT License - bebas digunakan untuk project pribadi maupun komersial.