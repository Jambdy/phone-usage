# Phone Usage Backend

Python CLI tool for collecting Android app usage data via ADB.

## Prerequisites

- Python 3.8+
- ADB (Android Debug Bridge) installed and in PATH
- Android device with USB debugging enabled

## Setup

1. Create virtual environment:
```bash
python -m venv venv
```

2. Activate virtual environment:
```bash
# Windows
venv\Scripts\activate

# macOS/Linux
source venv/bin/activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

## Android Setup

1. Enable Developer Options on your Android device
2. Enable USB Debugging
3. Connect device via USB
4. Authorize the computer when prompted on device
5. Verify connection: `adb devices`

## Usage

### List connected devices
```bash
python collect_usage.py --list-devices
```

### Collect usage data (default: last 7 days)
```bash
python collect_usage.py
```

### Collect specific number of days
```bash
python collect_usage.py --days 30
```

### Connect to specific device
```bash
python collect_usage.py --device DEVICE_ID
```

## Output

Data is saved to `../data/usage_data.json` and can be read by the frontend dashboard.
