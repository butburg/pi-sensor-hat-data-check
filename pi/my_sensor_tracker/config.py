"""
Air Quality Monitor Configuration
LED thresholds, update intervals, and data paths
"""

# LED Configuration (3 addressable ZIPLEDs)
LED_CONFIG = {
    0: {
        "name": "Temperature",
        "metric": "temperature",
        "colors": {
            "green": (0, 255, 0),
            "yellow": (255, 255, 0),
            "red": (255, 0, 0)
        },
        "thresholds": {
            "green_min": 20,
            "green_max": 25,
            "yellow_min": 16,
            "yellow_max": 28
        }
    },
    1: {
        "name": "Humidity",
        "metric": "humidity",
        "colors": {
            "green": (0, 255, 0),
            "yellow": (255, 165, 0),
            "red": (255, 0, 0)
        },
        "thresholds": {
            "temp_min": 10,
            "temp_max": 40,
            "tolerance": 15.0
        }
    },
    2: {
        "name": "eCO2",
        "metric": "eco2",
        "colors": {
            "green": (0, 255, 0),
            "yellow": (255, 255, 0),
            "red": (255, 0, 0)
        },
        "thresholds": {
            "green_max": 800,
            "yellow_max": 1200
        }
    }
}

# Measurement and logging settings
UPDATE_INTERVAL = 60  # in seconds
DATA_DIR = "data"
BRIGHTNESS = 5  # LED brightness (0-100)

# Temperature calibration for sensor offset correction.
# Two points define a linear correction from sensor reading to real temperature.
# Example: if the sensor reads 32°C but the real temperature is 22°C,
# and a later point says 20°C sensor corresponds to 10°C real, then the
# correction is "real = sensor - 10" for now.
TEMPERATURE_CALIBRATION = {
    "sensor_point_1": 32.0,
    "actual_point_1": 22.0,
    "sensor_point_2": 20.0,
    "actual_point_2": 10.0,
}

# OLED Display settings
OLED_ENABLED = True
SHOW_METRICS = [
    "temperature",
    "humidity",
    "eco2",
    "pressure",
    "air_quality_percent",
    "air_quality_score"
]
