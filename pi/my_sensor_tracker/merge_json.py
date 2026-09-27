#!/usr/bin/env python3
"""
merge_json.py
Project: Pi Sensor HAT
Description: Collects sensor CSV data from the last 14 days and merges
             them into a single JSON file (two_week_merge.json) for
             consumption by Home Assistant and Grafana.
Runs: every 5 minutes via cron
"""

import os
import csv
import json
from datetime import datetime, timedelta

DATA_DIR = "/home/pi/pi-sensor-project/my_sensor_tracker/data"
OUTPUT_FILE = os.path.join(DATA_DIR, "two_week_merge.json")

def collect_data():
    records = []
    today = datetime.now().date()

    # Oldest day first; rows inside a CSV are already in logging order
    for i in reversed(range(14)):
        date = today - timedelta(days=i)
        filename = os.path.join(DATA_DIR, f"{date}.csv")
        if not os.path.exists(filename):
            continue
        with open(filename, newline="") as f:
            reader = csv.DictReader(f)
            for row in reader:
                # Convert pressure from Pa to hPa
                row["temperature"] = float(row["temperature"])
                row["humidity"] = float(row["humidity"])
                row["pressure"] = round(float(row["pressure"]) / 100, 2)
                row["eco2"] = float(row["eco2"])
                row["air_quality_percent"] = float(row["air_quality_percent"])
                row["air_quality_score"] = float(row["air_quality_score"])
                # gas_resistance (Ohm) only exists in rows logged after 2026-09-27
                gas = row.get("gas_resistance")
                row["gas_resistance"] = float(gas) if gas else None
                records.append(row)

    # No sort by timestamp string: rows logged before 2026-09-27 used "%H:%S"
    # (minute missing) and would get shuffled within each hour
    return records

def main():
    records = collect_data()
    # Write to a temp file and swap it in atomically, so the HTTP server
    # never serves a half-written file (-> JSON parse errors in HA/clients)
    tmp_file = OUTPUT_FILE + ".tmp"
    with open(tmp_file, "w") as f:
        json.dump(records, f, indent=2)
    os.replace(tmp_file, OUTPUT_FILE)
    print(f"[{datetime.now()}] Merged {len(records)} records into {OUTPUT_FILE}")

if __name__ == "__main__":
    main()
