import importlib.util
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

spec = importlib.util.spec_from_file_location("monitor", ROOT / "monitor.py")
monitor = importlib.util.module_from_spec(spec)
spec.loader.exec_module(monitor)


def test_led_mapping_uses_three_metrics():
    m = monitor.AirQualityMonitor.__new__(monitor.AirQualityMonitor)

    temp = 22
    humidity = 50
    eco2 = 600

    # LED 0 -> temperature comfort
    assert m.get_color_for_metric(0, temp, humidity, None, eco2, None, None) == (0, 255, 0)

    # LED 1 -> humidity related to temperature comfort
    assert m.get_color_for_metric(1, temp, humidity, None, eco2, None, None) == (0, 255, 0)

    # LED 2 -> eCO2 traffic light
    assert m.get_color_for_metric(2, temp, humidity, None, eco2, None, None) == (0, 255, 0)


def test_led_mapping_marks_bad_co2_red():
    m = monitor.AirQualityMonitor.__new__(monitor.AirQualityMonitor)

    assert m.get_color_for_metric(2, 22, 50, None, 1400, None, None) == (255, 0, 0)


def test_humidity_comfort_uses_wider_temperature_range():
    m = monitor.AirQualityMonitor.__new__(monitor.AirQualityMonitor)

    assert m.get_color_for_metric(1, 40, 70, None, 600, None, None) == (0, 255, 0)


def test_temperature_calibration_uses_two_points():
    m = monitor.AirQualityMonitor.__new__(monitor.AirQualityMonitor)

    assert abs(m.correct_temperature(32.0) - 22.0) < 0.001
    assert abs(m.correct_temperature(20.0) - 10.0) < 0.001
    assert abs(m.correct_temperature(22.0) - 12.0) < 0.001
