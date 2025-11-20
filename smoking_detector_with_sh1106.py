#!/usr/bin/env python3
"""
Enhanced No-Smoking Detection System with SH1106 OLED Display
Combines: Motion Detection + MQ-135 Sensor + Visual Cigarette Detection + OLED Display
Optimized for Raspberry Pi Zero 2 W with SH1106 OLED (128x64)
Access via: http://<pi-ip-address>:5000
"""

import cv2
import numpy as np
from datetime import datetime
import os
import time
from picamera2 import Picamera2
import threading
import RPi.GPIO as GPIO
from flask import Flask, render_template_string, Response, jsonify, send_from_directory
from luma.core.interface.serial import i2c
from luma.oled.device import sh1106
from PIL import Image, ImageDraw, ImageFont

# ==================== GPIO CONFIGURATION ====================
MQ135_PIN = 17      # MQ-135 smoke sensor
BUZZER_PIN = 27     # Optional buzzer
LED_RED = 22        # Optional red LED
LED_GREEN = 23      # Optional green LED

# ==================== OLED CONFIGURATION ====================
OLED_ADDRESS = 0x3C  # Your working OLED address
OLED_WIDTH = 128
OLED_HEIGHT = 64

# ==================== DETECTION SETTINGS ====================
ENABLE_SENSOR = False             # Enable MQ-135 sensor (set True when sensor works)
ENABLE_MOTION = True              # Enable motion detection
ENABLE_VISUAL = True              # Enable visual cigarette detection (IMPROVED ALGORITHM)
ENABLE_OLED = True                # Enable OLED display
SENSOR_INVERTED = False           # Set True if sensor logic is backwards
DETECTION_CONFIDENCE = 0.5        # Visual detection threshold (0.1-0.9) - Balanced sensitivity

