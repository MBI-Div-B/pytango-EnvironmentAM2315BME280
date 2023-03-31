#!/usr/bin/python3 -u
# coding: utf8


# Copyright (C) 2023  MBI-Division-B
# MIT License, refer to LICENSE file
# Author: Leon Werner / Email: leon.werner@mbi-berlin.de


from tango import DevState
from tango.server import Device, command, device_property
import AM2315
import board
from adafruit_bme280 import basic as adafruit_bme280
from time import sleep


class EnvironmentAM2315BME280Ctrl(Device):
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
        self.sensor_types = {0: 'am2315',
                             1: 'bme280'}
        self.bme_init = False
        self.set_state(DevState.ON)
        self._current_channel = None

    @command(dtype_in=(int,), dtype_out=str)
    def init_sensor(self, channel_sens):
        error = ''
        sens_type = self.sensor_types[channel_sens[1]]
        if sens_type == 'am2315' or (sens_type == 'bme280' and self.bme_init):
            pass
        elif sens_type == 'bme280' and not self.bme_init:
            try:
                self.mux_select(channel_sens[0])
                self._bme1 = adafruit_bme280.Adafruit_BME280_I2C(self.i2c)
                self.bme_init = True
            except ValueError:
                error = 'BME280 not connected to channel ' + str(channel_sens)
        else:
            error = 'wrong sensor type/name'
        return error

    @command(dtype_in=(int,), dtype_out=(float,))
    def read_data(self, channel_sens):
        sens_type = self.sensor_types[channel_sens[1]]
        data = [-273, -1, -1]
        sleep(0.1)
        if channel_sens[0] != self._current_channel:
            self.mux_select(channel_sens[0])
            self._current_channel = channel_sens[0]
        try:
            if sens_type == 'am2315':
                data = self._am1.read_temperature_humidity()                
            elif sens_type == 'bme280':
                data = (self._bme1.temperature, self._bme1.humidity,
                        self._bme1.pressure)
            else:
               self.error_stream('Could not read device. wrong device')
        except Exception as e:
            self.error_stream('Something went wrong while reading the sensor {:d}'.format(channel_sens[0]))
        return data

    def mux_select(self, channel):
        if channel > 7:
            self.error_stream('Channel number too high')
            return
        self.i2c.writeto(self.MuxAddress, bytearray([1 << channel]))
        sleep(0.1)


if __name__ == '__main__':
    EnvironmentAM2315BME280Ctrl.run_server()
