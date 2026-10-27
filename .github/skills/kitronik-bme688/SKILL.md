---
name: kitronik-bme688
description: 'What the Kitronik Air Quality Control HAT / BME688 really measures, and how eCO2/IAQ are computed. Use whenever questioning sensor values, resolution, steps, eCO2 accuracy, or calibration.'
---

# Kitronik HAT / BME688 facts

- Only gas sensor = Bosch BME688 (MOX, VOC). **No real CO2 sensor.** Real CO2 would need NDIR (SCD40/41, SenseAir S8).
- Library: `venv/lib/python3.11/site-packages/KitronikAirQualityControlHAT.py`, `calcAirQuality()` ~L965. Kitronik's own formula, not Bosch BSEC:
  `iaqPercent = trunc(humScore + gasScore)` → `iaqScore = (100-iaqPercent)*5` → `eCO2 = trunc(250·e^(0.012·iaqScore))` (× hum/temp ratio if hum > 40 % / temp > baseline temp, +1500 if hum rose ≥3 %-pts since last read).
- Humidity reference = fixed 40 % (not measured) → higher RH lowers the score *and* multiplies eCO2 by RH/40: same air 40 % → 337 ppm, 60 % → 868 ppm (×2.6). "Breath" +1500 time check is dead code → fires at any interval.
- ⇒ eco2, score, percent are 1:1 coupled and step in 6.2 % (513, 545, 579, 614…). Not a bug.
- Humidity integer too (`hRead // 1000`, ~L673). Temperature/pressure fine.
- Only continuous air value = `readGasRes()` (Ω) → logged as `gas_resistance` (not in HA, user decision).
- Baseline: `calcBaselines(oled)` reuses `baselines.txt` in the working dir (`my_sensor_tracker/`, from 2026-02-15, verified 2026-10-22); only without file → 60×5 s ≈ 5 min. Recalibrate = `calcBaselines(oled, forcedRun=True)` (code comment `calcBaselines(True)` is wrong) or delete the file — ask user first. monitor.py's "Always calculate a fresh baseline" is misleading.
- Never patch the venv library (lost on reinstall) — compute derived values in monitor.py instead. Smooth eCO2 (no trunc) = ask user first; it adds no real info.
- Refs: github.com/KitronikLtd/Kitronik-Raspberry-Pi-Air-Quality-Control-HAT-Python · Bosch BME688 datasheet (bst-bme688-ds000.pdf).
