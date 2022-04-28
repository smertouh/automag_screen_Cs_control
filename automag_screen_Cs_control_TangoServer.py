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


class automag_screen_Cs_control_TangoServer(TangoServerPrototype):
    server_version = '1.0'
    server_name = 'Python Control screen shot, dipole magnets and Cs temperature Tango Server'
    device_list = []

    screenshot_time = attribute(label="screenshot_time", dtype=float,
                            display_level=DispLevel.OPERATOR,
                            access=AttrWriteType.READ_WRITE,
                            unit="s", format="%f",
                            doc="time to grab screen")

    def init_device(self):
        """
        self.power = 0.0
        self.rf_power = 0.0
        self.power_limit_value = 50.0
        self.device_name = ''
        # devices
        self.timer = None
        self.adc = None
        self.dac = None
        # attribute values
        self.ia = None
        self.ea = None
        self.ua = None
        self.ic = None
        self.iscr = None
        self.ug1 = None
        """
        #
        super().init_device()
        """
        self.power_limit_value = self.config.get('power_limit', 50.0)
        self.power_limit.set_write_value(self.power_limit_value)
        self.configure_tango_logging()
        automag_screen_Cs_control_TangoServer.device_list.append(self)
        """

    def read_screenshot_time(self):
        return self.screenshot_time
    def write_screenshot_time(self, value):
        self.screenshot_time = value





def looping():
    global time_lag
    time.sleep(1)
    print(time_lag)

    time.sleep(0.001)
    try:
        time_lag += 1
        if time_lag > 300:
            time_lag = 0
            screenshott(0)
        try:
            auto_starter_on = float(vasya_lastshottime.get_property('auto_starter_on')['auto_starter_on'][0])
            if (auto_starter_on == 1):
                mag_on(1)
        except:
            mag_on_init(1)
    except:
        pass


time_lag=301
if __name__ == "__main__":
    print(1)

    automag_screen_Cs_control_TangoServer.run_server(event_loop=looping)
    #RFPowerTangoServer.run_server()
