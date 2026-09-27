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
| `AGENTS.local.example.md` | Template for your machine-specific agent config (copy to the gitignored `AGENTS.local.md`) |

## Setting up the Pi

Tested on Raspberry Pi OS (Bookworm, Python 3.11) with the HAT attached and I²C enabled
(`sudo raspi-config` → Interface Options → I2C). The systemd units and cron entry assume
user `pi` and the project at `/home/pi/pi-sensor-project/`. Adjust the paths in
`pi/system/` if yours differ.

```bash
# on your PC
rsync -av pi/ pi@<pi-host>:pi-sensor-project/

# on the Pi
cd ~/pi-sensor-project
python3 -m venv venv
venv/bin/pip install -r requirements.txt
sudo cp system/*.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable --now air-quality-monitor csvserver
crontab system/crontab   # replaces your crontab; use `crontab -e` to merge instead
```

`csvserver` serves the `data/` folder on port 8765 **without authentication** to everyone
on your network. Don't forward that port to the internet.

### Home Assistant (optional)

Add a [RESTful](https://www.home-assistant.io/integrations/rest/) resource that polls
`http://<pi-host>:8765/two_week_merge.json` and reads the latest row with
`value_json[-1].<field>`, for example `value_json[-1].temperature`.

## Local chart

Requires [uv](https://docs.astral.sh/uv/) and access to the Pi on the LAN.

```bash
export SENSOR_DATA_URL=http://<pi-host>:8765/two_week_merge.json   # default: raspberrypi.local
uv run visualize_sensors.py            # writes sensor_chart.html
uv run visualize_sensors.py --help     # --url / --out options
```

Open `sensor_chart.html` in a browser. From WSL, `explorer.exe sensor_chart.html` opens it in
the Windows default browser. The chart shows one panel per value, with night hours
(22:00–08:00) shaded. The file is generated, so it is not committed.

## Working on the Pi

`pi/` is kept identical to the Pi: edit locally, then deploy.

```bash
# Deploy local changes (never use --delete: data/ and venv/ only exist on the Pi)
rsync -av --exclude venv --exclude data --exclude __pycache__ --exclude '*.log' \
  --exclude '*.bak-*' --exclude baselines.txt --exclude system \
  pi/ pi@<pi-host>:pi-sensor-project/

# After changing monitor.py or config.py
ssh pi@<pi-host> 'sudo systemctl restart air-quality-monitor'

# Live log
ssh pi@<pi-host> 'journalctl -u air-quality-monitor -f'
```

After a restart, the monitor recalibrates its baseline for about 5 minutes, so no rows
are logged during that time.

## Data format

CSV columns: `timestamp, temperature, humidity, pressure (Pa), eco2, air_quality_percent,
air_quality_score, gas_resistance (Ω)`. The merged JSON uses the same fields, with
pressure in hPa.

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

## License

[MIT](LICENSE). The example scripts in `pi/scripts/` are © Kitronik Ltd (also MIT), see
[pi/scripts/README.md](pi/scripts/README.md).
