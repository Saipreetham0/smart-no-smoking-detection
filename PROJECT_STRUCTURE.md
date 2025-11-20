# 📁 Smart No-Smoking Detection System - Project Structure

This document describes the complete file structure and organization of the project.

---

## 📂 Directory Structure

```
smoke-detector/
│
├── 📄 Core Application Files
│   ├── smoking_detector_with_sh1106.py     # Main detection system (SH1106 OLED)
│   ├── smoking_detector_with_lcd.py        # Alternative: 16x2 LCD version
│   └── smoking_detector_with_oled.py       # Alternative: SSD1306 OLED version
│
├── 🧪 Test & Diagnostic Scripts
│   ├── test_oled_i2c.py                    # OLED test (Adafruit library)
│   ├── test_oled_alternative.py            # OLED test (luma.oled library)
│   ├── test_oled_raw.py                    # OLED raw I2C communication test
│   └── test_lcd_i2c.py                     # LCD 16x2 test script
│
├── 🔧 System Configuration
│   ├── smoke-detector.service              # Systemd service file
│   ├── install_autostart.sh                # Auto-start installation script
│   └── requirements.txt                    # Python dependencies
│
├── 📚 Documentation
│   ├── PROJECT_README.md                   # Main project documentation
│   ├── README.md                           # Quick start guide
│   ├── AUTOSTART_GUIDE.md                 # Auto-start setup guide
│   └── PROJECT_STRUCTURE.md               # This file
│
├── 📦 AI Models (Optional)
│   ├── MobileNetSSD_deploy.prototxt       # Model architecture
│   └── MobileNetSSD_deploy.caffemodel     # Model weights
│
├── 📸 Runtime Data (Auto-created)
│   └── violations/                         # Violation images directory
│       ├── 20250120_143052.jpg
│       ├── 20250120_143125.jpg
│       └── ...
│
└── 📝 Additional Files
    ├── LICENSE                             # MIT License
    └── .gitignore                          # Git ignore rules
```

---

## 📄 File Descriptions

### Core Application Files

#### `smoking_detector_with_sh1106.py` (Main Application)
- **Purpose**: Primary detection system for SH1106 OLED displays
- **Size**: ~1200 lines
- **Dependencies**: luma.oled, OpenCV, Flask, picamera2
- **Features**:
  - Multi-modal detection (visual, motion, sensor)
  - SH1106 OLED display support
  - Web interface (Flask)
  - Automatic violation capture
  - Storage management

#### `smoking_detector_with_lcd.py`
- **Purpose**: Alternative version for 16x2 LCD displays
- **Display**: I2C LCD (16x2 or 20x4)
- **Library**: adafruit-circuitpython-charlcd
- **Use Case**: When using character LCD instead of OLED

#### `smoking_detector_with_oled.py`
- **Purpose**: Alternative version for SSD1306 OLED displays
- **Display**: 128x64 SSD1306 OLED
- **Library**: adafruit-circuitpython-ssd1306
- **Use Case**: When using Adafruit OLED libraries

### Test Scripts

#### `test_oled_i2c.py`
- **Purpose**: Test OLED display using Adafruit libraries
- **Tests**: 8 comprehensive tests
- **Features**:
  - I2C device scanning
  - Display initialization
  - Text rendering
  - Shapes and graphics
  - Scrolling animation
  - Contrast testing

#### `test_oled_alternative.py`
- **Purpose**: Test OLED using luma.oled library
- **Drivers**: SSD1306, SH1106, SSD1331
- **Features**:
  - Auto-detect OLED driver
  - 10 diagnostic tests
  - More stable for some displays

#### `test_oled_raw.py`
- **Purpose**: Direct I2C communication test
- **Level**: Low-level hardware access
- **Use Case**: When libraries don't work
- **Features**:
  - Direct SSD1306 commands
  - Pattern generation
  - Hardware debugging

#### `test_lcd_i2c.py`
- **Purpose**: Test 16x2/20x4 LCD displays
- **Tests**: 13 comprehensive tests
- **Features**:
  - Character display
  - Scrolling text
  - Backlight control
  - Interactive mode

### System Configuration

#### `smoke-detector.service`
- **Purpose**: Systemd service configuration
- **Type**: Unit file
- **Features**:
  - Auto-start on boot
  - Auto-restart on crash
  - Log to systemd journal
  - Proper environment setup

