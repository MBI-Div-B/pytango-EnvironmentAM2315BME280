#!/usr/bin/python3 -u
# coding: utf8
# PhytronMCC2Ctrl
from tango import DevState, AttrWriteType, DispLevel
from tango.server import Device, attribute, command, device_property
import AM2315
import board
from adafruit_bme280 import basic as adafruit_bme280
from Adafruit_GPIO import I2C


class AM2315BME280MuxCtrl(Device):
    # device properties
    Address = device_property(
        dtype="str",
        default_value="0x70",
    )

    def init_device(self):
        Device.init_device(self)
        self.set_state(DevState.INIT)
        try:
            self.i2c = board.I2C()
            #self.mux = I2C.get_i2c_device(address=int(self.Address, 16))
            self.sensor_types = {"AM2315" : (AM2315.AM2315(1),(read_temperature,read_humidity)), 
                            "BME280" : (adafruit_bme280.Adafruit_BME280_I2C(self.i2c),(temperature,humidity,pressure))}
            self.sensors = {}
            for i in self.sensors_types:
                self.sensors[i] = self.sensors_types[i]
            self.set_state(DevState.ON)
        except:
            self.set_state(DevState.OFF)
            self.error_stream('Cannot connect!')

    @command(dtype_in=int, dtype_out=(float,))
    def read_data(self, channel, sens_type= "AM2315"):
        try:
            self.mux_select(channel)
            data = [self.sensors[sens_type].x() for x in self.sensor_types[sens_type][1]]
            return data
        except:
            return -1, -1

    def mux_select(self, channel):
        if channel > 7:
            return
        self.i2c.writeto(self.Address,bytearray([1 << channel]))

if __name__ == "__main__":
    AM2315BME280MuxCtrl.run_server()