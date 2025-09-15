#!/bin/bash

# Raspberry Pi Project Setup Script
# This script sets up the environment for the Raspberry Pi project

echo "🍓 Raspberry Pi Project Setup"
echo "============================="

# Check if running on Raspberry Pi
if ! grep -q "Raspberry Pi" /proc/cpuinfo 2>/dev/null; then
    echo "⚠️  Warning: This doesn't appear to be a Raspberry Pi"
    echo "   Some features may not work on other systems"
fi

# Create necessary directories
echo "📁 Creating directories..."
mkdir -p logs
mkdir -p data
mkdir -p tests

# Set permissions for GPIO access
echo "🔧 Setting up GPIO permissions..."
if groups $USER | grep -q gpio; then
    echo "✓ User already in gpio group"
else
    echo "Adding user to gpio group..."
    sudo usermod -a -G gpio $USER
    echo "⚠️  You may need to log out and back in for GPIO permissions to take effect"
fi

# Install system dependencies
echo "📦 Installing system dependencies..."
sudo apt-get update
sudo apt-get install -y python3-pip python3-dev python3-venv
sudo apt-get install -y i2c-tools spi-tools
sudo apt-get install -y git

# Enable I2C and SPI if not already enabled
echo "⚙️  Enabling I2C and SPI interfaces..."
if ! grep -q "dtparam=i2c_arm=on" /boot/config.txt; then
    echo "dtparam=i2c_arm=on" | sudo tee -a /boot/config.txt
fi

if ! grep -q "dtparam=spi=on" /boot/config.txt; then
    echo "dtparam=spi=on" | sudo tee -a /boot/config.txt
fi

# Create virtual environment
echo "🐍 Creating Python virtual environment..."
python3 -m venv venv
source venv/bin/activate

# Install Python dependencies
echo "📚 Installing Python dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

# Create .env file if it doesn't exist
if [ ! -f .env ]; then
    echo "📝 Creating .env file..."
    cat > .env << EOF
# Raspberry Pi Project Environment Variables
DEBUG=False
LOG_LEVEL=INFO
DATABASE_URL=sqlite:///data/sensor_data.db
EOF
fi

# Set up log rotation
echo "📋 Setting up log rotation..."
sudo tee /etc/logrotate.d/raspberry-pi-project > /dev/null << EOF
$(pwd)/logs/*.log {
    daily
    missingok
    rotate 7
    compress
    notifempty
    create 644 $USER $USER
}
EOF

# Make scripts executable
echo "🔨 Making scripts executable..."
chmod +x scripts/*.sh
chmod +x examples/*.py

# Create systemd service file (optional)
echo "🔧 Creating systemd service file..."
sudo tee /etc/systemd/system/raspberry-pi-project.service > /dev/null << EOF
[Unit]
Description=Raspberry Pi Project Web Server
After=network.target

[Service]
Type=simple
User=$USER
WorkingDirectory=$(pwd)
Environment=PATH=$(pwd)/venv/bin
ExecStart=$(pwd)/venv/bin/python examples/web_server.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

echo ""
echo "✅ Setup completed successfully!"
echo ""
echo "Next steps:"
echo "1. Activate the virtual environment: source venv/bin/activate"
echo "2. Test basic GPIO: python examples/basic_gpio.py"
echo "3. Test sensors: python examples/sensor_reading.py"
echo "4. Start web server: python examples/web_server.py"
echo ""
echo "Optional:"
echo "- Enable the service: sudo systemctl enable raspberry-pi-project"
echo "- Start the service: sudo systemctl start raspberry-pi-project"
echo "- Check service status: sudo systemctl status raspberry-pi-project"
echo ""
echo "⚠️  Note: You may need to reboot for all changes to take effect"