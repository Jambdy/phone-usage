#!/usr/bin/env python3
"""
Phone Usage Data Collector
CLI tool to collect app usage data from Android device via ADB
"""
import argparse
from adb_connector import ADBConnector
from data_storage import DataStorage


def main():
    parser = argparse.ArgumentParser(
        description='Collect app usage data from Android device'
    )
    parser.add_argument(
        '--days',
        type=int,
        default=7,
        help='Number of days of usage data to collect (default: 7)'
    )
    parser.add_argument(
        '--device',
        type=str,
        help='Specific device ID to connect to (optional)'
    )
    parser.add_argument(
        '--list-devices',
        action='store_true',
        help='List available devices and exit'
    )

    args = parser.parse_args()

    # Initialize
    adb = ADBConnector()
    storage = DataStorage()

    # Check ADB installation
    if not adb.check_adb_installed():
        print("ERROR: ADB is not installed or not in PATH")
        print("Please install Android SDK Platform Tools")
        return 1

    # List devices if requested
    if args.list_devices:
        devices = adb.get_connected_devices()
        if devices:
            print(f"Found {len(devices)} connected device(s):")
            for device in devices:
                print(f"  - {device}")
        else:
            print("No devices connected")
        return 0

    # Connect to device
    print("Connecting to device...")
    if not adb.connect_device(args.device):
        print("ERROR: Failed to connect to device")
        print("Make sure:")
        print("  1. Device is connected via USB")
        print("  2. USB debugging is enabled")
        print("  3. Device is authorized (check device screen)")
        print("\nRun with --list-devices to see available devices")
        return 1

    print(f"Connected to: {adb.device_id}")

    # Collect usage data
    print(f"\nCollecting usage data for the last {args.days} days...")
    usage_data = adb.get_app_usage_stats(days=args.days)

    if not usage_data:
        print("WARNING: No usage data retrieved")
        print("This may be due to:")
        print("  1. No apps have been used")
        print("  2. Usage stats permission not granted")
        print("  3. Android version compatibility issues")
        return 1

    print(f"Retrieved {len(usage_data)} usage records")

    # Save to file
    print("\nSaving data...")
    if storage.save_usage_data(usage_data):
        print(f"Data saved successfully to: {storage.data_file}")
        print(f"Total records in storage: {len(storage.get_all_records())}")

        # Show summary
        summary = storage.get_summary_by_app()
        print(f"\nTop 5 most used apps:")
        for i, (package, time_ms) in enumerate(
            sorted(summary.items(), key=lambda x: x[1], reverse=True)[:5], 1
        ):
            hours = time_ms / (1000 * 60 * 60)
            print(f"  {i}. {package}: {hours:.2f} hours")

        return 0
    else:
        print("ERROR: Failed to save data")
        return 1


if __name__ == '__main__':
    exit(main())
