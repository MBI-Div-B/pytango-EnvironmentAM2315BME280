from .EnvironmentAM2315BME280Ctrl import EnvironmentAM2315BME280Ctrl
from .EnvironmentAM2315BME280Sensor import EnvironmentAM2315BME280Sensor


def main():
    import sys
    import tango.server

    args = ["EnvironmentAM2315BME280"] + sys.argv[1:]
    tango.server.run(
        (EnvironmentAM2315BME280Ctrl, EnvironmentAM2315BME280Sensor), args=args
    )
