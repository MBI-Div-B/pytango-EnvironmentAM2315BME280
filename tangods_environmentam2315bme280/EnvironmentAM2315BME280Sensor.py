#!/usr/bin/env python3
# -*- coding: utf-8 -*-


# Copyright (C) 2023  MBI-Division-B
# MIT License, refer to LICENSE file
# Author: Leon Werner / Email: leon.werner@mbi-berlin.de


from tango import AttrWriteType, DevState, DeviceProxy, DevFailed
from tango import ConnectionFailed, AttrQuality
from tango.server import Device, attribute, device_property


class EnvironmentAM2315BME280Sensor(Device):
    CtrlDevice = device_property(
        dtype=str,
        default_value="domain/family/member",
    )

    SensorType = device_property(
        dtype=str, default_value="AM2315", doc="AM2315 or BME280"
    )

    Channel = device_property(
        dtype=int,
        default_value=0,
    )

    def init_device(self):
        Device.init_device(self)
        self.set_state(DevState.INIT)

        # connect to controller
        try:
            self.ctrl = DeviceProxy(self.CtrlDevice)
            self.info_stream(
                "Connection established to controller {:s}".format(self.CtrlDevice)
            )
            self.set_state(DevState.ON)
        except AttributeError:
            self.error_stream(
                "Connection could not be established to controller {:s}".format(
                    self.CtrlDevice
                )
            )
            self.set_state(DevState.OFF)

        if self.SensorType.lower() == "am2315":
            self.sens_id = 0
            self._attr_values = {"temperature": 0.0, "humidity": 0.0}
            self._address = 0x5C
        elif self.SensorType.lower() == "bme280":
            self.sens_id = 1
            self._attr_values = {"temperature": 0.0, "humidity": 0.0, "pressure": 0.0}
            self._address = 0x77
        else:
            self.error_stream("Sensor type {:s} not defined".format(self.SensorType))
            self.set_state(DevState.FAULT)

        # initialize sensor
        try:
            e = ""
            e = self.ctrl.init_sensor((self.Channel, self.sens_id))
            self.debug_stream(e)
        except (AttributeError, DevFailed):
            self.error_stream("Could not initialize sensor on controller")
            self.set_state(DevState.OFF)
        if e != "":
            self.error_stream(e)
            self.set_state(DevState.FAULT)

    def initialize_dynamic_attributes(self):
        for k in self._attr_values:
            self.create_attributes(k)

    def create_attributes(self, name):
        """
        Command creates a new Attribute
        """
        if name == "humidity":
            min_value = 0
            max_value = 100
            unit = "%"
        elif name == "pressure":
            min_value = 300
            max_value = 1100
            unit = "hPa"
        else:
            min_value = -40
            max_value = 125
            unit = "C"

        attr = attribute(
            name=name,
            dtype=float,
            access=AttrWriteType.READ,
            label=name,
            unit=unit,
            min_value=min_value,
            max_value=max_value,
            format="%4.1f",
        ).to_attr()
        self.add_attribute(attr, r_meth=self.read_value)

    # @DebugIt()
    def read_value(self, attr):
        # avoid multiple communication with sensor hardware since every read
        # command returns always all attribute values
        # communication is only initiated for temperature
        if attr.get_name() == "temperature":
            try:
                # read_data returns measures both humidity and temperature
                for k, v in zip(
                    self._attr_values, self.ctrl.read_data((self.Channel, self.sens_id))
                ):
                    self._attr_values[k] = float(v)
                self.set_state(DevState.ON)
            except (AttributeError, DevFailed, ConnectionFailed) as e:
                self.error_stream(e)
                self.error_stream("Communication with controller broken")
                self.set_state(DevState.OFF)
            except ValueError:
                self.error_stream("Returned data seems to be corrupt")
                self.set_state(DevState.FAULT)

        # check if attribute values is within its limits
        attr_config = attr.get_properties()
        min_value = float(attr_config.min_value)
        max_value = float(attr_config.max_value)
        value = self._attr_values[attr.get_name()]
        if (value >= min_value) & (value <= max_value):
            attr.set_value(value)
        else:
            attr.set_qualtity(AttrQuality.ATTR_INVALID)
            self.error_stream("attribute value is invalid")


if __name__ == "__main__":
    EnvironmentAM2315BME280Sensor.run_server()
