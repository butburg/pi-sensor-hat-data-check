# Pi Sensor HAT — Data Collection & Visualization

[![ko-fi](https://ko-fi.com/img/githubbutton_sm.svg)](https://ko-fi.com/O4O111DFT3)

A Raspberry Pi with the [Kitronik Air Quality Control HAT](https://kitronik.co.uk/blogs/resources/kitronik-air-quality-control-hat-raspberry-pi-introduction-quick-start-guide)
logs temperature, humidity, pressure and air-quality values every minute. The data is
served on the LAN, pulled into Home Assistant, and can be plotted locally as an
interactive chart.

## Data flow

```
BME688 on HAT
  └─ monitor.py (systemd: air-quality-monitor, every 60 s)
       └─ data/YYYY-MM-DD.csv
            └─ merge_json.py (cron, every 5 min) → data/two_week_merge.json (last 14 days)
                 └─ http.server :8765 (systemd: csvserver)
                      ├─ Home Assistant REST sensors (sensor.sensor_*)
                      └─ visualize_sensors.py → sensor_chart.html
```

## Repository layout

| Path | What |
|---|---|
| `pi/` | Mirror of `~/pi-sensor-project/` on the Pi (`my_sensor_tracker/`, Kitronik `scripts/`, `requirements.txt`) |
| `pi/system/` | Copies of the systemd units and the crontab entry on the Pi |
| `visualize_sensors.py` | Local chart generator |
| `AGENTS.md`, `.github/skills/` | Instructions and skills for coding agents working on this project |

`pi/` is kept identical to the Pi: edit locally, then deploy (see below).

## Local chart

Requires [uv](https://docs.astral.sh/uv/) and access to the Pi on the LAN.

```bash
uv run visualize_sensors.py            # writes sensor_chart.html
uv run visualize_sensors.py --help     # --url / --out options
```

Open `sensor_chart.html` in a browser. From WSL, `explorer.exe sensor_chart.html` opens it in
the Windows default browser. The chart shows one panel per value, with night hours
(22:00–08:00) shaded. The file is generated, so it is not committed.

## Working on the Pi

SSH alias `pi-sensor` (`pi@<pi-host>`) is set up in `~/.ssh/config`.

```bash
# Deploy local changes
rsync -av --exclude venv --exclude data --exclude __pycache__ --exclude '*.log' \
  --exclude '*.bak-*' --exclude baselines.txt --exclude system \
  pi/ pi-sensor:pi-sensor-project/

# After changing monitor.py or config.py
ssh pi-sensor 'sudo systemctl restart air-quality-monitor'

# Live log
ssh pi-sensor 'journalctl -u air-quality-monitor -f'
```

After a restart, the monitor recalibrates its baseline for about 5 minutes, so no rows
are logged during that time.

## Data format

CSV columns: `timestamp, temperature, humidity, pressure (Pa), eco2, air_quality_percent,
air_quality_score, gas_resistance (Ω)`. The merged JSON uses the same fields, with
pressure in hPa. `gas_resistance` has been logged since 2026-09-27. Older rows have `null`.

## About the values

The HAT has **no real CO₂ sensor**. Its only gas sensor is a Bosch BME688, a metal-oxide
sensor that reacts to volatile organic compounds (VOCs).

- The Kitronik library derives `air_quality_percent`, `air_quality_score` and `eco2` from
  the gas resistance and humidity. It uses its own formula, not Bosch BSEC. Because the
  percent value is truncated to an integer, all three values move together in coarse steps
  (for eCO₂: 513 → 545 → 579 → 614 ppm, about 6 % each).
- Humidity is reported as whole percent.
- `gas_resistance` is the raw, continuous sensor reading.

In Home Assistant, a new history row only appears when a value *changes*. Long flat
stretches in the history therefore mean the value stayed on one step, not that data is
missing.

## Known data quirk

Rows logged on 2026-09-27 between 01:24 and 19:47 have timestamps in the form
`YYYY-MM-DD HH:SS`: the minute was lost because of a bug that has since been fixed. The
rows are still in the right order. `visualize_sensors.py` estimates their times inside
each hour.
