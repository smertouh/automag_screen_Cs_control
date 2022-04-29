import logging
import sys
import time

import numpy
import tango
from tango import DispLevel, AttrWriteType, DevState
from tango.server import attribute, command
from automag import screenshott



sys.path.append('../TangoUtils')
from TangoServerPrototype import TangoServerPrototype
from TangoUtils import Configuration
from config_logger import config_logger
from log_exception import log_exception

t0 = time.time()
OFF_PASSWORD = 'topsecret'


class elapsed_TangoServer(TangoServerPrototype):
    server_version = '1.0'
    server_name = 'elapsed emulator'
    device_list = []

    elapsed = attribute(label="elapsed", dtype=float,
                            display_level=DispLevel.OPERATOR,
                            access=AttrWriteType.READ_WRITE,
                            unit="s", format="%f",
                            doc="t")
    output_state = attribute(label="output_state", dtype=bool,
                               display_level=DispLevel.OPERATOR,
                               access=AttrWriteType.READ_WRITE,
                               unit="", format="%s",
                               doc="1/0")


    def init_device(self):
        self.elapsed_v=0
        self.auto_output_state_v=0
        super().init_device()


    def read_elapsed(self):
        return self.elapsed_v
    def write_elapsed(self, value):
        self.elapsed_v = value
    def read_output_state(self):
        return self.auto_output_state_v == 1
    def write_output_state(self,value):
        self.auto_output_state_v = value



try:
    adc_device = tango.DeviceProxy("binp/nbi/adc0")
except:
    pass
def looping():

    global time_lag,adc_device
    time.sleep(0.1)
    print(time_lag)
    if time_lag>120:
        time_lag=0
    else:
        time_lag+=0.1
    adc_device.write_attribute("elapsed",time_lag)



time_lag=301
if __name__ == "__main__":
    print(1)

    elapsed_TangoServer.run_server(event_loop=looping)
    #RFPowerTangoServer.run_server()
