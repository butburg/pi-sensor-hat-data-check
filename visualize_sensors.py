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


def parse_timestamps(df):
    """Parse timestamps, repairing rows logged with the old '%H:%S' bug.

    On 2026-09-27 (01:24-19:47) monitor.py logged 'YYYY-MM-DD HH:SS'
    (minute missing). Those rows are still in logging order, so each one is
    placed ~61 s (the logging cadence) from its neighbours inside its hour:
    the first hour of a legacy block is anchored to the hour's end, all
    others to the hour's start. An approximation that avoids zig-zag lines.
    """
    ts = df["timestamp"].astype(str)
    legacy = ts.str.len() == 16  # 'YYYY-MM-DD HH:SS' vs 'YYYY-MM-DD HH:MM:SS'

    parsed = pd.to_datetime(ts.where(~legacy), format="%Y-%m-%d %H:%M:%S", errors="coerce")

    hour = pd.to_datetime(ts.where(legacy).str[:13], format="%Y-%m-%d %H", errors="coerce")
    group = (hour != hour.shift()).cumsum()
    pos = df.groupby(group).cumcount()
    size = df.groupby(group)["timestamp"].transform("size")
    step = (3600 / size).clip(upper=61)
    block_start = legacy & ~legacy.shift(fill_value=False)
    first_hour = block_start.groupby(group).transform("any")
    offset = (3600 - (size - pos) * step).where(first_hour, pos * step)
    approx = hour + pd.to_timedelta(offset, unit="s")

    df["timestamp"] = parsed.where(~legacy, approx)
    df = df.dropna(subset=["timestamp"])
    return df.sort_values("timestamp", kind="stable").reset_index(drop=True)


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

    df = parse_timestamps(pd.DataFrame(fetch_records(args.url)))
    if df.empty:
        sys.exit("[ERROR] No rows with a valid timestamp")

    build_figure(df).write_html(args.out, include_plotlyjs="cdn")
    print(f"Saved {len(df)} rows to {args.out}")


if __name__ == "__main__":
    main()
