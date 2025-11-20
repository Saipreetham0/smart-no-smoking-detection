# 🚀 Auto-Start Setup Guide for Raspberry Pi

This guide will help you set up the smoking detection system to start automatically when your Raspberry Pi boots.

## 📋 Prerequisites

Before setting up auto-start, ensure:
- ✅ Script is working manually (`python smoking_detector_with_sh1106.py`)
- ✅ Virtual environment is set up at `~/smoke-env`
- ✅ All dependencies are installed
- ✅ OLED display is working

---

## 🔧 Installation Methods

### **Method 1: Automatic Installation (Recommended)**

Transfer all files to your Raspberry Pi:

```bash
# From your computer
scp /Users/koyyalasaipreetham/Downloads/smoke/smoking_detector_with_sh1106.py raspberrypi@192.168.1.14:~/
scp /Users/koyyalasaipreetham/Downloads/smoke/smoke-detector.service raspberrypi@192.168.1.14:~/
scp /Users/koyyalasaipreetham/Downloads/smoke/install_autostart.sh raspberrypi@192.168.1.14:~/
```

On your Raspberry Pi, run:

```bash
# Make installer executable
chmod +x install_autostart.sh

# Run the installer
bash install_autostart.sh
```

✅ **Done!** The system will now start on boot.

---

### **Method 2: Manual Installation**

If you prefer to set it up manually:

#### Step 1: Transfer Files

```bash
# Transfer service file
scp /Users/koyyalasaipreetham/Downloads/smoke/smoke-detector.service raspberrypi@192.168.1.14:~/

# Transfer main script (if not already done)
scp /Users/koyyalasaipreetham/Downloads/smoke/smoking_detector_with_sh1106.py raspberrypi@192.168.1.14:~/
```

#### Step 2: On Raspberry Pi

```bash
# Copy service file to systemd directory
sudo cp ~/smoke-detector.service /etc/systemd/system/

# Set correct permissions
sudo chmod 644 /etc/systemd/system/smoke-detector.service

# Reload systemd
sudo systemctl daemon-reload

# Enable service to start on boot
sudo systemctl enable smoke-detector.service

# Start service now
sudo systemctl start smoke-detector.service

# Check if it's running
sudo systemctl status smoke-detector.service
```

---

## 📊 Managing the Service

### Check Status
```bash
sudo systemctl status smoke-detector.service
```

### View Live Logs
```bash
sudo journalctl -u smoke-detector.service -f
```

### View Last 100 Lines of Logs
```bash
sudo journalctl -u smoke-detector.service -n 100
```

### Stop Service
```bash
sudo systemctl stop smoke-detector.service
```

### Start Service
```bash
sudo systemctl start smoke-detector.service
```

### Restart Service
```bash
sudo systemctl restart smoke-detector.service
```

### Disable Auto-Start (stop running on boot)
```bash
sudo systemctl disable smoke-detector.service
```

### Re-Enable Auto-Start
```bash
sudo systemctl enable smoke-detector.service
```

---

## 🔍 Troubleshooting

### Service Won't Start

```bash
# Check for errors in logs
sudo journalctl -u smoke-detector.service -n 50

# Common issues:
# 1. Virtual environment path wrong
# 2. Script path wrong
# 3. Python dependencies not installed
# 4. Camera/I2C permissions
```

### Check Service File Configuration

```bash
cat /etc/systemd/system/smoke-detector.service
```

Should show:
```ini
[Unit]
Description=No-Smoking Detection System with OLED Display
After=network.target

[Service]
Type=simple
User=raspberrypi
WorkingDirectory=/home/raspberrypi
Environment="PATH=/home/raspberrypi/smoke-env/bin:/usr/local/bin:/usr/bin:/bin"
ExecStart=/home/raspberrypi/smoke-env/bin/python /home/raspberrypi/smoking_detector_with_sh1106.py
Restart=always
RestartSec=10
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
```

### Fix Common Issues

**Issue: Permission denied for camera**
```bash
# Add user to video group
sudo usermod -a -G video raspberrypi

# Reboot
sudo reboot
```

**Issue: I2C permission denied**
```bash
# Add user to i2c group
sudo usermod -a -G i2c raspberrypi

# Reboot
sudo reboot
```

**Issue: Virtual environment not found**
```bash
# Recreate virtual environment
python3 -m venv ~/smoke-env

# Reinstall dependencies
source ~/smoke-env/bin/activate
pip install luma.oled opencv-python-headless numpy flask picamera2 RPi.GPIO
```

---

## 🔄 Updating the Script

When you update the Python script:

```bash
# Transfer new version
scp smoking_detector_with_sh1106.py raspberrypi@192.168.1.14:~/

# Restart service to use new version
sudo systemctl restart smoke-detector.service

# Check if it started successfully
sudo systemctl status smoke-detector.service
```

---

## 🗑️ Uninstalling Auto-Start

To remove the auto-start service:

```bash
# Stop the service
sudo systemctl stop smoke-detector.service

# Disable auto-start
sudo systemctl disable smoke-detector.service

# Remove service file
sudo rm /etc/systemd/system/smoke-detector.service

# Reload systemd
sudo systemctl daemon-reload
```

You can still run the script manually:
```bash
source ~/smoke-env/bin/activate
python ~/smoking_detector_with_sh1106.py
```

---

## ✅ Verify Installation

After installation, verify everything works:

### 1. Check Service Status
```bash
sudo systemctl status smoke-detector.service
```
Should show: **Active: active (running)**

### 2. Check OLED Display
- Should show startup screen
- Then monitoring screen with IP address

### 3. Check Web Interface
Open browser and go to: `http://192.168.1.14:5000`

### 4. Test Auto-Start
```bash
# Reboot the Pi
sudo reboot

# After reboot, check if service started
sudo systemctl status smoke-detector.service
```

---

## 📝 Boot Sequence

When Raspberry Pi boots:

1. **System starts** → Loads operating system
2. **Network ready** → Connects to WiFi/Ethernet
3. **Service starts** → `smoke-detector.service` launches
4. **OLED shows** → "SMOKE DETECTOR" startup screen
5. **System ready** → Shows monitoring screen with IP:5000
6. **Web interface** → Available at `http://<ip>:5000`

---

## 💡 Tips

1. **Check logs regularly** to ensure system is running smoothly
2. **Monitor storage** - service automatically cleans old violation images
3. **Update regularly** - transfer new scripts when you make improvements
4. **Backup configuration** - keep a copy of the service file
5. **Test after updates** - always check status after updating

---

## 🆘 Getting Help

If you encounter issues:

1. Check logs: `sudo journalctl -u smoke-detector.service -n 100`
2. Check service status: `sudo systemctl status smoke-detector.service`
3. Test manually: Stop service, run script manually to see errors
4. Check permissions: Ensure user has access to camera, GPIO, I2C

---

## 📊 Monitoring Performance

View real-time CPU and memory usage:

```bash
# Install htop if not available
sudo apt install htop

# Monitor system
htop

# Look for 'python' process running the detector
```

Check system logs:
```bash
# All system logs
sudo journalctl -f

# Only smoke detector logs
sudo journalctl -u smoke-detector.service -f
```

---

**Your smoking detection system is now set up to run automatically on boot!** 🎉
