#!/usr/bin/python3 -u
from tango.server import run
import os
from EnvironmentAM2315BME280Sensor import EnvironmentAM2315BME280Sensor
from EnvironmentAM2315BME280Ctrl import EnvironmentAM2315BME280Ctrl

# Run EnvironmentAM2315BME280Ctrl and EnvironmentAM2315BME280Sensor
run([EnvironmentAM2315BME280Ctrl, EnvironmentAM2315BME280Sensor])