class OLEDDisplay:
    """SH1106 OLED Display Handler (using luma.oled)"""

    def __init__(self, address=OLED_ADDRESS):
        """Initialize I2C OLED display"""
        self.enabled = ENABLE_OLED
        self.device = None
        self.width = OLED_WIDTH
        self.height = OLED_HEIGHT

        if not self.enabled:
            print("⚠ OLED disabled in settings")
            return

        try:
            # Initialize I2C and SH1106 device
            serial = i2c(port=1, address=address)
            self.device = sh1106(serial)
            self.device.clear()

            print(f"✓ OLED Display initialized (SH1106 at 0x{address:02X})")

            # Load fonts
            try:
                self.font_large = ImageFont.truetype(
                    "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 18
                )
                self.font_normal = ImageFont.truetype(
                    "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 12
                )
                self.font_small = ImageFont.truetype(
                    "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 10
                )
            except:
                self.font_large = ImageFont.load_default()
                self.font_normal = ImageFont.load_default()
                self.font_small = ImageFont.load_default()

            # Show startup message
            self.show_startup()

        except Exception as e:
            print(f"⚠ OLED not found: {e}")
            print(f"   Check wiring and I2C address")
            self.device = None
            self.enabled = False

    def clear(self):
        """Clear display"""
        if not self.enabled or self.device is None:
            return
        try:
            self.device.clear()
        except:
            pass

    def show_text(self, lines, center=False, font=None):
        """Display multiple lines of text"""
        if not self.enabled or self.device is None:
            return
        try:
            if font is None:
                font = self.font_small

            # Create blank image
            image = Image.new("1", (self.width, self.height))
            draw = ImageDraw.Draw(image)

            y = 0
            line_height = 12

            for line in lines[:6]:  # Max 6 lines for 64px height
                if center:
                    bbox = draw.textbbox((0, 0), line, font=font)
                    text_width = bbox[2] - bbox[0]
                    x = (self.width - text_width) // 2
                else:
                    x = 0
                draw.text((x, y), line, font=font, fill=255)
                y += line_height

            self.device.display(image)
        except Exception as e:
            print(f"⚠ OLED error: {e}")

    def show_no_smoking(self):
        """Display NO SMOKING warning with graphic"""
        if not self.enabled or self.device is None:
            return
        try:
            image = Image.new("1", (self.width, self.height))
            draw = ImageDraw.Draw(image)

            # Draw "no smoking" symbol (circle with diagonal line)
            center_x, center_y = self.width // 2, 24
            radius = 18
            draw.ellipse((center_x - radius, center_y - radius,
                         center_x + radius, center_y + radius),
                        outline=255, fill=0)
            draw.line((center_x - radius + 5, center_y - radius + 5,
                      center_x + radius - 5, center_y + radius - 5),
                     fill=255, width=3)

            # Text
            text = "NO SMOKING"
            bbox = draw.textbbox((0, 0), text, font=self.font_normal)
            text_width = bbox[2] - bbox[0]
            x = (self.width - text_width) // 2
            draw.text((x, 48), text, font=self.font_normal, fill=255)

            self.device.display(image)
        except:
            pass

    def show_violation(self, detection_type=""):
        """Display violation detected"""
        if not self.enabled or self.device is None:
            return
        try:
            image = Image.new("1", (self.width, self.height))
            draw = ImageDraw.Draw(image)

            # Alert symbol (triangle with !)
            draw.polygon([(64, 5), (50, 25), (78, 25)], outline=255, fill=0)
            draw.text((60, 10), "!", font=self.font_large, fill=255)

            # Detection type
            y = 30
            if "CIGARETTE" in detection_type:
                lines = ["VIOLATION!", "Cigarette", "Detected!"]
            elif "SENSOR" in detection_type:
                lines = ["VIOLATION!", "Smoke", "Detected!"]
            elif "MOTION" in detection_type:
                lines = ["VIOLATION!", "Motion", "Detected!"]
            else:
                lines = ["VIOLATION!", "Detected!"]

            for line in lines:
                bbox = draw.textbbox((0, 0), line, font=self.font_normal)
                text_width = bbox[2] - bbox[0]
                x = (self.width - text_width) // 2
                draw.text((x, y), line, font=self.font_normal, fill=255)
                y += 12

            self.device.display(image)
        except:
            pass

    def show_monitoring(self, sensor_status="", violations=0, ip_address=""):
        """Display monitoring status with web port"""
        if not self.enabled or self.device is None:
            return
        try:
            image = Image.new("1", (self.width, self.height))
            draw = ImageDraw.Draw(image)

            timestamp = datetime.now().strftime('%H:%M:%S')

            # Header
            draw.text((0, 0), "MONITORING", font=self.font_normal, fill=255)
            draw.line((0, 14, self.width, 14), fill=255)

            # Web Access Info
            draw.text((0, 18), f"Web: {ip_address}:5000", font=self.font_small, fill=255)

            # Time
            draw.text((0, 30), f"Time: {timestamp}", font=self.font_small, fill=255)

            # Status
            if sensor_status and sensor_status != "DISABLED":
                draw.text((0, 42), f"Sensor: {sensor_status[:8]}", font=self.font_small, fill=255)
            else:
                draw.text((0, 42), "Status: OK", font=self.font_small, fill=255)

            # Violations
            draw.text((0, 54), f"Alerts: {violations}", font=self.font_small, fill=255)

            self.device.display(image)
        except:
            pass

    def show_startup(self):
        """Display startup message"""
        if not self.enabled or self.device is None:
            return
        try:
            image = Image.new("1", (self.width, self.height))
            draw = ImageDraw.Draw(image)

            # Logo/Title
            text1 = "SMOKE"
            text2 = "DETECTOR"

            bbox1 = draw.textbbox((0, 0), text1, font=self.font_large)
            text1_width = bbox1[2] - bbox1[0]
            x1 = (self.width - text1_width) // 2

            bbox2 = draw.textbbox((0, 0), text2, font=self.font_large)
            text2_width = bbox2[2] - bbox2[0]
            x2 = (self.width - text2_width) // 2

            draw.text((x1, 10), text1, font=self.font_large, fill=255)
            draw.text((x2, 30), text2, font=self.font_large, fill=255)

            # Status
            text3 = "Initializing..."
            bbox3 = draw.textbbox((0, 0), text3, font=self.font_small)
            text3_width = bbox3[2] - bbox3[0]
            x3 = (self.width - text3_width) // 2
            draw.text((x3, 52), text3, font=self.font_small, fill=255)

            self.device.display(image)
            time.sleep(2)
        except:
            pass

    def show_system_ready(self, ip_address=""):
        """Display system ready message with web access info"""
        if not self.enabled or self.device is None:
            return
        try:
            image = Image.new("1", (self.width, self.height))
            draw = ImageDraw.Draw(image)

            # Checkmark
            draw.line((60, 20, 65, 28), fill=255, width=2)
            draw.line((65, 28, 75, 15), fill=255, width=2)

            # Text
            text1 = "SYSTEM READY"
            bbox1 = draw.textbbox((0, 0), text1, font=self.font_normal)
            text1_width = bbox1[2] - bbox1[0]
            x1 = (self.width - text1_width) // 2
            draw.text((x1, 38), text1, font=self.font_normal, fill=255)

            # Web Access Port
            if ip_address:
                text2 = f"{ip_address}:5000"
            else:
                text2 = "Monitoring..."
            bbox2 = draw.textbbox((0, 0), text2, font=self.font_small)
            text2_width = bbox2[2] - bbox2[0]
            x2 = (self.width - text2_width) // 2
            draw.text((x2, 52), text2, font=self.font_small, fill=255)

            self.device.display(image)
            time.sleep(3)
        except:
            pass

    def show_alert_count(self, count):
        """Display alert count prominently"""
        if not self.enabled or self.device is None:
            return
        try:
            image = Image.new("1", (self.width, self.height))
            draw = ImageDraw.Draw(image)

            # Large alert icon (bell)
            draw.ellipse((55, 5, 73, 20), outline=255, fill=0)
            draw.rectangle((60, 18, 68, 22), outline=255, fill=255)

            # Alert count
            count_text = str(count)
            bbox = draw.textbbox((0, 0), count_text, font=self.font_large)
            text_width = bbox[2] - bbox[0]
            x = (self.width - text_width) // 2
            draw.text((x, 28), count_text, font=self.font_large, fill=255)

            # Label
            label = "ALERTS"
            bbox2 = draw.textbbox((0, 0), label, font=self.font_small)
            text_width2 = bbox2[2] - bbox2[0]
            x2 = (self.width - text_width2) // 2
            draw.text((x2, 52), label, font=self.font_small, fill=255)

            self.device.display(image)
            time.sleep(2)
        except:
            pass