```ini
[Unit]
Description=No-Smoking Detection System with OLED Display
After=network.target

[Service]
Type=simple
User=raspberrypi
WorkingDirectory=/home/raspberrypi
Environment="PATH=/home/raspberrypi/smoke-env/bin:..."
ExecStart=/home/raspberrypi/smoke-env/bin/python ...
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

#### `install_autostart.sh`
- **Purpose**: Automated installation script
- **Type**: Bash script
- **Features**:
  - Verifies prerequisites
  - Installs systemd service
  - Enables auto-start
  - Provides status feedback

#### `requirements.txt`
- **Purpose**: Python package dependencies
- **Format**: pip requirements file
- **Usage**: `pip install -r requirements.txt`
- **Contents**:
  - OpenCV
  - NumPy
  - Flask
  - luma.oled
  - picamera2
  - RPi.GPIO

### Documentation

#### `PROJECT_README.md`
- **Purpose**: Complete project documentation
- **Sections**:
  - Features overview
  - Hardware requirements
  - Installation guide
  - Configuration options
  - Usage instructions
  - Troubleshooting
  - API documentation

#### `README.md` (Quick Start)
- **Purpose**: Quick installation and setup
- **Target**: Users who want to get started quickly
- **Length**: ~100 lines
- **Contents**:
  - Quick installation steps
  - Basic configuration
  - First run instructions

#### `AUTOSTART_GUIDE.md`
- **Purpose**: Detailed auto-start setup
- **Sections**:
  - Installation methods
  - Service management
  - Troubleshooting
  - Verification steps

#### `PROJECT_STRUCTURE.md`
- **Purpose**: This document
- **Contents**: File organization and descriptions

### AI Models (Optional)

#### `MobileNetSSD_deploy.prototxt`
- **Purpose**: Neural network architecture
- **Format**: Caffe model definition
- **Size**: ~30 KB
- **Usage**: Person detection (optional feature)

#### `MobileNetSSD_deploy.caffemodel`
- **Purpose**: Pre-trained weights
- **Format**: Caffe binary model
- **Size**: ~23 MB
- **Usage**: Person detection (optional feature)

Download with:
```bash
wget https://raw.githubusercontent.com/chuanqi305/MobileNet-SSD/master/MobileNetSSD_deploy.prototxt
wget https://github.com/chuanqi305/MobileNet-SSD/raw/master/MobileNetSSD_deploy.caffemodel
```

### Runtime Data

#### `violations/` Directory
- **Purpose**: Stores violation images
- **Created**: Automatically on first run
- **Format**: JPEG images
- **Naming**: `YYYYMMDD_HHMMSS.jpg`
- **Management**: Auto-cleanup based on limits
- **Limits**:
  - Max images: 150 (configurable)
  - Max storage: 300 MB (configurable)

---

## 🗂️ Code Organization

### Main Application Structure

```python
smoking_detector_with_sh1106.py
│
├── Configuration (Lines 1-39)
│   ├── GPIO pin definitions
│   ├── OLED settings
│   └── Detection parameters
│
├── OLEDDisplay Class (Lines 40-320)
│   ├── __init__()              # Initialize display
│   ├── show_monitoring()       # Normal status
│   ├── show_violation()        # Alert display
│   ├── show_no_smoking()       # Warning symbol
│   ├── show_system_ready()     # Startup screen
│   └── show_alert_count()      # Alert counter
│
├── SensorHandler Class (Lines 321-365)
│   ├── __init__()              # Setup MQ-135
│   ├── _warmup()               # Sensor calibration
│   ├── detect_smoke()          # Read sensor
│   └── get_status()            # Status string
│
├── AlertSystem Class (Lines 366-387)
│   ├── __init__()              # Setup buzzer/LEDs
│   ├── trigger_alert()         # Sound alarm
│   └── set_normal()            # Clear alarm
│
├── SmokingDetectionSystem Class (Lines 388-899)
│   ├── __init__()              # Initialize system
│   ├── load_models()           # Load AI models
│   ├── detect_person()         # AI person detection
│   ├── detect_motion()         # Frame diff motion
│   ├── detect_cigarette_visual()  # Visual cigarette
│   ├── detect_all()            # Combined detection
│   ├── save_violation()        # Save image
│   ├── cleanup_old_files()    # Storage management
│   ├── get_storage_info()     # Storage stats
│   ├── get_recent_violations()  # Violation list
│   ├── run_detection()         # Main loop
│   ├── _show_alert_briefly()   # Alert display
│   ├── get_frame()             # Video streaming
│   └── stop()                  # Cleanup
│
├── Flask Web Application (Lines 900-1100)
│   ├── HTML_TEMPLATE           # Web interface HTML
│   ├── generate_frames()       # Video stream
│   ├── @app.route('/')        # Dashboard
│   ├── @app.route('/video_feed')  # Video endpoint
│   ├── @app.route('/api/stats')   # Statistics API
│   ├── @app.route('/api/violations')  # Violations API
│   ├── @app.route('/violations/<file>')  # Image serving
│   └── start_web_server()      # Flask startup
│
└── Main Execution (Lines 1101-1162)
    ├── Display startup info
    ├── Get IP address
    ├── Initialize detector
    ├── Start detection thread
    └── Start web server
