# Local setup (template)

Copy to `AGENTS.local.md` (gitignored) and fill in your values. Skills refer to the
`<keys>` below; agents read `AGENTS.local.md` for the real values. Never commit it.

## Sensor Pi

- `<pi-ssh>` = SSH alias for the Pi, e.g. `pi-sensor` (in `~/.ssh/config`)
- `<pi-host>` = Pi hostname or LAN IP, e.g. `raspberrypi.local`
- `<pi-user>` = login user, e.g. `pi`
- `<pi-key>` = SSH key file, e.g. `~/.ssh/id_ed25519`
- sudo without password for `systemctl`: yes/no
- Other services on the Pi that agents must not touch: …

## Home Assistant

- `<ha-ssh>` = SSH target for the HA host, e.g. `user@homeassistant.local`
- `<ha-fallback>` = fallback IP if mDNS fails
- `<ha-container>` = Docker container name, e.g. `homeassistant`
- `<ha-config>` = config dir on the host (mounted as `/config`), e.g. `/path/to/homeassistant/`
- Notes (e.g. managed by a NAS UI or not, API token available or not): …

## Chart

- `SENSOR_DATA_URL` = `http://<pi-host>:8765/two_week_merge.json` (env var for `visualize_sensors.py`)
