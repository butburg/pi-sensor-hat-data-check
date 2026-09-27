# pi-sensor-hat-data-check

Repo for the Raspberry Pi with the Kitronik Air Quality Control HAT (BME688):
sensor code on the Pi (mirrored in `pi/`), its Home Assistant integration,
and a local Plotly chart of the data.

Skills live at `.github/skills/SKILLNAME/SKILL.md`.

skills (load order = dependency order, each requires the one(s) before it):
- ssh-pi-sensor — connect to the sensor Pi
- pi-sensor-stack — services, data flow, local pi/ mirror and deploy rules (requires ssh-pi-sensor)
- kitronik-bme688 — what the sensor really measures, eCO2/IAQ formula and its steps (requires pi-sensor-stack)
- homeassistant-sensor — REST sensors in Home Assistant, change procedure (requires pi-sensor-stack)
- sensor-chart — local visualize_sensors.py chart (requires pi-sensor-stack)
- git-commits — commit message style for this repo (standalone, no dependency)
- skill-writing — rules for writing/tightening skills, token-optimized (standalone, no dependency)

## Usage

Load the relevant skill before touching the Pi or HA. Don't guess connection
details or paths — they're documented in the skills; if something's missing,
ask the user rather than assuming.

Machine-specific values (hosts, IPs, users, keys) are not in the repo. Skills use
placeholders like `<pi-ssh>`; the real values are in `AGENTS.local.md`
(gitignored, template `AGENTS.local.example.md`). Read it before connecting
anywhere. Missing → ask the user to create it from the template.

Local `pi/` must match the Pi. Edit locally, deploy with rsync, and pull
first if the Pi drifted (see pi-sensor-stack).

## Time

Things can change. If you do something more than once or learn something new,
ask the user whether to add it as a skill, next to the actual answer — like:
"Btw, I used [process] multiple times, should we add it as skill?" You can also
change or improve skills, but let the user know.
