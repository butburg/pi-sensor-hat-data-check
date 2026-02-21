#!/usr/bin/env python3
"""
visualize_sensors.py
Project: Pi Sensor HAT
Description: Loads all CSV files from the last 14 days and plots
             interactive line charts for every sensor feature.
"""

import os
import glob
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import requests
from datetime import datetime, timedelta


DATA_URL = "http://192.168.0.72:8765/two_week_merge.json"
df = pd.read_json(DATA_URL)


# Load from Pi server
df = pd.DataFrame(requests.get(DATA_URL).json())

df["timestamp"] = pd.to_datetime(df["timestamp"], errors='coerce')
df = df.dropna(subset=["timestamp"])
df = df.sort_values("timestamp").reset_index(drop=True)

# Features to plot
features = [
    ("temperature", "Temperature", "°C"),
    ("humidity", "Humidity", "%RH"),
    ("pressure", "Pressure", "Pa"),
    ("eco2", "eCO2", "ppm"),
    ("air_quality_score", "Air Quality IAQ", "IAQ"),
    ("air_quality_percent", "Air Quality", "%"),
]

fig = make_subplots(
    rows=len(features),
    cols=1,
    shared_xaxes=True,
    subplot_titles=[f[1] for f in features],
    vertical_spacing=0.05
)

for i, (col, label, unit) in enumerate(features, start=1):
    fig.add_trace(
        go.Scatter(
            x=df["timestamp"],
            y=df[col],
            name=label,
            mode="lines",
            hovertemplate=f"%{{x}}<br>{label}: %{{y}} {unit}<extra></extra>"
        ),
        row=i, col=1
    )
    fig.update_yaxes(title_text=unit, row=i, col=1)

# Add night-time background shading (22:00 to 08:00)
min_date = df["timestamp"].min().date()
max_date = df["timestamp"].max().date()

current_date = min_date
while current_date <= max_date:
    night_start = pd.Timestamp(current_date, hour=22, minute=0)
    night_end = night_start + timedelta(days=1, hours=10)

    fig.add_vrect(
        x0=night_start,
        x1=night_end,
        fillcolor="rgba(100, 100, 120, 0.15)",
        layer="below",
        line_width=0
    )

    current_date += timedelta(days=1)

fig.update_layout(
    title="Pi Sensor HAT — Full History",
    height=300 * len(features),
    showlegend=False,
    hovermode="x unified"
)

fig.write_html("sensor_chart.html")
print("Saved to sensor_chart.html")