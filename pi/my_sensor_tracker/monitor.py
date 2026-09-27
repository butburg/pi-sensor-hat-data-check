#!/usr/bin/env python3
"""
Air Quality Monitor - Continuous monitoring, logging, and LED feedback
Measures every 5 minutes, logs to CSV, updates OLED and LEDs based on thresholds
"""

import os
import csv
import sys
from datetime import datetime
from time import sleep
import traceback

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from KitronikAirQualityControlHAT import *
from config import LED_CONFIG, UPDATE_INTERVAL, DATA_DIR, BRIGHTNESS, TEMPERATURE_CALIBRATION

class AirQualityMonitor:
    def __init__(self):
        """Initialize all HAT components"""
        print("[INIT] Starting Air Quality Monitor initialization...")

        self.is_initialized = False

        try:
            # Initialize components (OLED must come before BME688)
            self.oled = KitronikOLED()
            self.bme688 = KitronikBME688()
            self.bme688.screen = self.oled  # Link OLED to BME688 for internal use
            self.zipLEDs = KitronikZIPLEDs(autoShow=False)
            self.rtc = KitronikRTC()

            # Set LED brightness
            self.zipLEDs.setBrightness(BRIGHTNESS)

            print("[INIT] All components initialized successfully")
            self.is_initialized = True
        except Exception as e:
            print(f"[ERROR] Failed to initialize components: {e}")
            traceback.print_exc()
            self.is_initialized = False
            return

        # Create data directory if needed
        if not os.path.exists(DATA_DIR):
            os.makedirs(DATA_DIR)
            print(f"[INIT] Created data directory: {DATA_DIR}")

        # Always calculate a fresh baseline
        self.calculate_baseline()

    def calculate_baseline(self):
        """Calculate baseline values for BME688"""
        print("[BASELINE] Calculating new baseline...")
        try:
            # Show progress on OLED
            self.oled.clear()
            self.oled.displayText("Calibrating...", 3)
            self.oled.show()

            # Calculate baselines (takes ~300 seconds)
            self.bme688.calcBaselines(self.oled)

            print("[BASELINE] Baseline calibration complete")

        except Exception as e:
            print(f"[ERROR] Baseline calculation failed: {e}")
            traceback.print_exc()

    def correct_temperature(self, sensor_temp):
        """Convert sensor temperature to a corrected real temperature using two calibration points."""
        calibration = TEMPERATURE_CALIBRATION

        sensor_1 = calibration["sensor_point_1"]
        actual_1 = calibration["actual_point_1"]
        sensor_2 = calibration["sensor_point_2"]
        actual_2 = calibration["actual_point_2"]

        if sensor_1 == sensor_2:
            return sensor_temp + (actual_1 - sensor_1)

        slope = (actual_2 - actual_1) / (sensor_2 - sensor_1)
        intercept = actual_1 - (slope * sensor_1)

        return (slope * sensor_temp) + intercept

    def get_color_for_metric(self, led_index, temp, humidity, pressure, eco2, air_quality_percent, air_quality_score):
        """Determine LED color based on the three requested metrics."""
        config = LED_CONFIG[led_index]
        metric_name = config["name"]

        try:
            if metric_name == "Temperature":
                if config["thresholds"]["green_min"] <= temp <= config["thresholds"]["green_max"]:
                    return config["colors"]["green"]
                elif config["thresholds"]["yellow_min"] <= temp <= config["thresholds"]["yellow_max"]:
                    return config["colors"]["yellow"]
                else:
                    return config["colors"]["red"]

            elif metric_name == "Humidity":
                config_thresh = config["thresholds"]
                tolerance = config_thresh["tolerance"]
                temp_min = config_thresh["temp_min"]
                temp_max = config_thresh["temp_max"]

                temp_for_comfort = max(temp_min, min(temp_max, temp))
                ideal_rh = 35 + (0.5 * temp_for_comfort)
                min_rh = max(20, ideal_rh - tolerance)
                max_rh = min(90, ideal_rh + tolerance)

                if min_rh <= humidity <= max_rh:
                    return config["colors"]["green"]
                elif abs(humidity - ideal_rh) <= tolerance + 5:
                    return config["colors"]["yellow"]
                else:
                    return config["colors"]["red"]

            elif metric_name == "eCO2":
                if eco2 <= config["thresholds"]["green_max"]:
                    return config["colors"]["green"]
                elif eco2 <= config["thresholds"]["yellow_max"]:
                    return config["colors"]["yellow"]
                else:
                    return config["colors"]["red"]
        except Exception as e:
            print(f"[ERROR] Error calculating color for LED {led_index}: {e}")
            return (255, 0, 0)

    @staticmethod
    def _format_display_value(value):
        formatted = f"{value:.1f}".rstrip("0").rstrip(".")
        return "0" if formatted == "-0" else formatted

    def update_display(self, temp, humidity, pressure, eco2, air_quality_percent, air_quality_score):
        """Update OLED display with current readings"""
        try:
            self.oled.clear()
            self.oled.displayText(f"Temp:{self._format_display_value(temp)}", 1)
            self.oled.displayText(f"Hum:{self._format_display_value(humidity)}", 2)
            self.oled.displayText(f"eCO2:{self._format_display_value(eco2)}", 3)
            self.oled.displayText(f"Press:{self._format_display_value(pressure)}", 4)
            self.oled.displayText(f"AQ %:{self._format_display_value(air_quality_percent)}", 5)
            self.oled.displayText(f"AQ Score:{self._format_display_value(air_quality_score)}", 6)
            self.oled.show()
        except Exception as e:
            print(f"[ERROR] Failed to update OLED: {e}")

    def update_leds(self, temp, humidity, pressure, eco2, air_quality_percent, air_quality_score):
        """Update LED colors based on the three requested metrics."""
        try:
            for led_index in range(3):
                color = self.get_color_for_metric(
                    led_index, temp, humidity, pressure, eco2, air_quality_percent, air_quality_score
                )
                self.zipLEDs.setPixel(led_index, color)
            self.zipLEDs.show()
        except Exception as e:
            print(f"[ERROR] Failed to update LEDs: {e}")

    def log_data(self, temp, humidity, pressure, eco2, air_quality_percent, air_quality_score, gas_resistance):
        """Log measurement to daily CSV file"""
        try:
            timestamp = datetime.now()
            filename = os.path.join(DATA_DIR, timestamp.strftime("%Y-%m-%d.csv"))

            # Check if file exists to determine if we need headers
            file_exists = os.path.isfile(filename)

            with open(filename, 'a', newline='') as csvfile:
                writer = csv.writer(csvfile)

                # Write header if new file
                if not file_exists:
                    writer.writerow([
                        "timestamp",
                        "temperature",
                        "humidity",
                        "pressure",
                        "eco2",
                        "air_quality_percent",
                        "air_quality_score",
                        "gas_resistance"
                    ])

                # Write data
                writer.writerow([
                    timestamp.strftime("%Y-%m-%d %H:%M:%S"),
   		    f"{temp:.2f}",
   		    f"{humidity:.2f}",
   		    f"{pressure:.2f}",
   		    f"{eco2:.2f}",
 		    f"{air_quality_percent:.2f}",
		    f"{air_quality_score:.2f}",
		    f"{gas_resistance:.0f}"
                ])

            print(f"[LOG] Data logged to {filename}")
        except Exception as e:
            print(f"[ERROR] Failed to log data: {e}")

    def measure_and_update(self):
        """Take a measurement and update all outputs"""
        try:
            # Measure
            self.bme688.measureData()

            # Read values
            sensor_temp = self.bme688.readTemperature()
            temp = self.correct_temperature(sensor_temp)
            humidity = self.bme688.readHumidity()
            pressure = self.bme688.readPressure()
            eco2 = self.bme688.readeCO2()
            air_quality_percent = self.bme688.getAirQualityPercent()
            air_quality_score = self.bme688.getAirQualityScore()
            gas_resistance = self.bme688.readGasRes()

            # Log timestamp
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            print(f"\n[{timestamp}] Measurement taken")
            print(f"  Sensor Temp: {sensor_temp}°C, Corrected Temp: {temp}°C")
            print(f"  Humidity: {humidity}%, Pressure: {pressure}Pa")
            print(f"  eCO2: {eco2}ppm, Air Quality: {air_quality_percent}%, Gas: {gas_resistance}Ohm")

            # Update outputs
            self.update_display(temp, humidity, pressure, eco2, air_quality_percent, air_quality_score)
            self.update_leds(temp, humidity, pressure, eco2, air_quality_percent, air_quality_score)
            self.log_data(temp, humidity, pressure, eco2, air_quality_percent, air_quality_score, gas_resistance)

        except Exception as e:
            print(f"[ERROR] Measurement failed: {e}")
            traceback.print_exc()

    def run(self):
        """Main monitoring loop"""
        if not self.is_initialized:
            print("[ERROR] Monitor failed to initialize, exiting")
            return

        print(f"\n[START] Air Quality Monitor running")
        print(f"[START] Measurement interval: {UPDATE_INTERVAL} seconds ({UPDATE_INTERVAL/60:.1f} minutes)")
        print(f"[START] Data stored in: {DATA_DIR}/")

        try:
            while True:
                self.measure_and_update()
                print(f"[SLEEP] Waiting {UPDATE_INTERVAL} seconds until next measurement...")
                sleep(UPDATE_INTERVAL)
        except KeyboardInterrupt:
            print("\n[EXIT] Monitor stopped by user")
        except Exception as e:
            print(f"[ERROR] Unexpected error in main loop: {e}")
            traceback.print_exc()

if __name__ == "__main__":
    monitor = AirQualityMonitor()
    monitor.run()