class SensorHandler:
    """MQ-135 Smoke Sensor Handler"""

    def __init__(self, pin=MQ135_PIN, inverted=SENSOR_INVERTED, warmup_time=30):
        """Initialize sensor"""
        self.pin = pin
        self.inverted = inverted
        self.warmup_time = warmup_time
        self.is_warmed_up = False
        self.enabled = ENABLE_SENSOR

        if not self.enabled:
            print("⚠ Sensor disabled in settings")
            return

        try:
            GPIO.setmode(GPIO.BCM)
            GPIO.setup(self.pin, GPIO.IN)
            print(f"⏳ MQ-135 warming up ({warmup_time}s)...")
            threading.Thread(target=self._warmup, daemon=True).start()
        except Exception as e:
            print(f"⚠ Sensor initialization failed: {e}")
            self.enabled = False

    def _warmup(self):
        """Warmup sensor"""
        time.sleep(self.warmup_time)
        self.is_warmed_up = True
        print("✓ MQ-135 sensor ready!")

    def detect_smoke(self):
        """Check if smoke detected"""
        if not self.enabled or not self.is_warmed_up:
            return False

        try:
            reading = GPIO.input(self.pin)
            if self.inverted:
                return reading == GPIO.LOW
            else:
                return reading == GPIO.HIGH
        except:
            return False

    def get_status(self):
        """Get sensor status"""
        if not self.enabled:
            return "DISABLED"
        if not self.is_warmed_up:
            return "WARMUP"
        return "SMOKE!" if self.detect_smoke() else "CLEAR"

class AlertSystem:
    """Optional buzzer and LED alerts"""

    def __init__(self, buzzer_pin=BUZZER_PIN, led_red=LED_RED, led_green=LED_GREEN):
        """Initialize alert system"""
        self.enabled = False
        try:
            GPIO.setmode(GPIO.BCM)
            GPIO.setup(buzzer_pin, GPIO.OUT)
            GPIO.setup(led_red, GPIO.OUT)
            GPIO.setup(led_green, GPIO.OUT)

            GPIO.output(buzzer_pin, GPIO.LOW)
            GPIO.output(led_red, GPIO.LOW)
            GPIO.output(led_green, GPIO.HIGH)

            self.buzzer_pin = buzzer_pin
            self.led_red = led_red
            self.led_green = led_green
            self.enabled = True
            print("✓ Alert system initialized")
        except Exception as e:
            print(f"⚠ Alert system not available: {e}")

    def trigger_alert(self):
        """Trigger alert"""
        if not self.enabled:
            return
        try:
            GPIO.output(self.led_red, GPIO.HIGH)
            GPIO.output(self.led_green, GPIO.LOW)
            for _ in range(3):
                GPIO.output(self.buzzer_pin, GPIO.HIGH)
                time.sleep(0.2)
                GPIO.output(self.buzzer_pin, GPIO.LOW)
                time.sleep(0.1)
        except:
            pass

    def set_normal(self):
        """Set normal status"""
        if not self.enabled:
            return
        try:
            GPIO.output(self.led_red, GPIO.LOW)
            GPIO.output(self.led_green, GPIO.HIGH)
            GPIO.output(self.buzzer_pin, GPIO.LOW)
        except:
            pass

