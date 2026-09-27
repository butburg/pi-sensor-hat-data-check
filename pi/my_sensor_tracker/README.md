# Air Quality Monitor

Continuous logging of temperature, humidity, pressure and air-quality values on a Raspberry Pi
with the Kitronik Air Quality Control HAT (BME688). It also shows the readings on the HAT's OLED
and uses its three ZIP LEDs as traffic lights.

## Components

| File | Role |
|---|---|
| `monitor.py` | Main loop: measure, update OLED + LEDs, append to `data/YYYY-MM-DD.csv` (systemd `air-quality-monitor`) |
| `config.py` | Interval, LED thresholds, brightness, temperature calibration |
| `merge_json.py` | Merges the last 14 days into `data/two_week_merge.json` (cron, every 5 min) |
| `plain_sensor_print.py` | Debug: print raw readings every second (stop the service first) |
| `tests/` | pytest tests for the LED mapping |

`data/` is served on port 8765 by the systemd service `csvserver` (`python3 -m http.server`).
Home Assistant and the chart script read `two_week_merge.json` from there.

## Manual start (testing)

```bash
sudo systemctl stop air-quality-monitor
cd ~/pi-sensor-project/my_sensor_tracker
source ../venv/bin/activate
python3 monitor.py
```

On every start the monitor recalibrates its baseline for about 5 minutes, with progress on the
OLED. After that it measures every `UPDATE_INTERVAL` seconds (60 by default). Stop it with
`Ctrl+C`, then start the service again.

## LED indicators

| LED | Metric | 🟢 Green | 🟡 Yellow | 🔴 Red |
|---|---|---|---|---|
| 1 | Temperature (corrected) | 20–25 °C | 16–28 °C | outside |
| 2 | Humidity vs. temperature | within ideal RH ± 15 % | within ± 20 % | outside |
| 3 | eCO2 | ≤ 800 ppm | ≤ 1200 ppm | > 1200 ppm |

The ideal RH for LED 2 is `35 + 0.5 × temperature` (temperature clamped to 10–40 °C) and is
limited to 20–90 %. All thresholds are set in `config.py`.

## Data files

`data/YYYY-MM-DD.csv`, one file per day:

```
timestamp,temperature,humidity,pressure,eco2,air_quality_percent,air_quality_score,gas_resistance
2026-09-27 19:53:01,23.46,21.00,101682.00,513.00,88.00,60.00,420200
```

- `pressure` is in Pa in the CSV and in hPa in `two_week_merge.json`.
- `gas_resistance` is the raw BME688 reading in Ω.

## Notes on the values

- `eco2` is **not measured**. The Kitronik library estimates it from the air-quality score, which
  it derives from gas resistance and humidity. The score is truncated to steps of 5, so
  `eco2`, `air_quality_score` and `air_quality_percent` change together in coarse steps (about
  6 % for eCO2).
- Humidity is reported as whole percent by the library.
- `temperature` is corrected with the two-point calibration in `config.py`
  (`TEMPERATURE_CALIBRATION`), because the board heats up the sensor.

## Service management

```bash
sudo systemctl status air-quality-monitor
sudo systemctl restart air-quality-monitor   # after changing monitor.py / config.py
journalctl -u air-quality-monitor -f         # live log
journalctl -u air-quality-monitor --since today
```

`merge_json.py` needs no restart. Its output goes to `merge_json.log`.

## Troubleshooting

- **No new CSV rows:** check `systemctl status air-quality-monitor`. Right after a (re)start, wait
  about 5 minutes for the calibration.
- **Hardware check:** `python3 ../scripts/test_all.py` in the venv, with the service stopped.
