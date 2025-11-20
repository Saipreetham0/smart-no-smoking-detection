# Contributing to Smart No-Smoking Detection System

First off, thank you for considering contributing to the Smart No-Smoking Detection System! It's people like you that make this project better for everyone.

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [How Can I Contribute?](#how-can-i-contribute)
- [Development Setup](#development-setup)
- [Pull Request Process](#pull-request-process)
- [Coding Standards](#coding-standards)
- [Testing Guidelines](#testing-guidelines)
- [Documentation](#documentation)

## Code of Conduct

### Our Pledge

We are committed to providing a welcoming and inspiring community for all. Please be respectful and constructive in your interactions.

### Our Standards

**Positive behaviors include:**
- Using welcoming and inclusive language
- Being respectful of differing viewpoints
- Gracefully accepting constructive criticism
- Focusing on what is best for the community
- Showing empathy towards other community members

**Unacceptable behaviors include:**
- Harassment, trolling, or derogatory comments
- Publishing others' private information without permission
- Other conduct which could reasonably be considered inappropriate

## How Can I Contribute?

### Reporting Bugs

Before creating bug reports, please check existing issues to avoid duplicates. When creating a bug report, include as many details as possible:

**Bug Report Template:**

```markdown
**Describe the bug**
A clear description of what the bug is.

**To Reproduce**
Steps to reproduce the behavior:
1. Go to '...'
2. Click on '...'
3. See error

**Expected behavior**
What you expected to happen.

**Screenshots**
If applicable, add screenshots.

**Environment:**
- Raspberry Pi Model: [e.g., Pi Zero 2 W]
- OS Version: [e.g., Raspberry Pi OS Bookworm]
- Python Version: [e.g., 3.9]
- Project Version: [e.g., 1.0]

**Additional context**
Any other relevant information.
```

### Suggesting Enhancements

Enhancement suggestions are tracked as GitHub issues. When creating an enhancement suggestion, include:

- A clear and descriptive title
- Detailed description of the proposed enhancement
- Explanation of why this enhancement would be useful
- Possible implementation approach (optional)

**Popular Enhancement Ideas:**
- Improved detection algorithms
- Mobile app for remote monitoring
- Analytics and reporting dashboard
- Push notifications (email, SMS, Telegram)
- Multi-language support
- Enhanced web UI/UX
- Database integration for violation history
- Multi-camera support
- Cloud integration options

### Your First Code Contribution

Unsure where to start? Look for issues labeled:
- `good first issue` - Simple issues for newcomers
- `help wanted` - Issues that need attention
- `documentation` - Documentation improvements

## Development Setup

### Prerequisites

- Raspberry Pi (Zero 2 W, 3, 4, or 5) or similar Linux system for testing
- Python 3.7+
- Git
- Basic knowledge of Python, OpenCV, and Flask

### Setting Up Development Environment

1. **Fork and Clone**

```bash
# Fork the repository on GitHub, then clone your fork
git clone https://github.com/Saipreetham0/smart-no-smoking-detection.git
cd smart-no-smoking-detection
```

2. **Create Virtual Environment**

```bash
# Create and activate virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install Dependencies**

```bash
# Install all required packages
pip install --upgrade pip
pip install -r requirements.txt

# Install development dependencies (if testing on non-Pi systems)
pip install pylint black pytest
```

4. **Create a Branch**

```bash
# Create a new branch for your feature/fix
git checkout -b feature/your-feature-name
# or
git checkout -b fix/bug-description
```

### Project Structure

```
smart-no-smoking-detection/
├── smoking_detector_with_sh1106.py  # Main application
├── requirements.txt                 # Dependencies
├── smoke-detector.service           # Systemd service
├── install_autostart.sh             # Auto-start installer
├── README.md                        # Main documentation
├── CONTRIBUTING.md                  # This file
├── LICENSE                          # MIT License
└── docs/                            # Additional documentation
```

## Pull Request Process

### Before Submitting

1. **Test Your Changes**
   - Test on actual Raspberry Pi hardware if possible
   - Ensure all features work as expected
   - Check for any introduced bugs

2. **Code Quality**
   - Follow the coding standards below
   - Add comments for complex logic
   - Update documentation if needed

3. **Commit Messages**
   - Use clear, descriptive commit messages
   - Follow conventional commit format:
     ```
     type(scope): subject

     body (optional)

     footer (optional)
     ```

   **Examples:**
   ```
   feat(detection): Add support for thermal cameras
   fix(oled): Resolve display refresh issue
   docs(readme): Update installation instructions
   refactor(web): Improve Flask route organization
   ```

### Submitting the Pull Request

1. **Push Your Changes**

```bash
git push origin feature/your-feature-name
```

2. **Create Pull Request**
   - Go to your fork on GitHub
   - Click "New Pull Request"
   - Fill in the PR template with details
   - Link any related issues

3. **PR Description Template**

```markdown
## Description
Brief description of changes

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Breaking change
- [ ] Documentation update

## Testing
How has this been tested?

## Checklist
- [ ] Code follows project style guidelines
- [ ] Self-review completed
- [ ] Commented complex code sections
- [ ] Documentation updated
- [ ] No new warnings generated
- [ ] Tested on Raspberry Pi (if applicable)
```

4. **Review Process**
   - Maintainers will review your PR
   - Address any requested changes
   - Once approved, your PR will be merged

## Coding Standards

### Python Style Guide

We follow [PEP 8](https://www.python.org/dev/peps/pep-0008/) with some modifications:

```python
# Good Examples

def detect_cigarette_visual(frame, sensitivity=0.5):
    """
    Detect cigarettes using visual analysis.

    Args:
        frame: Input image frame (numpy array)
        sensitivity: Detection sensitivity (0.0-1.0)

    Returns:
        tuple: (detected, confidence, bounding_boxes)
    """
    # Convert to HSV color space
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

    # Define color ranges for cigarette detection
    lower_orange = np.array([0, 150, 150])
    upper_orange = np.array([20, 255, 255])

    # Process and return results
    mask = cv2.inRange(hsv, lower_orange, upper_orange)
    return process_mask(mask)
```

### Code Formatting

- Use 4 spaces for indentation (no tabs)
- Maximum line length: 100 characters (soft limit)
- Use meaningful variable names
- Add docstrings to functions and classes
- Group imports: standard library, third-party, local

### Comments

```python
# Good: Explain WHY, not WHAT
# Use proximity checking to reduce false positives from random orange objects
if orange_detected and white_detected and distance < threshold:
    return True

# Bad: Don't state the obvious
# Check if x is greater than 5
if x > 5:
    return True
```

## Testing Guidelines

### Manual Testing

When testing on Raspberry Pi:

1. **Hardware Tests**
   - Verify camera initialization
   - Check OLED display output
   - Test smoke sensor (if connected)
   - Validate GPIO connections

2. **Detection Tests**
   - Test with actual cigarette/smoke
   - Test false positive scenarios
   - Verify motion detection
   - Check alert triggering

3. **Web Interface Tests**
   - Access from multiple devices
   - Test video streaming
   - Verify all endpoints
   - Check responsiveness

### Test Checklist

```markdown
- [ ] Camera captures frames correctly
- [ ] OLED displays system info
- [ ] Web interface loads properly
- [ ] Video stream works smoothly
- [ ] Detection algorithm functions
- [ ] Alerts trigger appropriately
- [ ] Violation images are saved
- [ ] Service auto-starts on boot
- [ ] No memory leaks during extended run
- [ ] All configuration options work
```

## Documentation

### Code Documentation

- Add docstrings to all public functions/classes
- Document complex algorithms
- Include usage examples where helpful
- Keep inline comments concise and relevant

### User Documentation

When adding features, update:
- README.md - Main user guide
- PROJECT_README.md - Detailed technical docs
- AUTOSTART_GUIDE.md - If affecting auto-start
- Code comments for configuration options

### Documentation Style

```python
def example_function(param1, param2="default"):
    """
    Brief one-line description.

    Longer description if needed, explaining what the function does,
    when to use it, and any important considerations.

    Args:
        param1 (type): Description of param1
        param2 (type, optional): Description of param2. Defaults to "default".

    Returns:
        type: Description of return value

    Raises:
        ExceptionType: When this exception is raised

    Example:
        >>> result = example_function("test", param2="custom")
        >>> print(result)
        Expected output
    """
    pass
```

## Areas for Contribution

### High Priority
- [ ] Improve detection algorithm accuracy
- [ ] Add unit tests
- [ ] Performance optimization
- [ ] Multi-camera support
- [ ] Database integration

### Medium Priority
- [ ] Enhanced web UI
- [ ] Mobile responsive design
- [ ] Email/SMS notifications
- [ ] Statistics dashboard
- [ ] Configuration file support

### Low Priority
- [ ] Multi-language support
- [ ] Voice alerts
- [ ] Cloud integration
- [ ] Machine learning improvements
- [ ] Docker container support

## Recognition

Contributors will be:
- Listed in the project README
- Credited in release notes
- Mentioned in the CONTRIBUTORS.md file

## Questions?

Feel free to:
- Open an issue for discussion
- Start a GitHub discussion
- Contact the maintainers

## Thank You!

Your contributions make this project better for everyone. We appreciate your time and effort! ⭐

---

**Happy Contributing!** 🚀
