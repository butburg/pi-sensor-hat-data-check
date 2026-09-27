---
name: ssh-pi-sensor
description: 'How to connect to the Raspberry Pi with the Kitronik sensor HAT via SSH. Use whenever checking, deploying to, or troubleshooting anything on the Pi / sensor.'
---

# SSH to the sensor Pi

- Real host/user/key values: `AGENTS.local.md` (keys `<pi-ssh>`, `<pi-host>`, `<pi-user>`, `<pi-key>`). Missing → ask user, don't guess.
- `ssh -o BatchMode=yes <pi-ssh> "<cmd>"` · `rsync`/`scp` work with the alias.
- Use `sudo -n` for `systemctl`; fails → passwordless sudo not set up, ask user.
- `Permission denied` although "Server accepts key" → key has a passphrase and no agent in the shell → ask user to load the key into an agent.
- Other services may run on this Pi (listed in `AGENTS.local.md`) — don't touch.
- Load pi-sensor-stack next before changing anything.
