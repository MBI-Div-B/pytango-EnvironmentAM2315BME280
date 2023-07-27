from setuptools import setup, find_packages

setup(
    name="tangods_environmentam2315bme280",
    version="0.0.1",
    description="Tango Device Server for AM2315 and BME280 Temperature, Humidity, and Pressure Sensors",
    author="Leon Werner",
    author_email="",
    python_requires=">=3.6",
    entry_points={
        "console_scripts": [
            "EnvironmentAM2315BME280 = tangods_environmentam2315bme280:main"
        ]
    },
    license="MIT",
    packages=[
        "tangods_environmentam2315bme280",
        "tangods_environmentam2315bme280.driver",
    ],
    install_requires=[
        "pytango",
        "adafruit-circuitpython-bme280",
        "Adafruit-GPIO",
        "Adafruit-Blinka",
    ],
    url="https://github.com/MBI-Div-b/pytango-EnvironmentAM2315BME280",
    keywords=[
        "tango device",
        "tango",
        "pytango",
        "AM2315",
        "BME280",
    ],
)
