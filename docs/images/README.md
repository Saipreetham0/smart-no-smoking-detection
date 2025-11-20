# Project Images and Diagrams

This directory contains images, diagrams, and visual assets for the project documentation.

## Directory Structure

```
docs/images/
├── hardware/           # Hardware setup photos
│   ├── raspberry-pi-setup.jpg
│   ├── oled-display.jpg
│   ├── camera-module.jpg
│   └── full-assembly.jpg
├── screenshots/        # Software screenshots
│   ├── web-interface.png
│   ├── oled-startup.jpg
│   ├── oled-monitoring.jpg
│   └── oled-alert.jpg
├── diagrams/          # Technical diagrams
│   ├── system-architecture.png
│   ├── detection-flow.png
│   └── gpio-pinout.png
└── demo/              # Demo GIFs and videos
    ├── detection-demo.gif
    └── web-interface-demo.gif
```

## How to Add Images

### 1. Hardware Photos

Take clear, well-lit photos of:
- Complete hardware setup
- Individual components
- GPIO connections
- Wiring diagrams

**Naming Convention:**
- `component-name-view.jpg`
- Example: `raspberry-pi-top-view.jpg`

### 2. Screenshots

Capture screenshots of:
- Web interface (all pages)
- OLED display screens
- Configuration screens
- Alert notifications

**Naming Convention:**
- `interface-page-description.png`
- Example: `web-dashboard-monitoring.png`

### 3. Diagrams

Create diagrams for:
- System architecture
- Data flow
- Detection algorithm
- Network topology

**Tools:**
- draw.io (diagrams.net)
- Lucidchart
- Mermaid diagrams
- Python matplotlib

**Naming Convention:**
- `diagram-type-description.png`
- Example: `architecture-detection-pipeline.png`

### 4. Demo GIFs

Create animated demonstrations:
- Detection in action
- Web interface usage
- OLED display states

**Tools:**
- LICEcap (Windows/Mac)
- Peek (Linux)
- ScreenToGif (Windows)
- ffmpeg for video conversion

**Naming Convention:**
- `demo-feature-name.gif`
- Example: `demo-cigarette-detection.gif`

## Image Guidelines

### Size Requirements
- Screenshots: Max 1920x1080
- Photos: Max 2048x1536
- Diagrams: SVG preferred, or PNG at 300 DPI
- GIFs: Max 10MB, 15 FPS

### Quality Standards
- Use high resolution (300 DPI for print)
- Clear, focused images
- Good lighting for photos
- Remove sensitive information (IP addresses, passwords)
- Compress images appropriately

### Optimization
```bash
# Install ImageMagick for optimization
sudo apt install imagemagick

# Optimize PNG
convert input.png -quality 85 -strip output.png

# Optimize JPEG
convert input.jpg -quality 85 -strip output.jpg

# Resize image
convert input.png -resize 1920x1080 output.png
```

## Using Images in Documentation

### Markdown Syntax

```markdown
# Absolute path
![Description](docs/images/category/image-name.png)

# Relative path (from README.md)
![Description](./docs/images/category/image-name.png)

# With link
[![Description](docs/images/image.png)](https://link-url.com)

# Centered with HTML
<div align="center">
  <img src="docs/images/image.png" alt="Description" width="600">
</div>
```

### Example Usage

```markdown
## Hardware Setup

Here's the complete setup:

![Complete Hardware Setup](docs/images/hardware/full-assembly.jpg)

### GPIO Connections

<div align="center">
  <img src="docs/images/diagrams/gpio-pinout.png" alt="GPIO Pinout" width="500">
</div>
```

## Placeholder Images

Until actual images are available, we recommend:
- Using placeholder services (placeholder.com)
- Creating simple diagrams with ASCII art
- Using icons and emojis

## Contributing Images

When contributing images:
1. Place in appropriate subdirectory
2. Follow naming conventions
3. Optimize file size
4. Update this README if adding new categories
5. Include attribution if not original work

## Copyright and Licensing

All images should be:
- Original content
- Properly licensed
- Attribution provided for third-party content
- Consistent with MIT license

## Future Additions

Planned image content:
- [ ] Complete hardware assembly guide
- [ ] OLED display state screenshots
- [ ] Web interface screenshots (all pages)
- [ ] Detection algorithm flowchart
- [ ] System architecture diagram
- [ ] Network setup diagram
- [ ] Demo GIF of detection in action
- [ ] Comparison before/after images
- [ ] Performance benchmark graphs

---

**Note**: When you add actual project images, update this README with specific file listings and descriptions.
