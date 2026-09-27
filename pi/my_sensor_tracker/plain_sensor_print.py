#!/usr/bin/env python3

import os
import sys
from time import sleep

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from KitronikAirQualityControlHAT import *

oled = KitronikOLED()
bme688 = KitronikBME688()
bme688.screen = oled
bme688.calcBaselines(oled)

while True:
	bme688.measureData()
	temp = bme688.readTemperature()
	humidity = bme688.readHumidity()
	pressure = bme688.readPressure()
	eco2 = bme688.readeCO2()
	air_quality_percent = bme688.getAirQualityPercent()
	air_quality_score = bme688.getAirQualityScore()

	print(
		"temp=", temp,
		"humidity=", humidity,
		"pressure=", pressure,
		"eco2=", eco2,
		"aq%=", air_quality_percent,
		"aq_score=", air_quality_score,
	)

	sleep(1)
