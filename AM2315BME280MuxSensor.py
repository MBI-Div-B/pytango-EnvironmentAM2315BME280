#!/usr/bin/env python3
# -*- coding: utf-8 -*-


# Copyright (C) 2020  MBI-Division-B
# MIT License, refer to LICENSE file
# Author: Luca Barbera / Email: barbera@mbi-berlin.de


from tango import AttrWriteType, DevState, DebugIt, ErrorIt, InfoIt, DeviceProxy, DevFailed, ConnectionFailed
from tango.server import Device, attribute, command, device_property


class AM2315BME280MuxSensor(Device):
    CtrlDevice = device_property(
        dtype=str,
        default_value="domain/family/memeber",
        )

    SensorType = device_property(
        dtype=str,
        default_value="AM2315",
        )
    Channel = device_property(
        dtype=int,
        default_value=0,
        )
    @DebugIt()
    def init_device(self):
        
        Device.init_device(self)
        self.set_state(DevState.INIT)
        try:
            self.ctrl = DeviceProxy(self.CtrlDevice)
            self.info_stream("Connection established.")
            self.set_state(DevState.ON)
        except AttributeError:
            self.error_stream('Connection could not be established.')
            self.set_state(DevState.OFF)
            
        if self.SensorType.lower() == "am2315":
            self.sens_int = 0
            self._attr_lib = {"temperature": 0.0, "humidity" : 0.0}
            self._address = 0x5c
        elif self.SensorType.lower() == "bme280":
            self.sens_int = 1
            self._attr_lib = {"temperature": 0.0, "humidity" : 0.0, "pressure" : 0.0}
            self._address = 0x77
        else:
            self.error_stream('Worng Address')
            self.set_state(DevState.FAULT)

        try:
            e = ''
            e = self.ctrl.init_sensor((self.Channel,self.sens_int))
        except (AttributeError, DevFailed):
            self.error_stream('Controller not started')
            self.set_state(DevState.OFF)
        if e != '':
            self.error_stream(e)
            self.set_state(DevState.FAULT)
            
        for i in self._attr_lib:
            self.create_attributes(i)
        
    @DebugIt()
    def always_executed_hook(self):
        read_out = []
        try:
            # _read_data measures both humidity and temperature
            read_out = self.ctrl.read_data((self.Channel,self.sens_int))
            self.set_state(DevState.ON)
            
        except (AttributeError, DevFailed, ConnectionFailed):
            self.error_stream('Controller not started')
            self.set_state(DevState.OFF)
            return
        if len(read_out) < 2:
            self.error_stream('Data could not be read')
            self.set_state(DevState.FAULT)
            for i,a in enumerate(self._attr_lib):
                self._attr_lib[a] = float([-1,-1,-1][i])
        else:
            for i,a in enumerate(self._attr_lib):
                    self._attr_lib[a] = float(read_out[i])

    @DebugIt()
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
        attr.set_value(self._attr_lib[attr.get_name()])
        return self._attr_lib[attr.get_name()]
        


if __name__ == "__main__":
    AM2315BME280MuxSensor.run_server()