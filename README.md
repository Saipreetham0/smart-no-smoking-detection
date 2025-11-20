# Smart No-Smoking Detection System

A real-time cigarette and smoke detection system for Raspberry Pi with SH1106 OLED display, web interface, and multi-modal detection capabilities.

## Features

- **Multi-Modal Detection**: Combines visual cigarette detection, motion detection, and MQ-135 smoke sensor
- **Real-Time Monitoring**: Live camera feed with detection overlays
- **OLED Display**: SH1106 128x64 display showing system status, alerts, and web access info
- **Web Interface**: Remote monitoring via Flask web server with live video stream
- **Auto-Start**: Systemd service for automatic startup on boot
- **Violation Logging**: Automatic capture and storage of violation images with timestamps
- **Smart Alerts**: Configurable cooldown period to prevent alert spam

## Hardware Requirements

### Essential Components
- Raspberry Pi Zero 2 W (or any Raspberry Pi with camera support)
- Raspberry Pi Camera Module (V2 or HQ recommended)
- SH1106 OLED Display (128x64, I2C interface)
- MQ-135 Air Quality/Smoke Sensor (optional but recommended)
- 5V 2.5A Power Supply
- MicroSD Card (16GB+ recommended, Class 10)

### GPIO Connections

```
SH1106 OLED Display (I2C):
├── VCC  → Pin 1  (3.3V)
├── GND  → Pin 6  (Ground)
├── SCL  → Pin 5  (GPIO 3 - SCL)
└── SDA  → Pin 3  (GPIO 2 - SDA)

MQ-135 Smoke Sensor:
├── VCC  → Pin 2  (5V)
├── GND  → Pin 9  (Ground)
└── DOUT → Pin 11 (GPIO 17)
```

## Quick Start

### 1. System Prerequisites

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install system dependencies
sudo apt install -y python3-pip python3-venv git i2c-tools
sudo apt install -y libatlas-base-dev libhdf5-dev libhdf5-serial-dev
sudo apt install -y libjasper-dev libqtgui4 libqt4-test libcap-dev

# Enable camera and I2C
sudo raspi-config
# Navigate to: Interface Options → Camera → Enable
# Navigate to: Interface Options → I2C → Enable
# Reboot when prompted
```

### 2. Verify I2C Device

```bash
# Check if OLED is detected at address 0x3C
sudo i2cdetect -y 1
```

Expected output:
```
     0  1  2  3  4  5  6  7  8  9  a  b  c  d  e  f
00:          -- -- -- -- -- -- -- -- -- -- -- -- --
10: -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- --
20: -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- --
30: -- -- -- -- -- -- -- -- -- -- -- -- 3c -- -- --
40: -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- --
```

### 3. Installation

```bash
# Clone or download project files
cd ~
# (If you have the files locally, copy them to Raspberry Pi)

# Create virtual environment
python3 -m venv ~/smoke-env
source ~/smoke-env/bin/activate

# Install Python dependencies
pip install --upgrade pip
pip install -r requirements.txt

# Test the system
python smoking_detector_with_sh1106.py
```

### 4. Enable Auto-Start (Optional)

```bash
# Make installer executable
chmod +x install_autostart.sh

# Run auto-start installer
sudo bash install_autostart.sh

# Check service status
sudo systemctl status smoke-detector
```

## Usage

### Manual Operation

```bash
# Activate virtual environment
source ~/smoke-env/bin/activate

# Run the detection system
python smoking_detector_with_sh1106.py
```

The system will:
1. Initialize camera, OLED display, and sensors
2. Display system IP and port on OLED (e.g., `192.168.1.14:5000`)
3. Start web server for remote monitoring
4. Begin real-time detection

### Web Interface Access

Open a browser and navigate to:
```
http://<raspberry-pi-ip>:5000
```

Example: `http://192.168.1.14:5000`

### OLED Display Information

**Startup Screen:**
- System name
- IP:Port for web access
- "System Ready" status

**Monitoring Screen:**
- Current time
- Web access info (IP:5000)
- Detection status
- Alert count

**Alert Screen:**
- Large bell icon
- "ALERT!" message
- Current alert count

## Configuration

Edit `smoking_detector_with_sh1106.py` to customize settings:

```python
# Detection Settings (Lines 34-39)
ENABLE_SENSOR = False        # Enable/disable MQ-135 sensor
ENABLE_MOTION = True         # Enable/disable motion detection
ENABLE_VISUAL = True         # Enable/disable visual cigarette detection
ENABLE_OLED = True           # Enable/disable OLED display
DETECTION_CONFIDENCE = 0.5   # Detection sensitivity (0.0-1.0)

# Hardware Settings (Lines 29-32)
OLED_WIDTH = 128            # OLED display width
OLED_HEIGHT = 64            # OLED display height
OLED_ADDRESS = 0x3C         # I2C address of OLED

# Camera Settings (Lines 47-49)
CAMERA_WIDTH = 640          # Camera resolution width
CAMERA_HEIGHT = 480         # Camera resolution height
CAMERA_FPS = 10             # Frames per second

# Alert Settings (Line 1137)
alert_cooldown=30           # Seconds between alerts
```

