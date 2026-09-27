---
name: ssh-pi-sensor
description: 'How to connect to the Raspberry Pi with the Kitronik sensor HAT via SSH. Use whenever checking, deploying to, or troubleshooting anything on the Pi / sensor / <pi-host>.'
---

# SSH to the sensor Pi

- Alias `pi-sensor` in `~/.ssh/config` → `pi@<pi-host>` (hostname `raspberrypi`), key `~/.ssh/id_ed25519`.
- `ssh -o BatchMode=yes pi-sensor "<cmd>"` · `rsync`/`scp` work with the alias.
- `sudo -n` works for `systemctl`.
- `Permission denied` although "Server accepts key" → key has a passphrase, no agent in the shell → regenerate key without passphrase (ask user; they run `ssh-copy-id` with the Pi password).
- Other stuff runs on this Pi too (<other-services>) — don't touch.
- Load pi-sensor-stack next before changing anything.