```

---

## 📊 File Sizes

| File | Lines | Size | Type |
|------|-------|------|------|
| smoking_detector_with_sh1106.py | ~1200 | ~45 KB | Python |
| smoking_detector_with_lcd.py | ~1000 | ~40 KB | Python |
| smoking_detector_with_oled.py | ~1100 | ~42 KB | Python |
| test_oled_i2c.py | ~200 | ~8 KB | Python |
| test_oled_alternative.py | ~150 | ~6 KB | Python |
| test_oled_raw.py | ~250 | ~10 KB | Python |
| test_lcd_i2c.py | ~300 | ~12 KB | Python |
| smoke-detector.service | ~20 | ~1 KB | INI |
| install_autostart.sh | ~100 | ~4 KB | Bash |
| requirements.txt | ~20 | ~1 KB | Text |
| PROJECT_README.md | ~1500 | ~60 KB | Markdown |
| AUTOSTART_GUIDE.md | ~500 | ~20 KB | Markdown |

**Total Project Size**: ~250 KB (excluding AI models and violation images)

---

## 🔄 Data Flow

```
┌──────────────┐
│   Camera     │
└──────┬───────┘
       │
       ▼
┌─────────────────────┐
│  Frame Capture      │
│  (picamera2)        │
└──────┬──────────────┘
       │
       ▼
┌─────────────────────┐
│  Detection Methods  │
│  ├─ Visual (OpenCV) │
│  ├─ Motion (Diff)   │
│  └─ Sensor (GPIO)   │
└──────┬──────────────┘
       │
       ▼
┌─────────────────────┐
│  Decision Logic     │
│  (threshold check)  │
└──────┬──────────────┘
       │
       ├─────────────┐
       │             │
       ▼             ▼
┌────────────┐  ┌──────────────┐
│  OLED      │  │  Save Image  │
│  Display   │  │  to disk     │
└────────────┘  └──────────────┘
       │             │
       ▼             ▼
┌────────────┐  ┌──────────────┐
│  Alerts    │  │  Web         │
│  (Buzzer)  │  │  Interface   │
└────────────┘  └──────────────┘
```

---

## 🚀 Deployment Files Checklist

### Minimum Required Files
- ✅ `smoking_detector_with_sh1106.py`
- ✅ `requirements.txt`
- ✅ `README.md` or `PROJECT_README.md`

### Recommended Files
- ✅ `smoke-detector.service`
- ✅ `install_autostart.sh`
- ✅ `AUTOSTART_GUIDE.md`
- ✅ `test_oled_i2c.py` or `test_oled_alternative.py`

### Optional Files
- ⚠️ `MobileNetSSD_deploy.prototxt`
- ⚠️ `MobileNetSSD_deploy.caffemodel`
- ⚠️ Alternative versions (LCD/OLED variants)
- ⚠️ Additional test scripts

---

## 📦 Packaging for Distribution

### Create Release Package

```bash
# Create distribution directory
mkdir smoke-detector-v1.0

# Copy essential files
cp smoking_detector_with_sh1106.py smoke-detector-v1.0/
cp requirements.txt smoke-detector-v1.0/
cp PROJECT_README.md smoke-detector-v1.0/README.md
cp AUTOSTART_GUIDE.md smoke-detector-v1.0/
cp smoke-detector.service smoke-detector-v1.0/
cp install_autostart.sh smoke-detector-v1.0/
cp test_oled_alternative.py smoke-detector-v1.0/

# Create archive
tar -czf smoke-detector-v1.0.tar.gz smoke-detector-v1.0/

# Or create ZIP
zip -r smoke-detector-v1.0.zip smoke-detector-v1.0/
```

### Installation from Package

```bash
# Extract
tar -xzf smoke-detector-v1.0.tar.gz
cd smoke-detector-v1.0/

# Install
python3 -m venv ~/smoke-env
source ~/smoke-env/bin/activate
pip install -r requirements.txt

# Setup auto-start
chmod +x install_autostart.sh
bash install_autostart.sh
```

---

## 🔧 Customization Points

### Where to Customize

1. **GPIO Pins** → Lines 23-26
2. **OLED Address** → Line 31
3. **Detection Settings** → Lines 34-39
4. **Storage Limits** → Lines 425-427
5. **Web Port** → Line 1161
6. **Camera Resolution** → Line 453
7. **Detection Thresholds** → Lines 385-450

---

## 📝 Version Control

### Git Repository Structure

```
.git/
.gitignore
README.md
LICENSE
src/
  ├── smoking_detector_with_sh1106.py
  ├── smoking_detector_with_lcd.py
  └── smoking_detector_with_oled.py
tests/
  ├── test_oled_i2c.py
  ├── test_oled_alternative.py
  ├── test_oled_raw.py
  └── test_lcd_i2c.py
config/
  ├── smoke-detector.service
  └── install_autostart.sh
docs/
  ├── PROJECT_README.md
  ├── AUTOSTART_GUIDE.md
  └── PROJECT_STRUCTURE.md
requirements.txt
```

### `.gitignore` Contents

```
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
env/
venv/
smoke-env/

# Runtime data
violations/
*.jpg
*.jpeg
*.png

# AI Models (large files)
*.caffemodel

# OS
.DS_Store
Thumbs.db

# IDE
.vscode/
.idea/
*.swp
*.swo
```

---

**This structure provides a clean, organized, and maintainable project layout for the Smart No-Smoking Detection System.**