class SmokingDetectionSystem:
    def __init__(self, save_dir="violations", alert_cooldown=30,
                 max_storage_mb=300, max_images=150, image_quality=60, ip_address=""):
        """Initialize enhanced detection system"""
        self.save_dir = save_dir
        self.alert_cooldown = alert_cooldown
        self.last_alert_time = 0
        self.last_oled_update = 0
        self.max_storage_mb = max_storage_mb
        self.max_images = max_images
        self.image_quality = image_quality
        self.ip_address = ip_address

        os.makedirs(save_dir, exist_ok=True)
        self.cleanup_old_files()

        # Initialize hardware
        print("\n" + "="*50)
        print("🚭 ENHANCED NO-SMOKING DETECTION SYSTEM")
        print("="*50 + "\n")

        self.oled = OLEDDisplay()

        self.sensor = SensorHandler() if ENABLE_SENSOR else None
        self.alerts = AlertSystem()

        # Initialize camera
        print("📷 Initializing camera...")
        self.picam2 = Picamera2()
        config = self.picam2.create_preview_configuration(
            main={"size": (416, 320)}  # Optimized for Pi Zero 2 W
        )
        self.picam2.configure(config)
        self.picam2.start()
        time.sleep(2)
        print("✓ Camera ready")

        # Load AI model (optional)
        self.load_models()

        self.confidence_threshold = DETECTION_CONFIDENCE
        self.running = False
        self.frame_skip = 2
        self.frame_count = 0

        # For web streaming
        self.current_frame = None
        self.lock = threading.Lock()
        self.detection_status = "Monitoring..."
        self.total_violations = 0
        self.detection_counts = {
            'sensor': 0,
            'motion': 0,
            'visual': 0,
            'combined': 0
        }

        print("\n✓ System initialized!")
        print(f"Detection modes: Sensor={'✓' if ENABLE_SENSOR else '✗'}, "
              f"Motion={'✓' if ENABLE_MOTION else '✗'}, "
              f"Visual={'✓' if ENABLE_VISUAL else '✗'}, "
              f"OLED={'✓' if ENABLE_OLED else '✗'}\n")

        self.oled.show_system_ready(self.ip_address)

    def load_models(self):
        """Load MobileNet-SSD model (optional)"""
        try:
            self.net = cv2.dnn.readNetFromCaffe(
                "MobileNetSSD_deploy.prototxt",
                "MobileNetSSD_deploy.caffemodel"
            )
            self.net.setPreferableBackend(cv2.dnn.DNN_BACKEND_OPENCV)
            self.net.setPreferableTarget(cv2.dnn.DNN_TARGET_CPU)
            print("✓ MobileNet-SSD loaded")
        except:
            print("⚠ MobileNet-SSD not found (using lightweight detection)")
            self.net = None

    def detect_person(self, frame):
        """Detect person using MobileNet-SSD"""
        if self.net is None or not ENABLE_MOTION:
            return False, []

        try:
            height, width = frame.shape[:2]
            blob = cv2.dnn.blobFromImage(
                cv2.resize(frame, (300, 300)),
                0.007843, (300, 300), 127.5
            )
            self.net.setInput(blob)
            detections = self.net.forward()

            boxes = []
            for i in range(detections.shape[2]):
                confidence = detections[0, 0, i, 2]
                if confidence > 0.5:
                    idx = int(detections[0, 0, i, 1])
                    if idx == 15:  # Person class
                        box = detections[0, 0, i, 3:7] * np.array([width, height, width, height])
                        (x, y, x2, y2) = box.astype("int")
                        boxes.append([x, y, x2-x, y2-y])

            return len(boxes) > 0, boxes
        except:
            return False, []

    def detect_motion(self, frame):
        """Motion detection fallback"""
        if not ENABLE_MOTION:
            return False, []

        if not hasattr(self, 'prev_frame'):
            self.prev_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            self.prev_frame = cv2.GaussianBlur(self.prev_frame, (21, 21), 0)
            return False, []

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        gray = cv2.GaussianBlur(gray, (21, 21), 0)
        frame_delta = cv2.absdiff(self.prev_frame, gray)
        thresh = cv2.threshold(frame_delta, 25, 255, cv2.THRESH_BINARY)[1]
        thresh = cv2.dilate(thresh, None, iterations=2)
        contours, _ = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL,
                                       cv2.CHAIN_APPROX_SIMPLE)

        motion_detected = any(cv2.contourArea(c) > 5000 for c in contours)
        self.prev_frame = gray
        return motion_detected, []

    def detect_cigarette_visual(self, frame):
        """Improved visual cigarette detection with better filtering"""
        if not ENABLE_VISUAL:
            return False, []

        try:
            hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

            # Detect bright orange/red (lit cigarette tip - most reliable)
            lower_orange = np.array([0, 150, 150])  # Higher saturation
            upper_orange = np.array([20, 255, 255])
            orange_mask = cv2.inRange(hsv, lower_orange, upper_orange)

            # Detect white cylindrical object (cigarette body)
            lower_white = np.array([0, 0, 180])  # Brighter white
            upper_white = np.array([180, 30, 255])  # Less saturation
            white_mask = cv2.inRange(hsv, lower_white, upper_white)

            # Apply morphological operations
            kernel_small = np.ones((2,2), np.uint8)
            kernel_large = np.ones((5,5), np.uint8)

            orange_mask = cv2.morphologyEx(orange_mask, cv2.MORPH_OPEN, kernel_small)
            orange_mask = cv2.dilate(orange_mask, kernel_small, iterations=2)

            white_mask = cv2.morphologyEx(white_mask, cv2.MORPH_OPEN, kernel_small)
            white_mask = cv2.morphologyEx(white_mask, cv2.MORPH_CLOSE, kernel_large)

            # Find contours in both masks
            orange_contours, _ = cv2.findContours(orange_mask, cv2.RETR_EXTERNAL,
                                                  cv2.CHAIN_APPROX_SIMPLE)
            white_contours, _ = cv2.findContours(white_mask, cv2.RETR_EXTERNAL,
                                                 cv2.CHAIN_APPROX_SIMPLE)

            boxes = []
            detected = False

            # Check for orange (lit tip) - high confidence
            for contour in orange_contours:
                area = cv2.contourArea(contour)
                if 50 < area < 800:  # Small bright spot
                    x, y, w, h = cv2.boundingRect(contour)
                    aspect_ratio = float(max(w, h)) / float(min(w, h)) if min(w, h) > 0 else 0

                    # Check for circular/square shape (lit tip)
                    if 0.5 < aspect_ratio < 2.5:
                        boxes.append([x, y, w, h])
                        detected = True

            # Check for white cylindrical object (cigarette body)
            for contour in white_contours:
                area = cv2.contourArea(contour)
                if 200 < area < 3000:  # Cigarette-sized
                    x, y, w, h = cv2.boundingRect(contour)
                    aspect_ratio = float(max(w, h)) / float(min(w, h)) if min(w, h) > 0 else 0

                    # Cigarettes are elongated (aspect ratio > 2.5)
                    if aspect_ratio > 2.5 and aspect_ratio < 8.0:
                        # Additional check: should be thin
                        if min(w, h) < 30:  # Thin object
                            # Check if there's an orange tip nearby
                            has_orange_tip = False
                            for ox, oy, ow, oh in boxes:
                                # Check if orange is near this white object
                                distance = abs((x + w/2) - (ox + ow/2)) + abs((y + h/2) - (oy + oh/2))
                                if distance < 100:
                                    has_orange_tip = True
                                    break

                            # Only add if confidence is high enough
                            if has_orange_tip or aspect_ratio > 4.0:
                                if [x, y, w, h] not in boxes:
                                    boxes.append([x, y, w, h])
                                    detected = True

            return detected, boxes
        except Exception as e:
            print(f"Visual detection error: {e}")
            return False, []

    def detect_all(self, frame):
        """Run all detection methods"""
        results = {
            'sensor': False,
            'motion': False,
            'visual': False,
            'boxes': []
        }

        # Check sensor
        if self.sensor and ENABLE_SENSOR:
            results['sensor'] = self.sensor.detect_smoke()

        # Check motion/person
        if ENABLE_MOTION:
            person_detected, person_boxes = self.detect_person(frame)
            if person_detected:
                results['motion'] = True
                results['boxes'].extend(person_boxes)
            else:
                motion_detected, _ = self.detect_motion(frame)
                results['motion'] = motion_detected

        # Check visual cigarette
        if ENABLE_VISUAL:
            visual_detected, visual_boxes = self.detect_cigarette_visual(frame)
            if visual_detected:
                results['visual'] = True
                results['boxes'].extend(visual_boxes)

        # Overall detection
        detected = results['sensor'] or results['motion'] or results['visual']

        return detected, results

    def save_violation(self, frame, results):
        """Save violation image"""
        timestamp = datetime.now()
        filename = timestamp.strftime("%Y%m%d_%H%M%S") + ".jpg"
        filepath = os.path.join(self.save_dir, filename)

        # Resize if needed
        height, width = frame.shape[:2]
        if width > 640:
            scale = 640 / width
            frame = cv2.resize(frame, (640, int(height * scale)))

        annotated_frame = frame.copy()

        # Draw boxes
        for box in results.get('boxes', []):
            x, y, w, h = box
            if width > 640:
                scale = 640 / width
                x, y, w, h = int(x*scale), int(y*scale), int(w*scale), int(h*scale)
            cv2.rectangle(annotated_frame, (x, y), (x+w, y+h), (0, 0, 255), 2)

        # Add detection info
        y_offset = 25
        cv2.putText(annotated_frame, "VIOLATION DETECTED", (10, y_offset),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)
        y_offset += 25

        detection_types = []
        if results['sensor']:
            detection_types.append("SENSOR")
        if results['motion']:
            detection_types.append("MOTION")
        if results['visual']:
            detection_types.append("CIGARETTE")

        cv2.putText(annotated_frame, f"Type: {'+'.join(detection_types)}",
                   (10, y_offset), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 1)
        y_offset += 20

        cv2.putText(annotated_frame, timestamp.strftime("%Y-%m-%d %H:%M:%S"),
                   (10, y_offset), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 1)

        # Save
        cv2.imwrite(filepath, annotated_frame,
                   [cv2.IMWRITE_JPEG_QUALITY, self.image_quality])

        file_size = os.path.getsize(filepath) / 1024
        print(f"✓ Violation saved: {filename} ({file_size:.1f} KB)")

        # Update counters
        self.total_violations += 1
        if results['sensor'] and (results['motion'] or results['visual']):
            self.detection_counts['combined'] += 1
        elif results['sensor']:
            self.detection_counts['sensor'] += 1
        elif results['visual']:
            self.detection_counts['visual'] += 1
        elif results['motion']:
            self.detection_counts['motion'] += 1

        self.cleanup_old_files()
        return filepath

    def cleanup_old_files(self):
        """Remove old files if limits exceeded"""
        files = []
        for f in os.listdir(self.save_dir):
            if f.endswith('.jpg'):
                filepath = os.path.join(self.save_dir, f)
                files.append((filepath, os.path.getmtime(filepath)))

        files.sort(key=lambda x: x[1])
        total_size = sum(os.path.getsize(f[0]) for f in files) / (1024 * 1024)
        removed_count = 0

        while len(files) > self.max_images or total_size > self.max_storage_mb:
            if not files:
                break
            os.remove(files.pop(0)[0])
            removed_count += 1
            total_size = sum(os.path.getsize(f[0]) for f in files) / (1024 * 1024)

        if removed_count > 0:
            print(f"🗑️  Cleaned up {removed_count} old files")

    def get_storage_info(self):
        """Get storage statistics"""
        files = [f for f in os.listdir(self.save_dir) if f.endswith('.jpg')]
        total_size = sum(os.path.getsize(os.path.join(self.save_dir, f))
                        for f in files) / (1024 * 1024)
        return {
            "total_images": len(files),
            "total_size_mb": round(total_size, 2),
            "max_storage_mb": self.max_storage_mb,
            "storage_percent": round((total_size / self.max_storage_mb) * 100, 1)
        }

    def get_recent_violations(self, limit=20):
        """Get recent violations"""
        files = []
        for f in os.listdir(self.save_dir):
            if f.endswith('.jpg'):
                filepath = os.path.join(self.save_dir, f)
                files.append({
                    'filename': f,
                    'timestamp': datetime.fromtimestamp(
                        os.path.getmtime(filepath)
                    ).strftime('%Y-%m-%d %H:%M:%S'),
                    'size_kb': round(os.path.getsize(filepath) / 1024, 1)
                })
        files.sort(key=lambda x: x['timestamp'], reverse=True)
        return files[:limit]

    def run_detection(self):
        """Main detection loop"""
        self.running = True
        print("🎥 Detection started...\n")

        # Wait for sensor warmup if enabled
        if self.sensor and ENABLE_SENSOR:
            while not self.sensor.is_warmed_up:
                self.oled.show_text(["Warming Up", "Please Wait..."], center=True)
                time.sleep(1)

        self.oled.show_no_smoking()

        try:
            while self.running:
                frame = self.picam2.capture_array()
                frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)

                self.frame_count += 1
                if self.frame_count % self.frame_skip != 0:
                    time.sleep(0.05)
                    continue

                # Run all detections
                detected, results = self.detect_all(frame)
                current_time = time.time()

                # Prepare display frame
                display_frame = frame.copy()
                status_color = (0, 0, 255) if detected else (0, 255, 0)

                # Draw status
                cv2.putText(display_frame, self.detection_status, (10, 25),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.5, status_color, 2)

                # Draw detection info
                y_offset = 45
                if self.sensor:
                    sensor_status = self.sensor.get_status()
                    sensor_color = (0, 0, 255) if results['sensor'] else (0, 255, 0)
                    cv2.putText(display_frame, f"Sensor: {sensor_status}", (10, y_offset),
                               cv2.FONT_HERSHEY_SIMPLEX, 0.4, sensor_color, 1)
                    y_offset += 18

                cv2.putText(display_frame, f"Violations: {self.total_violations}",
                           (10, y_offset), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255, 255, 255), 1)

                # Draw boxes
                for box in results.get('boxes', []):
                    x, y, w, h = box
                    cv2.rectangle(display_frame, (x, y), (x+w, y+h), (0, 0, 255), 2)

                # Handle detection
                if detected:
                    detection_types = []
                    if results['sensor']:
                        detection_types.append("SENSOR")
                    if results['motion']:
                        detection_types.append("MOTION")
                    if results['visual']:
                        detection_types.append("CIGARETTE")

                    self.detection_status = f"⚠️ DETECTED: {'+'.join(detection_types)}"

                    # Update OLED with violation
                    self.oled.show_violation('+'.join(detection_types))

                    if current_time - self.last_alert_time > self.alert_cooldown:
                        self.save_violation(frame, results)
                        self.alerts.trigger_alert()
                        self.last_alert_time = current_time
                        print(f"🚨 ALERT: {'+'.join(detection_types)}")
                        # Show alert count on OLED briefly
                        threading.Thread(target=self._show_alert_briefly, daemon=True).start()
                else:
                    self.detection_status = "Monitoring..."
                    self.alerts.set_normal()

                    # Update OLED monitoring status every 5 seconds
                    if current_time - self.last_oled_update > 5:
                        sensor_status = self.sensor.get_status() if self.sensor else ""
                        self.oled.show_monitoring(sensor_status, self.total_violations, self.ip_address)
                        self.last_oled_update = current_time

                # Update frame for streaming
                with self.lock:
                    self.current_frame = display_frame.copy()

                time.sleep(0.2)

        except Exception as e:
            print(f"❌ Error: {e}")
            import traceback
            traceback.print_exc()
        finally:
            self.running = False

    def _show_alert_briefly(self):
        """Show alert count briefly after detection"""
        time.sleep(3)  # Wait 3 seconds while violation message is showing
        self.oled.show_alert_count(self.total_violations)

    def get_frame(self):
        """Get frame for streaming"""
        with self.lock:
            if self.current_frame is not None:
                ret, buffer = cv2.imencode('.jpg', self.current_frame,
                                          [cv2.IMWRITE_JPEG_QUALITY, 70])
                return buffer.tobytes()
        return None

    def stop(self):
        """Stop system"""
        self.running = False
        self.picam2.stop()
        self.oled.clear()
        if self.sensor:
            GPIO.cleanup()
        print("✓ System stopped")


