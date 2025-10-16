"""
Data Storage Module
Handles saving and loading app usage data to/from local JSON file
"""
import json
import os
from datetime import datetime
from typing import List, Dict, Optional


class DataStorage:
    """Manages local JSON file storage for app usage data"""

    def __init__(self, data_dir: str = '../data'):
        self.data_dir = data_dir
        self.data_file = os.path.join(data_dir, 'usage_data.json')
        # Also save to frontend public directory for dashboard access
        self.frontend_data_file = os.path.join('..', 'frontend', 'public', 'data', 'usage_data.json')
        self._ensure_data_dir()

    def _ensure_data_dir(self):
        """Create data directory if it doesn't exist"""
        os.makedirs(self.data_dir, exist_ok=True)

        # Ensure frontend public/data directory exists
        frontend_data_dir = os.path.dirname(self.frontend_data_file)
        os.makedirs(frontend_data_dir, exist_ok=True)

        # Initialize empty data file if it doesn't exist
        if not os.path.exists(self.data_file):
            self._write_data({'records': [], 'last_updated': None})

    def _read_data(self) -> Dict:
        """Read data from JSON file"""
        try:
            with open(self.data_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (json.JSONDecodeError, FileNotFoundError):
            return {'records': [], 'last_updated': None}

    def _write_data(self, data: Dict):
        """Write data to JSON file"""
        # Write to main data directory
        with open(self.data_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

        # Also write to frontend public directory
        try:
            with open(self.frontend_data_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Warning: Could not write to frontend directory: {e}")

    def save_usage_data(self, usage_records: List[Dict]) -> bool:
        """
        Save app usage records to file

        Args:
            usage_records: List of usage records with structure:
                [{
                    'package': str,
                    'time_used_ms': int,
                    'timestamp': str (ISO format),
                    'app_name': str (optional)
                }]
        """
        try:
            data = self._read_data()

            # Add timestamp to each record if not present
            for record in usage_records:
                if 'timestamp' not in record:
                    record['timestamp'] = datetime.now().isoformat()

            # Append new records
            data['records'].extend(usage_records)
            data['last_updated'] = datetime.now().isoformat()

            self._write_data(data)
            return True
        except Exception as e:
            print(f"Error saving data: {e}")
            return False

    def get_all_records(self) -> List[Dict]:
        """Get all stored usage records"""
        data = self._read_data()
        return data.get('records', [])

    def get_records_by_date_range(self, start_date: str, end_date: str) -> List[Dict]:
        """
        Get records within a date range

        Args:
            start_date: ISO format date string
            end_date: ISO format date string
        """
        all_records = self.get_all_records()

        start = datetime.fromisoformat(start_date)
        end = datetime.fromisoformat(end_date)

        filtered = [
            record for record in all_records
            if start <= datetime.fromisoformat(record['timestamp']) <= end
        ]

        return filtered

    def get_records_by_package(self, package_name: str) -> List[Dict]:
        """Get all records for a specific package"""
        all_records = self.get_all_records()
        return [r for r in all_records if r.get('package') == package_name]

    def get_summary_by_app(self) -> Dict[str, int]:
        """
        Get total usage time per app across all records

        Returns:
            Dict mapping package name to total time in milliseconds
        """
        all_records = self.get_all_records()
        summary = {}

        for record in all_records:
            package = record.get('package', 'unknown')
            time_used = record.get('time_used_ms', 0)

            if package in summary:
                summary[package] += time_used
            else:
                summary[package] = time_used

        return summary

    def get_last_updated(self) -> Optional[str]:
        """Get timestamp of last data update"""
        data = self._read_data()
        return data.get('last_updated')

    def clear_all_data(self) -> bool:
        """Clear all stored data (use with caution)"""
        try:
            self._write_data({'records': [], 'last_updated': None})
            return True
        except Exception as e:
            print(f"Error clearing data: {e}")
            return False

    def export_to_csv(self, output_file: str) -> bool:
        """Export data to CSV file"""
        try:
            import csv

            records = self.get_all_records()

            if not records:
                return False

            with open(output_file, 'w', newline='', encoding='utf-8') as f:
                if records:
                    writer = csv.DictWriter(f, fieldnames=records[0].keys())
                    writer.writeheader()
                    writer.writerows(records)

            return True
        except Exception as e:
            print(f"Error exporting to CSV: {e}")
            return False
