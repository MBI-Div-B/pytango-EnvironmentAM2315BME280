#!/usr/bin/env python3
# -*- coding: utf-8 -*-


# Copyright (C) 2020  MBI-Division-B
# MIT License, refer to LICENSE file
# Author: Luca Barbera / Email: barbera@mbi-berlin.de


from tango import AttrWriteType, DevState, DebugIt, ErrorIt, InfoIt, DeviceProxy
from tango.server import Device, attribute, command, device_property


class AM2315BME280MuxSensor(Device):
    CtrlDevice = device_property(
        dtype="str",
        default_value="domain/family/memeber",
        )

    SensorType = device_property(
        dtype="str",
        default_value="AM2315",
        )
    
    def init_device(self):
        
        Device.init_device(self)
        self.set_state(DevState.INIT)
        try:
            self.ctrl = DeviceProxy(self.CtrlDevice)
            self.info_stream("Connection established.")
            self.set_state(DevState.ON)
        except Exception:
            self.error_stream('Connection could not be established.')
            self.set_state(DevState.OFF)

        if self.SensorType.lower() == "am2315":
            self._attr_lib = {"temperature": 0.0, "humidity" : 0.0}
            self._address = 0x5c
        elif self.SensorType.lower() == "bme280":
            self._attr_lib = {"temperature": 0.0, "humidity" : 0.0, "pressure" : 0.0}
            self._address = 0x77
        else:
            self.error_stream('Worng Address')
            self.set_state(DevState.FAULT)

        for i in self._attr_lib:
            self.create_attributes(i)
        

    def always_executed_hook(self):
        try:
            # _read_data measures both humidity and temperature
            read_out = self.ctrl.read_data(self._channel,sens_type = self.SensorType)
            for i,a in enumerate(self._attr_lib):
                self._attr_lib[a] = read_out[i]
        except Exception:
            self.error_stream('Data could not be read')


    def create_attributes(self, argin):
        
        """
        Command creates a new Attribute
        :param argin: 'DevFloat'
        dev_name
        :return:None
        """
        attr = attribute(
            name=argin,
            dtype=float,
            access=AttrWriteType.READ,
            label=argin,
        ).to_attr()
        self.add_attribute(attr,r_meth=self.read_value)

    def read_value(self,attr):
        return self._attr_lib[attr.get_name()]
        


if __name__ == "__main__":
    AM2315BME280MuxSensor.run_server()