# Flask Web Application
app = Flask(__name__)
detector = None

HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>🚭 No-Smoking Detection + OLED</title>
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: Arial, sans-serif;
            background: linear-gradient(135deg, #1a1a1a 0%, #2d2d2d 100%);
            color: #fff;
            padding: 20px;
        }
        .container { max-width: 1200px; margin: 0 auto; }
        h1 {
            text-align: center;
            color: #ff4444;
            margin-bottom: 10px;
            font-size: 24px;
        }
        .subtitle {
            text-align: center;
            color: #4CAF50;
            margin-bottom: 20px;
            font-size: 14px;
        }
        .status-bar {
            background: #2a2a2a;
            padding: 15px;
            border-radius: 10px;
            margin-bottom: 20px;
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
            gap: 12px;
        }
        .stat {
            background: #333;
            padding: 12px;
            border-radius: 5px;
            text-align: center;
        }
        .stat-label { font-size: 11px; color: #999; margin-bottom: 5px; }
        .stat-value { font-size: 18px; font-weight: bold; color: #4CAF50; }
        .alert { color: #ff4444; }
        .video-container {
            background: #000;
            border-radius: 10px;
            overflow: hidden;
            margin-bottom: 20px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.3);
            border: 2px solid #ff4444;
        }
        .video-container img {
            width: 100%;
            height: auto;
            display: block;
        }
        .violations-section {
            background: #2a2a2a;
            padding: 15px;
            border-radius: 10px;
        }
        .violations-section h2 {
            margin-bottom: 15px;
            color: #ff4444;
            font-size: 18px;
        }
        .violations-grid {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
            gap: 12px;
        }
        .violation-card {
            background: #333;
            border-radius: 5px;
            overflow: hidden;
            cursor: pointer;
            transition: transform 0.2s;
            border: 2px solid #555;
        }
        .violation-card:hover {
            transform: scale(1.05);
            border-color: #ff4444;
        }
        .violation-card img {
            width: 100%;
            height: 150px;
            object-fit: cover;
        }
        .violation-info {
            padding: 10px;
            font-size: 12px;
        }
        @media (max-width: 768px) {
            h1 { font-size: 20px; }
            .status-bar { grid-template-columns: 1fr 1fr; }
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>🚭 No-Smoking Detection System + SH1106 OLED</h1>
        <div class="subtitle">Sensor + Motion + Visual AI + 128x64 OLED Display</div>

        <div class="status-bar">
            <div class="stat">
                <div class="stat-label">Status</div>
                <div class="stat-value" id="status">Loading...</div>
            </div>
            <div class="stat">
                <div class="stat-label">Sensor</div>
                <div class="stat-value" id="sensor">--</div>
            </div>
            <div class="stat">
                <div class="stat-label">Total Violations</div>
                <div class="stat-value alert" id="violations">0</div>
            </div>
            <div class="stat">
                <div class="stat-label">Sensor Detections</div>
                <div class="stat-value" id="sensor-count">0</div>
            </div>
            <div class="stat">
                <div class="stat-label">Visual Detections</div>
                <div class="stat-value" id="visual-count">0</div>
            </div>
            <div class="stat">
                <div class="stat-label">Combined</div>
                <div class="stat-value" id="combined-count">0</div>
            </div>
            <div class="stat">
                <div class="stat-label">Storage</div>
                <div class="stat-value" id="storage">0 MB</div>
            </div>
            <div class="stat">
                <div class="stat-label">Images</div>
                <div class="stat-value" id="images">0</div>
            </div>
        </div>

        <div class="video-container">
            <img src="{{ url_for('video_feed') }}" alt="Live Detection Feed">
        </div>

        <div class="violations-section">
            <h2>📸 Recent Violations</h2>
            <div class="violations-grid" id="violations-list">
                <p style="color: #999;">No violations recorded</p>
            </div>
        </div>
    </div>

    <script>
        function updateStats() {
            fetch('/api/stats')
                .then(response => response.json())
                .then(data => {
                    const statusEl = document.getElementById('status');
                    statusEl.textContent = data.status;
                    statusEl.className = data.status.includes('DETECTED') ? 'stat-value alert' : 'stat-value';

                    document.getElementById('sensor').textContent = data.sensor_status || '--';
                    document.getElementById('violations').textContent = data.total_violations;
                    document.getElementById('sensor-count').textContent = data.detection_counts.sensor;
                    document.getElementById('visual-count').textContent = data.detection_counts.visual;
                    document.getElementById('combined-count').textContent = data.detection_counts.combined;
                    document.getElementById('storage').textContent = data.storage.total_size_mb + ' MB';
                    document.getElementById('images').textContent = data.storage.total_images;
                });

            fetch('/api/violations')
                .then(response => response.json())
                .then(data => {
                    const list = document.getElementById('violations-list');
                    if (data.violations.length === 0) {
                        list.innerHTML = '<p style="color: #999;">No violations recorded</p>';
                    } else {
                        list.innerHTML = data.violations.map(v => `
                            <div class="violation-card" onclick="window.open('/violations/${v.filename}', '_blank')">
                                <img src="/violations/${v.filename}" alt="Violation">
                                <div class="violation-info">
                                    <div style="color: #ff4444; font-weight: bold;">${v.timestamp}</div>
                                    <div style="color: #999; margin-top: 5px;">${v.size_kb} KB</div>
                                </div>
                            </div>
                        `).join('');
                    }
                });
        }

        setInterval(updateStats, 1500);
        updateStats();
    </script>
</body>
</html>
"""

def generate_frames():
    """Generate frames for streaming"""
    global detector
    while True:
        if detector is not None:
            frame = detector.get_frame()
            if frame is not None:
                yield (b'--frame\r\n'
                       b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
        time.sleep(0.1)

@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE)

@app.route('/video_feed')
def video_feed():
    return Response(generate_frames(),
                   mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/api/stats')
def api_stats():
    global detector
    if detector is None:
        return jsonify({'error': 'System not initialized'})

    storage = detector.get_storage_info()
    sensor_status = detector.sensor.get_status() if detector.sensor else "DISABLED"

    return jsonify({
        'status': detector.detection_status,
        'sensor_status': sensor_status,
        'total_violations': detector.total_violations,
        'detection_counts': detector.detection_counts,
        'storage': storage
    })

@app.route('/api/violations')
def api_violations():
    global detector
    if detector is None:
        return jsonify({'violations': []})

    violations = detector.get_recent_violations(limit=20)
    return jsonify({'violations': violations})

@app.route('/violations/<filename>')
def serve_violation(filename):
    global detector
    return send_from_directory(detector.save_dir, filename)

def start_web_server():
    app.run(host='0.0.0.0', port=5000, threaded=True, debug=False)

if __name__ == "__main__":
    print("\n" + "="*50)
    print("🚭 ENHANCED SMOKING DETECTION SYSTEM + SH1106 OLED")
    print("="*50)
    print(f"\nDetection Methods:")
    print(f"  Sensor (MQ-135): {'✓' if ENABLE_SENSOR else '✗'}")
    print(f"  Motion Detection: {'✓' if ENABLE_MOTION else '✗'}")
    print(f"  Visual Cigarette: {'✓' if ENABLE_VISUAL else '✗'}")
    print(f"  OLED Display: {'✓' if ENABLE_OLED else '✗'}")
    print(f"\nSettings:")
    print(f"  Sensor inverted: {SENSOR_INVERTED}")
    print(f"  Visual confidence: {DETECTION_CONFIDENCE}")
    print(f"  OLED address: 0x{OLED_ADDRESS:02x}")
    print("="*50 + "\n")

    # Get IP address first
    import socket
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(('8.8.8.8', 80))
        ip_address = s.getsockname()[0]
    except:
        ip_address = '127.0.0.1'
    finally:
        s.close()

    # Initialize system with IP address
    detector = SmokingDetectionSystem(
        save_dir="violations",
        alert_cooldown=30,
        max_storage_mb=300,
        max_images=150,
        image_quality=60,
        ip_address=ip_address
    )

    # Start detection thread
    detection_thread = threading.Thread(target=detector.run_detection, daemon=True)
    detection_thread.start()

    print(f"\n{'='*50}")
    print(f"🌐 Web Interface Started")
    print(f"{'='*50}")
    print(f"Access from any device:")
    print(f"  http://{ip_address}:5000")
    print(f"{'='*50}\n")

    # Start web server
    start_web_server()
