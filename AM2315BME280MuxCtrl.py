#!/usr/bin/python3 -u
# coding: utf8
# PhytronMCC2Ctrl
from tango import DevState, AttrWriteType, DispLevel, DebugIt
from tango.server import Device, attribute, command, device_property
import AM2315
import board
from adafruit_bme280 import basic as adafruit_bme280


class AM2315BME280MuxCtrl(Device):
    # device properties
    MuxAddress = device_property(
        dtype=int,
        default_value=int(0x70),
    )

    def init_device(self):
        Device.init_device(self)
        self.set_state(DevState.INIT)
        self._am1 = AM2315.AM2315(1)
        self.i2c = board.I2C()
        self.sensor_types = {0: "AM2315" ,
                             1: "BME280" }
        self.bme_init = False
        self.set_state(DevState.ON)
        
    @DebugIt()
    @command(dtype_in=(int,), dtype_out=str)
    def init_sensor(self,channel_sens):
        error = ""
        sens_type = self.sensor_types[channel_sens[1]]
        if sens_type == "AM2315":
            pass
        elif sens_type == "BME280" and not self.bme_init:
            try:
                self.mux_select(channel_sens[0])
                self._bme1 = adafruit_bme280.Adafruit_BME280_I2C(self.i2c)
                self.bme_init = True
            except ValueError:
                error = "BME280 not connected to Channel " + str(channel)
        else:
            error = "wrong Sensor type/name"
        return error
    
    @DebugIt()
    @command(dtype_in=(int,) , dtype_out=(float,))
    def read_data(self, channel_sens):
        sens_type = self.sensor_types[channel_sens[1]]
        self.info_stream(str(sens_type))
        self.mux_select(channel_sens[0])
        try:
            if sens_type == "AM2315": #AM2315
                self.info_stream("inam")
                data = (self._am1.read_temperature(), self._am1.read_humidity())
                self.info_stream("out am")
            elif sens_type == "BME280":#BME280
                data = (self._bme1.temperature,self._bme1.humidity,self._bme1.pressure)
            else:
                self.error_stream('could not read Device. wrong device')
        except Exception:
            self.error_stream('something went wrong while reading the Sensor')
            data = (-1.)
        return data

        
    @DebugIt()
    def mux_select(self, channel):
        if channel > 7:
            self.error_stream('channel number too high')
            return
        self.i2c.writeto(self.MuxAddress, bytearray([1 << channel]))

if __name__ == "__main__":
    AM2315BME280MuxCtrl.run_server()