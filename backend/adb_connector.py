"""
ADB Connector Module
Handles connection to Android device and data extraction
"""
import subprocess
import json
from datetime import datetime, timedelta
from typing import List, Dict, Optional


class ADBConnector:
    """Manages ADB connection and data retrieval from Android device"""

    def __init__(self):
        self.device_id = None

    def check_adb_installed(self) -> bool:
        """Check if ADB is installed and accessible"""
        try:
            result = subprocess.run(['adb', 'version'],
                                  capture_output=True,
                                  text=True,
                                  timeout=5)
            return result.returncode == 0
        except (subprocess.TimeoutExpired, FileNotFoundError):
            return False

    def get_connected_devices(self) -> List[str]:
        """Get list of connected Android devices"""
        try:
            result = subprocess.run(['adb', 'devices'],
                                  capture_output=True,
                                  text=True,
                                  timeout=5)
            lines = result.stdout.strip().split('\n')[1:]  # Skip header
            devices = [line.split()[0] for line in lines if line.strip() and 'device' in line]
            return devices
        except Exception as e:
            print(f"Error getting devices: {e}")
            return []

    def connect_device(self, device_id: Optional[str] = None) -> bool:
        """Connect to a specific device or the first available one"""
        devices = self.get_connected_devices()

        if not devices:
            print("No devices connected")
            return False

        if device_id:
            if device_id in devices:
                self.device_id = device_id
            else:
                print(f"Device {device_id} not found")
                return False
        else:
            self.device_id = devices[0]

        print(f"Connected to device: {self.device_id}")
        return True

    def execute_command(self, command: List[str]) -> Optional[str]:
        """Execute ADB shell command on connected device"""
        if not self.device_id:
            print("No device connected")
            return None

        try:
            cmd = ['adb', '-s', self.device_id] + command
            result = subprocess.run(cmd,
                                  capture_output=True,
                                  text=True,
                                  timeout=30)

            if result.returncode == 0:
                return result.stdout.strip()
            else:
                print(f"Command failed: {result.stderr}")
                return None
        except Exception as e:
            print(f"Error executing command: {e}")
            return None

    def get_app_usage_stats(self, days: int = 7) -> List[Dict]:
        """
        Get app usage statistics from Android device
        Requires UsageStatsManager permission
        """
        # Calculate timestamp for query (milliseconds since epoch)
        end_time = datetime.now()
        start_time = end_time - timedelta(days=days)

        start_ms = int(start_time.timestamp() * 1000)
        end_ms = int(end_time.timestamp() * 1000)

        # Query usage stats using dumpsys
        command = ['shell', 'dumpsys', 'usagestats']
        output = self.execute_command(command)

        if not output:
            return []

        # Parse the output to extract app usage data
        # This is a simplified parser - actual implementation may need refinement
        usage_data = self._parse_usage_stats(output)

        return usage_data

    def _parse_usage_stats(self, raw_output: str) -> List[Dict]:
        """Parse raw dumpsys usagestats output - focuses on daily stats section"""
        import re

        usage_data = []
        lines = raw_output.split('\n')
        in_daily_stats = False

        for line in lines:
            # Find the daily stats section
            if 'In-memory daily stats' in line:
                in_daily_stats = True
                continue

            # Stop when we hit the next section
            if in_daily_stats and ('In-memory weekly stats' in line or 'In-memory monthly stats' in line):
                break

            # Parse package usage lines
            # Format: package=com.example.app totalTimeUsed="12:34" ...
            if in_daily_stats and 'package=' in line and 'totalTimeUsed=' in line:
                # Extract package name
                package_match = re.search(r'package=([^\s]+)', line)
                # Extract totalTimeUsed
                time_match = re.search(r'totalTimeUsed="([^"]+)"', line)

                if package_match and time_match:
                    package = package_match.group(1)
                    time_str = time_match.group(1)

                    # Convert time string (HH:MM or MM:SS format) to milliseconds
                    time_ms = self._parse_time_to_ms(time_str)

                    # Only include apps with actual usage time
                    if time_ms > 0:
                        usage_data.append({
                            'package': package,
                            'time_used_ms': time_ms,
                            'timestamp': datetime.now().isoformat()
                        })

        return usage_data

    def _parse_time_to_ms(self, time_str: str) -> int:
        """Convert time string like '1:23:45' or '12:34' to milliseconds"""
        parts = time_str.split(':')

        try:
            if len(parts) == 3:
                # Format: HH:MM:SS
                hours = int(parts[0])
                minutes = int(parts[1])
                seconds = int(parts[2])
                return (hours * 3600 + minutes * 60 + seconds) * 1000
            elif len(parts) == 2:
                # Format: MM:SS
                minutes = int(parts[0])
                seconds = int(parts[1])
                return (minutes * 60 + seconds) * 1000
            else:
                return 0
        except (ValueError, IndexError):
            return 0

    def get_installed_apps(self) -> List[str]:
        """Get list of installed packages"""
        command = ['shell', 'pm', 'list', 'packages']
        output = self.execute_command(command)

        if not output:
            return []

        packages = [line.replace('package:', '') for line in output.split('\n') if line.startswith('package:')]
        return packages

    def get_screen_time_today(self) -> Dict:
        """Get total screen time for today"""
        command = ['shell', 'dumpsys', 'battery']
        output = self.execute_command(command)

        if not output:
            return {'screen_on_time': 0}

        # Parse screen on time from battery stats
        for line in output.split('\n'):
            if 'Screen on:' in line:
                time_str = line.split('Screen on:')[1].strip()
                return {'screen_on_time': time_str}

        return {'screen_on_time': 'N/A'}
