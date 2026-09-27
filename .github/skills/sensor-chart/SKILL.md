---
name: sensor-chart
description: 'Local Plotly chart of the Pi sensor data (visualize_sensors.py). Use whenever generating, fixing, or extending sensor_chart.html.'
---

# Local sensor chart

- `uv run visualize_sensors.py [--url URL] [--out FILE]` → `sensor_chart.html` (gitignored, plotly.js via CDN). Python 3.12, deps in pyproject.
- Source = `two_week_merge.json` from the Pi (see pi-sensor-stack); URL from `--url` > env `SENSOR_DATA_URL` (value in `AGENTS.local.md`) > `raspberrypi.local` default. Fetch retries on invalid JSON.
- `FEATURES` list = subplots; columns missing/empty in data are skipped (e.g. `gas_resistance` in old rows).
- Lines use `line_shape="hv"` (value held until next reading); night 22–08 shaded.
- Shell warns `VIRTUAL_ENV ... does not match` → harmless, uv uses `.venv`.
