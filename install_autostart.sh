#!/bin/bash
# Installation script for No-Smoking Detection System Auto-Start

echo "=================================================="
echo "  No-Smoking Detection System - Auto-Start Setup"
echo "=================================================="
echo ""

# Check if running as root
if [ "$EUID" -eq 0 ]; then
   echo "❌ Please do not run as root (don't use sudo)"
   echo "   Run: bash install_autostart.sh"
   exit 1
fi

# Define paths
SCRIPT_PATH="/home/raspberrypi/smoking_detector_with_sh1106.py"
SERVICE_FILE="/home/raspberrypi/smoke-detector.service"
VENV_PATH="/home/raspberrypi/smoke-env"

echo "Step 1: Checking if script exists..."
if [ ! -f "$SCRIPT_PATH" ]; then
    echo "❌ Script not found at $SCRIPT_PATH"
    echo "   Please ensure smoking_detector_with_sh1106.py is in /home/raspberrypi/"
    exit 1
fi
echo "✓ Script found"

echo ""
echo "Step 2: Checking virtual environment..."
if [ ! -d "$VENV_PATH" ]; then
    echo "❌ Virtual environment not found at $VENV_PATH"
    echo "   Please create it first with: python3 -m venv ~/smoke-env"
    exit 1
fi
echo "✓ Virtual environment found"

echo ""
echo "Step 3: Checking service file..."
if [ ! -f "$SERVICE_FILE" ]; then
    echo "❌ Service file not found at $SERVICE_FILE"
    echo "   Please ensure smoke-detector.service is in /home/raspberrypi/"
    exit 1
fi
echo "✓ Service file found"

echo ""
echo "Step 4: Installing systemd service..."
sudo cp "$SERVICE_FILE" /etc/systemd/system/smoke-detector.service
sudo chmod 644 /etc/systemd/system/smoke-detector.service
echo "✓ Service file copied to /etc/systemd/system/"

echo ""
echo "Step 5: Reloading systemd daemon..."
sudo systemctl daemon-reload
echo "✓ Daemon reloaded"

echo ""
echo "Step 6: Enabling service to start on boot..."
sudo systemctl enable smoke-detector.service
echo "✓ Service enabled"

echo ""
echo "Step 7: Starting service now..."
sudo systemctl start smoke-detector.service
echo "✓ Service started"

echo ""
echo "=================================================="
echo "✅ Installation Complete!"
echo "=================================================="
echo ""
echo "The smoke detection system will now:"
echo "  ✓ Start automatically on boot"
echo "  ✓ Restart automatically if it crashes"
echo "  ✓ Run in the background"
echo ""
echo "Useful commands:"
echo "  Check status:   sudo systemctl status smoke-detector.service"
echo "  View logs:      sudo journalctl -u smoke-detector.service -f"
echo "  Stop service:   sudo systemctl stop smoke-detector.service"
echo "  Start service:  sudo systemctl start smoke-detector.service"
echo "  Restart:        sudo systemctl restart smoke-detector.service"
echo "  Disable:        sudo systemctl disable smoke-detector.service"
echo ""
echo "To check if it's running, open a browser and go to:"
echo "  http://$(hostname -I | cut -d' ' -f1):5000"
echo ""
