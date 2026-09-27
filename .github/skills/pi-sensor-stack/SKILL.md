---
name: pi-sensor-stack
description: 'Layout, services, data flow and deploy rules for the sensor code on the Pi and its local mirror in pi/. Use whenever editing monitor.py, merge_json.py, config.py, the systemd units/cron, or the CSV/JSON data.'
---

# Sensor stack on the Pi

Requires ssh-pi-sensor first.

## Layout

- Local `pi/` = mirror of Pi `~/pi-sensor-project/` (minus `venv/`, `data/`, logs, `baselines.txt`, `__pycache__`, `*.bak-*`). `pi/system/` = copies of `/etc/systemd/system/*.service` + `crontab -l`.
- Code: `my_sensor_tracker/{monitor.py,config.py,merge_json.py}`; `scripts/` = Kitronik example/test scripts.
- venv `~/pi-sensor-project/venv` (python3.11), library `KitronikAirQualityControlHAT` from PyPI.

## Data flow

`air-quality-monitor.service` (monitor.py, every `UPDATE_INTERVAL`=60 s) → `data/YYYY-MM-DD.csv` → cron `*/5` `merge_json.py` → `data/two_week_merge.json` (14 days, oldest first) → `csvserver.service` (`python3 -m http.server 8765` in `data/`) → HA REST + `visualize_sensors.py`.
CSV cols: `timestamp,temperature,humidity,pressure(Pa),eco2,air_quality_percent,air_quality_score,gas_resistance(Ω)`; JSON has pressure in hPa.

## Deploy / sync rules

1. Edit locally in `pi/`, then `rsync -av --exclude venv --exclude data --exclude __pycache__ --exclude '*.log' --exclude '*.bak-*' --exclude baselines.txt --exclude system pi/ <pi-ssh>:pi-sensor-project/` (never `--delete`). `pi/system/` → install manually with sudo (`/etc/systemd/system/`, `daemon-reload`) / `crontab -e`.
2. Drift check: same rsync with `-nci` (dry-run, checksum) in both directions; only `.d..t` dir lines = in sync. Pi changed? → pull into `pi/` first, then edit.
3. Before editing on the Pi: `cp X X.bak-$(date +%F)`.
4. monitor.py/config.py change → `ssh <pi-ssh> sudo -n systemctl restart air-quality-monitor` → ~5 min baseline calibration, no rows meanwhile. merge_json.py → no restart, run it once to test.

## Gotchas

- CSV lines end `\r\n` (csv.writer) → sed on header needs `\r$`.
- New CSV column → also patch header of today's CSV, and make merge_json tolerate missing values in old rows.
- 2026-09-27 01:24–19:47 rows have `%H:%S` timestamps (minute lost, bug fixed) → never sort by timestamp string; merge_json keeps file order.
- merge_json must write atomically (tmp + `os.replace`) — http.server else serves half files → `ValueError: Expected object or value` / HA `unavailable`.
