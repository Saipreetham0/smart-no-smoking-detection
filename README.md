# 🚭 Smart No-Smoking Detection System

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.7+](https://img.shields.io/badge/python-3.7+-blue.svg)](https://www.python.org/downloads/)
[![Platform](https://img.shields.io/badge/platform-Raspberry%20Pi-red.svg)](https://www.raspberrypi.org/)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg)](CONTRIBUTING.md)

> A real-time AI-powered cigarette and smoke detection system for Raspberry Pi with OLED display, web interface, and multi-modal detection capabilities.

![Raspberry Pi](https://img.shields.io/badge/Raspberry%20Pi-Zero%202%20W%20%7C%203%20%7C%204%20%7C%205-C51A4A?style=flat&logo=raspberry-pi)
![OpenCV](https://img.shields.io/badge/OpenCV-4.5+-5C3EE8?style=flat&logo=opencv)
![Flask](https://img.shields.io/badge/Flask-2.0+-000000?style=flat&logo=flask)

---

## 🌟 Features

✨ **Multi-Modal Detection** - Combines visual cigarette detection, motion detection, and MQ-135 smoke sensor
📹 **Real-Time Monitoring** - Live camera feed with detection overlays and bounding boxes
📺 **OLED Display** - SH1106 128x64 display showing system status, alerts, and web access info
🌐 **Web Interface** - Remote monitoring via Flask web server with live MJPEG video stream
🚀 **Auto-Start** - Systemd service for automatic startup on boot
📸 **Violation Logging** - Automatic capture and storage of violation images with timestamps
⏱️ **Smart Alerts** - Configurable cooldown period to prevent alert spam
🔧 **Easy Configuration** - Simple Python-based configuration for all detection parameters

---

## 📋 Table of Contents

- [Demo](#-demo)
- [Hardware Requirements](#-hardware-requirements)
- [Quick Start](#-quick-start)
- [Usage](#-usage)
- [Configuration](#-configuration)
- [Web Interface](#-web-interface)
- [Detection Algorithm](#-detection-algorithm)
- [Troubleshooting](#-troubleshooting)
- [Contributing](#-contributing)
- [License](#-license)

---

## 🎬 Demo

### System Components
```
┌─────────────────────────────────────────────────┐
│  Raspberry Pi Camera → Computer Vision Engine  │
│         ↓                      ↓                │
│  Motion Detection      Visual Detection        │
│         ↓                      ↓                │
│         └──────────┬───────────┘                │
│                    ↓                            │
│            Detection System                     │
│                    ↓                            │
│      ┌─────────────┴─────────────┐              │
│      ↓                           ↓              │
│  OLED Display              Web Interface        │
│  (Local Status)          (Remote Monitoring)    │
└─────────────────────────────────────────────────┘
```

### OLED Display Screens
- **Startup**: Shows system IP:5000 for web access
- **Monitoring**: Real-time status with alert count
- **Alert Mode**: Visual and bell icon notification

### Web Dashboard
Access your detection system from any device on your network at `http://<pi-ip>:5000`

---

## 🛠️ Hardware Requirements

### Essential Components

| Component | Specification | Purpose |
|-----------|--------------|---------|
| **Raspberry Pi** | Zero 2 W / 3 / 4 / 5 | Main controller |
| **Camera Module** | V2 or HQ Camera | Visual detection |
| **OLED Display** | SH1106 128x64 I2C | Status display |
| **Smoke Sensor** | MQ-135 (optional) | Air quality sensing |
| **Power Supply** | 5V 2.5A+ | Power delivery |
| **MicroSD Card** | 16GB+ Class 10 | OS storage |

### 🔌 GPIO Pinout

```
┌─────────────────────────────────────────┐
│  SH1106 OLED Display (I2C)              │
│  ├── VCC  → Pin 1  (3.3V)               │
│  ├── GND  → Pin 6  (Ground)             │
│  ├── SCL  → Pin 5  (GPIO 3 - SCL)       │
│  └── SDA  → Pin 3  (GPIO 2 - SDA)       │
│                                         │
│  MQ-135 Smoke Sensor (Digital)          │
│  ├── VCC  → Pin 2  (5V)                 │
│  ├── GND  → Pin 9  (Ground)             │
│  └── DOUT → Pin 11 (GPIO 17)            │
└─────────────────────────────────────────┘
```

**Total Cost**: ~$50-80 USD (depending on Raspberry Pi model)

---

## 🚀 Quick Start

### 1️⃣ Clone the Repository

```bash
git clone https://github.com/Saipreetham0/smart-no-smoking-detection.git
cd smart-no-smoking-detection
```

### 2️⃣ System Prerequisites

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install dependencies
sudo apt install -y python3-pip python3-venv git i2c-tools
sudo apt install -y libatlas-base-dev libhdf5-dev libhdf5-serial-dev
sudo apt install -y libjasper-dev libqtgui4 libqt4-test libcap-dev

# Enable camera and I2C
sudo raspi-config
# Interface Options → Camera → Enable
# Interface Options → I2C → Enable
# Reboot when prompted
```

### 3️⃣ Verify Hardware

```bash
# Check camera
vcgencmd get_camera
# Expected: supported=1 detected=1

# Check OLED (should show device at 0x3C)
sudo i2cdetect -y 1
```

### 4️⃣ Installation

```bash
# Create virtual environment
python3 -m venv ~/smoke-env
source ~/smoke-env/bin/activate

# Install Python packages
pip install --upgrade pip
pip install -r requirements.txt
```

### 5️⃣ Run the System

```bash
# Test run
python smoking_detector_with_sh1106.py

# Enable auto-start on boot (optional)
chmod +x install_autostart.sh
sudo bash install_autostart.sh
```

🎉 **That's it!** Your system is now running. Check the OLED display for the web interface URL.

---

## 💻 Usage

### Manual Operation

```bash
# Activate environment
source ~/smoke-env/bin/activate

# Run detection system
python smoking_detector_with_sh1106.py
```

The system will:
1. ✅ Initialize camera, OLED display, and sensors
2. ✅ Display system IP:5000 on OLED screen
3. ✅ Start Flask web server at port 5000
4. ✅ Begin real-time cigarette detection

### Service Management

```bash
# Control the systemd service
sudo systemctl start smoke-detector    # Start
sudo systemctl stop smoke-detector     # Stop
sudo systemctl restart smoke-detector  # Restart
sudo systemctl status smoke-detector   # Check status

# View live logs
sudo journalctl -u smoke-detector -f
```

---

## ⚙️ Configuration

Edit `smoking_detector_with_sh1106.py` to customize:

```python
# Detection Settings (Lines 34-39)
ENABLE_SENSOR = False        # MQ-135 smoke sensor
ENABLE_MOTION = True         # Motion detection
ENABLE_VISUAL = True         # Visual cigarette detection
DETECTION_CONFIDENCE = 0.5   # Sensitivity (0.0-1.0)

# Camera Settings (Lines 47-49)
CAMERA_WIDTH = 640           # Resolution width
CAMERA_HEIGHT = 480          # Resolution height
CAMERA_FPS = 10              # Frames per second

# Alert Settings (Line 1137)
alert_cooldown=30            # Seconds between alerts
```

### Performance Tuning (for Pi Zero 2 W)

```python
# Lower resource usage
CAMERA_WIDTH = 320
CAMERA_HEIGHT = 240
CAMERA_FPS = 5
```

---

## 🌐 Web Interface

### Accessing the Dashboard

Open your browser and navigate to:
```
http://<raspberry-pi-ip>:5000
```

💡 **Tip**: The IP:Port is displayed on the OLED screen!

### Available Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | Main dashboard with live video |
| `/video_feed` | GET | MJPEG video stream |
| `/status` | GET | JSON status data |
| `/violations` | GET | List of violation images |
| `/violations/<file>` | GET | View specific violation |

### Example Status Response

```json
{
  "status": "monitoring",
  "violations": 5,
  "uptime": "2h 34m",
  "sensor_active": false,
  "motion_detected": true
}
```

---

## 🧠 Detection Algorithm

The system uses a **three-stage fusion approach**:

### 1. Visual Detection (Computer Vision)
- **HSV Color Space Analysis** to detect:
  - 🟠 Orange/red cigarette tips (thermal signature)
  - ⚪ White cylindrical cigarette bodies
- **Morphological Operations** for noise reduction
- **Proximity Checking** to ensure tip is near body
- **Shape Analysis** with aspect ratio filtering

### 2. Motion Detection
- **Frame Differencing** algorithm
- Identifies movement in monitored area
- Reduces false positives from static objects

### 3. Smoke Sensor (Optional)
- **MQ-135 Air Quality Sensor** integration
- Detects smoke particles in air
- Digital output via GPIO

All three methods are combined with configurable weights for maximum accuracy.

---

## 📁 Project Structure

```
smart-no-smoking-detection/
├── 📄 smoking_detector_with_sh1106.py  # Main application
├── ⚙️ smoke-detector.service           # Systemd service
├── 🔧 install_autostart.sh             # Auto-start installer
├── 📦 requirements.txt                 # Python dependencies
├── 📖 README.md                        # This file
├── 📚 PROJECT_README.md                # Detailed docs
├── 📋 AUTOSTART_GUIDE.md               # Auto-start guide
├── 📂 PROJECT_STRUCTURE.md             # File structure
├── 🤝 CONTRIBUTING.md                  # Contribution guide
├── ⚖️ LICENSE                          # MIT License
└── 🙈 .gitignore                       # Git ignore rules
```

---

## 🐛 Troubleshooting

<details>
<summary><b>Camera Not Working</b></summary>

```bash
# Check camera connection
vcgencmd get_camera
# Should show: supported=1 detected=1

# Enable camera interface
sudo raspi-config
# Interface Options → Camera → Enable
sudo reboot
```
</details>

<details>
<summary><b>OLED Display Not Detected</b></summary>

```bash
# Check I2C devices
sudo i2cdetect -y 1
# Should show device at 0x3C

# Enable I2C
sudo raspi-config
# Interface Options → I2C → Enable
sudo reboot
```
</details>

<details>
<summary><b>Module Import Errors</b></summary>

```bash
# Ensure virtual environment is activated
source ~/smoke-env/bin/activate

# Reinstall dependencies
pip install -r requirements.txt
```
</details>

<details>
<summary><b>Permission Denied Errors</b></summary>

```bash
# Add user to required groups
sudo usermod -a -G video,gpio,i2c $USER

# Logout and login for changes to take effect
```
</details>

For more troubleshooting, see [PROJECT_README.md](PROJECT_README.md).

---

## 🤝 Contributing

Contributions are welcome! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for details.

### How to Contribute

1. 🍴 Fork the repository
2. 🔨 Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. ✅ Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. 📤 Push to the branch (`git push origin feature/AmazingFeature`)
5. 🔃 Open a Pull Request

### Ideas for Contributions

- 🎯 Improved detection algorithms
- 📱 Mobile app for remote monitoring
- 📊 Analytics and reporting dashboard
- 🔔 Push notifications (email, SMS, Telegram)
- 🌍 Multi-language support
- 🎨 Enhanced web UI

---

## 📄 License

This project is licensed under the **MIT License** - see the [LICENSE](LICENSE) file for details.

```
Copyright (c) 2024 Smart No-Smoking Detection System
```

---

## 🙏 Acknowledgments

- **OpenCV** for computer vision capabilities
- **Raspberry Pi Foundation** for amazing hardware
- **Luma.OLED** library for display support
- **Flask** for web framework
- All contributors and supporters ⭐

---

## 📞 Support & Documentation

- 📚 [Complete Technical Documentation](PROJECT_README.md)
- 🚀 [Auto-Start Configuration Guide](AUTOSTART_GUIDE.md)
- 📂 [Project Structure Details](PROJECT_STRUCTURE.md)
- 🐛 [Report Issues](https://github.com/Saipreetham0/smart-no-smoking-detection/issues)
- 💬 [Discussions](https://github.com/Saipreetham0/smart-no-smoking-detection/discussions)

---

## ⭐ Show Your Support

If this project helped you, please give it a ⭐ star on GitHub!

**Share it with others who might find it useful!**

---

<div align="center">

**Made with ❤️ for a healthier environment**

[![GitHub stars](https://img.shields.io/github/stars/Saipreetham0/smart-no-smoking-detection?style=social)](https://github.com/Saipreetham0/smart-no-smoking-detection/stargazers)
[![GitHub forks](https://img.shields.io/github/forks/Saipreetham0/smart-no-smoking-detection?style=social)](https://github.com/Saipreetham0/smart-no-smoking-detection/network/members)

[⬆ Back to Top](#-smart-no-smoking-detection-system)

</div>
