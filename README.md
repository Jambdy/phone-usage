# Phone Usage Dashboard

A local dashboard for tracking and visualizing Android phone app usage statistics. Collects data via ADB and displays it in a beautiful Next.js dashboard.

## Features

- Collect app usage data from Android device via ADB
- Store data locally in JSON format
- Visualize usage with interactive charts (Pie & Bar)
- View detailed statistics per app
- Track total screen time and usage trends
- No cloud services - completely local and private

## Project Structure

```
phone-usage/
├── backend/          # Python scripts for data collection
│   ├── collect_usage.py    # Main CLI script
│   ├── adb_connector.py    # ADB communication module
│   ├── data_storage.py     # JSON file storage
│   └── requirements.txt    # Python dependencies
├── frontend/         # Next.js dashboard
│   ├── app/          # Next.js app directory
│   └── package.json  # Node dependencies
└── data/            # JSON data storage (generated)
```

## Prerequisites

- **Python 3.8+**
- **Node.js 18+**
- **ADB (Android Debug Bridge)** installed and in PATH
- **Android device** with USB debugging enabled

## Setup

### 1. Install ADB

Download Android SDK Platform Tools:
- Windows: https://developer.android.com/studio/releases/platform-tools
- Add to PATH or place in project directory

### 2. Setup Python Backend

```bash
cd backend
python -m venv venv

# Windows
venv\Scripts\activate

# macOS/Linux
source venv/bin/activate

pip install -r requirements.txt
```

### 3. Setup Next.js Frontend

```bash
cd frontend
npm install
```

### 4. Enable USB Debugging on Android

1. Go to Settings > About Phone
2. Tap "Build Number" 7 times to enable Developer Options
3. Go to Settings > Developer Options
4. Enable "USB Debugging"
5. Connect device via USB
6. Authorize computer when prompted on device

## Usage

### Step 1: Collect Data from Your Phone

```bash
cd backend
python collect_usage.py

# Collect specific number of days
python collect_usage.py --days 30

# List connected devices
python collect_usage.py --list-devices
```

This will create `data/usage_data.json` with your usage statistics.

### Step 2: View Dashboard

```bash
cd frontend
npm run dev
```

Open http://localhost:3000 in your browser to view the dashboard.

## Dashboard Features

- **Summary Cards**: Total screen time, apps tracked, total records
- **Pie Chart**: Visual breakdown of top 10 most used apps
- **Bar Chart**: Comparative view of app usage
- **Detailed List**: All apps with usage time sorted by most used

## Data Privacy

All data is stored locally on your machine. No data is sent to any cloud service or external server. The dashboard reads directly from the local JSON file.

## Troubleshooting

### ADB not found
- Make sure Android SDK Platform Tools are installed
- Add ADB to your system PATH
- Verify: `adb version`

### No devices connected
- Check USB cable connection
- Enable USB debugging in Developer Options
- Authorize computer on device screen
- Verify: `adb devices`

### No usage data retrieved
- Check device permissions for usage stats
- Some Android versions may have different data formats
- Try running with elevated permissions

## Development

### Backend
See [backend/README.md](backend/README.md) for detailed backend documentation.

### Frontend
The dashboard is built with:
- Next.js 15
- TypeScript
- Chart.js & react-chartjs-2
- React 19

## License

ISC
