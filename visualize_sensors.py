#!/usr/bin/env python3
"""
visualize_sensors.py
Project: Pi Sensor HAT
Description: Loads the merged 14-day JSON from the Pi and plots
             interactive line charts for every sensor feature.
Usage: uv run visualize_sensors.py [--url URL] [--out FILE]
       URL defaults to $SENSOR_DATA_URL, else raspberrypi.local.
"""

import argparse
import os
import sys
import time
from datetime import timedelta

import pandas as pd
import plotly.graph_objects as go
import requests
from plotly.subplots import make_subplots

DATA_URL = os.environ.get(
    "SENSOR_DATA_URL", "http://raspberrypi.local:8765/two_week_merge.json"
)
OUTPUT_FILE = "sensor_chart.html"

# (column, label, unit)
FEATURES = [
    ("temperature", "Temperature", "°C"),
    ("humidity", "Humidity", "%RH"),
    ("pressure", "Pressure", "hPa"),
    ("eco2", "eCO2 (estimated from VOC)", "ppm"),
    ("air_quality_score", "Air Quality IAQ", "IAQ"),
    ("air_quality_percent", "Air Quality", "%"),
    ("gas_resistance", "Gas Resistance (raw)", "Ω"),
]


def fetch_records(url, attempts=3):
    """Fetch the merged JSON; retry if the request fails or the JSON is invalid."""
    for attempt in range(1, attempts + 1):
        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            return response.json()
        except (requests.RequestException, ValueError) as e:
            print(f"[WARN] Attempt {attempt}/{attempts} failed: {e}", file=sys.stderr)
            if attempt < attempts:
                time.sleep(3)
    sys.exit(f"[ERROR] Could not load valid JSON from {url}")


def build_figure(df):
    features = [f for f in FEATURES if f[0] in df and df[f[0]].notna().any()]

    fig = make_subplots(
        rows=len(features),
        cols=1,
        shared_xaxes=True,
        subplot_titles=[f[1] for f in features],
        vertical_spacing=0.04,
    )

    for i, (col, label, unit) in enumerate(features, start=1):
        fig.add_trace(
            go.Scatter(
                x=df["timestamp"],
                y=df[col],
                name=label,
                mode="lines",
                line_shape="hv",  # values are held until the next reading
                hovertemplate=f"%{{x}}<br>{label}: %{{y}} {unit}<extra></extra>",
            ),
            row=i,
            col=1,
        )
        fig.update_yaxes(title_text=unit, row=i, col=1)

    # Night-time background shading (22:00 to 08:00)
    day = df["timestamp"].min().normalize() - timedelta(days=1)
    while day <= df["timestamp"].max():
        night_start = day + timedelta(hours=22)
        fig.add_vrect(
            x0=night_start,
            x1=night_start + timedelta(hours=10),
            fillcolor="rgba(100, 100, 120, 0.15)",
            layer="below",
            line_width=0,
        )
        day += timedelta(days=1)

    fig.update_layout(
        title=f"Pi Sensor HAT — last 14 days (latest: {df['timestamp'].max():%Y-%m-%d %H:%M})",
        height=260 * len(features),
        showlegend=False,
        hovermode="x unified",
    )
    return fig


def main():
    parser = argparse.ArgumentParser(description=__doc__.split("Usage")[0])
    parser.add_argument("--url", default=DATA_URL, help=f"merged JSON URL (default: {DATA_URL})")
    parser.add_argument("--out", default=OUTPUT_FILE, help=f"output HTML (default: {OUTPUT_FILE})")
    args = parser.parse_args()

    df = pd.DataFrame(fetch_records(args.url))
    df["timestamp"] = pd.to_datetime(df["timestamp"], format="%Y-%m-%d %H:%M:%S", errors="coerce")
    df = df.dropna(subset=["timestamp"]).sort_values("timestamp").reset_index(drop=True)
    if df.empty:
        sys.exit("[ERROR] No rows with a valid timestamp")

    build_figure(df).write_html(args.out, include_plotlyjs="cdn")
    print(f"Saved {len(df)} rows to {args.out}")


if __name__ == "__main__":
    main()
