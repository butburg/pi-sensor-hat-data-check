## Pi HAT Sensor Data Collection & Visualization

This project collects sensor data from a Raspberry Pi HAT, sends it via a Python server over the local network, and visualizes the collected data in a chart.

### Features
- Collects sensor data from Pi HAT
- Python server sends data to LAN
- Data is visualized in charts (see sensor_chart.html)

### Setup
1. Clone this repository:
	```bash
	git clone <repo-url>
	cd pi-sensor-hat-data-check
	```
2. Install dependencies:
	```bash
	uv pip install -r requirements.txt
	```
	(or use your preferred Python environment manager)

### Usage
- Run the data collection and visualization:
  ```bash
  uv run python3 main.py
  uv run python3 visualize_sensors.py
  ```
- Open `sensor_chart.html` in your browser to view the chart.

### Files
- `main.py`: Collects and sends sensor data
- `visualize_sensors.py`: Processes and visualizes data
- `sensor_chart.html`: Chart visualization
- `pyproject.toml`: Project configuration
- `.gitignore`, `.python-version`, `uv.lock`: Environment and dependency files

