---
name: homeassistant-sensor
description: 'How the Pi sensor data gets into Home Assistant (REST sensors) and how to change it safely. Use whenever HA entities sensor.sensor_*, history gaps, statistics or HA config for this sensor come up.'
---

# Home Assistant side

- HA runs in Docker on a separate host: `ssh <ha-ssh>` (fallback `<ha-fallback>`), container `<ha-container>`, config `<ha-config>` → real values + host notes in `AGENTS.local.md`.
- `configuration.yaml` → `rest:` resource `http://<pi-host>:8765/two_week_merge.json`, `scan_interval: 60`, reads `value_json[-1].<field>`.
- Entities `sensor.sensor_{temperature,humidity,pressure,eco2,air_quality_score,air_quality_percent}`; `unique_id: pi_sensor_*`, `state_class: measurement` (→ long-term stats: 5-min/hourly mean/min/max).
- No gas_resistance in HA (user decision).

## Change procedure

1. `cp configuration.yaml configuration.yaml.bak-$(date +%F)`
2. Edit, then `docker exec <ha-container> python3 -m homeassistant --script check_config -c /config`
3. `docker restart <ha-container>` (or reload via API if a token is available), check `home-assistant.log`.

## Gotchas

- History rows only on state *change* → gaps = unchanged value (see kitronik-bme688 steps), not missing data.
- Adding `unique_id` later keeps entity_id and history (verified 2026-09-27).
- `unavailable` for ~100 s = one failed poll (timeout 4 s or invalid JSON).