## Service Management

```bash
# Start service
sudo systemctl start smoke-detector

# Stop service
sudo systemctl stop smoke-detector

# Restart service
sudo systemctl restart smoke-detector

# Check status
sudo systemctl status smoke-detector

# View logs
sudo journalctl -u smoke-detector -f

# Disable auto-start
sudo systemctl disable smoke-detector

# Re-enable auto-start
sudo systemctl enable smoke-detector
```

## File Structure

```
smoke/
├── smoking_detector_with_sh1106.py  # Main application
├── smoke-detector.service           # Systemd service file
├── install_autostart.sh             # Auto-start installer
├── requirements.txt                 # Python dependencies
├── README.md                        # This file
├── PROJECT_README.md                # Detailed documentation
├── AUTOSTART_GUIDE.md               # Auto-start setup guide
└── PROJECT_STRUCTURE.md             # File structure details
```

## Troubleshooting

### Camera Issues

**Problem**: `Failed to initialize camera`

```bash
# Check camera connection
vcgencmd get_camera

# Should output: supported=1 detected=1

# Enable camera interface
sudo raspi-config
# Interface Options → Camera → Enable
sudo reboot
```

### I2C/OLED Issues

**Problem**: OLED not detected or not working

```bash
# Install I2C tools
sudo apt install -y i2c-tools

# Check I2C devices
sudo i2cdetect -y 1

# If not detected, check connections and enable I2C
sudo raspi-config
# Interface Options → I2C → Enable
```

### Module Import Errors

**Problem**: `ModuleNotFoundError`

```bash
# Ensure virtual environment is activated
source ~/smoke-env/bin/activate

# Reinstall dependencies
pip install -r requirements.txt

# For OpenCV issues on older systems
sudo apt install python3-opencv
```

### Permission Errors

**Problem**: `Permission denied` for GPIO or camera

```bash
# Add user to required groups
sudo usermod -a -G video,gpio,i2c $USER

# Logout and login again for changes to take effect
```

### Service Not Starting

**Problem**: Auto-start service fails

```bash
# Check service logs
sudo journalctl -u smoke-detector -n 50

# Verify paths in service file
sudo nano /etc/systemd/system/smoke-detector.service

# Test script manually
source ~/smoke-env/bin/activate
python ~/smoking_detector_with_sh1106.py

# Reload systemd after changes
sudo systemctl daemon-reload
sudo systemctl restart smoke-detector
```

## Performance Optimization

### For Raspberry Pi Zero 2 W:

```python
# Reduce camera resolution (Line 47-48)
CAMERA_WIDTH = 320
CAMERA_HEIGHT = 240

# Lower frame rate (Line 49)
CAMERA_FPS = 5

# Increase detection interval (Line 1192)
time.sleep(0.2)  # Check every 200ms instead of 100ms
```

### Disable Unused Features:

```python
# If not using smoke sensor
ENABLE_SENSOR = False

# If not using motion detection
ENABLE_MOTION = False

# If not using OLED display
ENABLE_OLED = False
```

## API Endpoints

The web interface provides these endpoints:

- `GET /` - Main dashboard with live video feed
- `GET /video_feed` - MJPEG video stream
- `GET /status` - JSON status information
- `GET /violations` - List of violation images
- `GET /violations/<filename>` - View specific violation image

## Detection Algorithm

The system uses a three-stage detection approach:

1. **Visual Detection**: HSV color space analysis to detect orange/red cigarette tips and white cigarette bodies
2. **Motion Detection**: Frame differencing to identify movement in the monitored area
3. **Smoke Sensor**: MQ-135 sensor for detecting smoke particles in the air

All three methods work together with configurable thresholds for reliable detection.

## Safety and Privacy

- All processing occurs locally on the Raspberry Pi
- No data is sent to external servers
- Violation images are stored locally in the `violations/` directory
- Web interface is accessible only on the local network (not exposed to internet)

## Contributing

For bug reports, feature requests, or contributions, please contact the project maintainer.

## License

This project is provided as-is for educational and safety purposes.

## Support

For detailed documentation, see:
- [PROJECT_README.md](PROJECT_README.md) - Complete technical documentation
- [AUTOSTART_GUIDE.md](AUTOSTART_GUIDE.md) - Auto-start configuration
- [PROJECT_STRUCTURE.md](PROJECT_STRUCTURE.md) - Detailed file structure

---

**Version**: 1.0
**Last Updated**: November 2024
**Compatible With**: Raspberry Pi Zero 2 W, Raspberry Pi 3/4/5
