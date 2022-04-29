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

    screenshottime = attribute(label="screenshot_time", dtype=float,
                            display_level=DispLevel.OPERATOR,
                            access=AttrWriteType.READ_WRITE,
                            unit="s", format="%f",
                            doc="time to grab screen")
    autostarteron = attribute(label="start_magnets", dtype=bool,
                               display_level=DispLevel.OPERATOR,
                               access=AttrWriteType.READ_WRITE,
                               unit="", format="%s",
                               doc="1 - enable magnets control, 0 - disable")
    Tstart = attribute(label="magnets_on_time", dtype=float,
                            display_level=DispLevel.OPERATOR,
                            access=AttrWriteType.READ_WRITE,
                            unit="s", format="%f",
                            doc="time from pulse begin when magnets turn on")
    Tstop = attribute(label="magnets_off_time", dtype=float,
                            display_level=DispLevel.OPERATOR,
                            access=AttrWriteType.READ_WRITE,
                            unit="s", format="%f",
                            doc="time from pulse begin when magnets turn off")
    Magstatus= attribute(label="magnets on or off", dtype=bool,
                               display_level=DispLevel.OPERATOR,
                               access=AttrWriteType.READ,
                               unit="", format="%s",
                               doc="magnets are on")


    def mag_on(self,c):
        #adc_device=self.adc_device
        #vasya_lastshottime=self.vasya_lastshottime
        elapsed = 10#adc_device.Elapsed

        Tstart = float(self.T_start)
        Tstop = float(self.T_stop)
        Mag_status = float(self.Mag_status)
        Screen_shot = float(self.screenshot_time)
        Screen_shot_stat = self.new_shot_screen


        if (elapsed > Tstart):
            if (elapsed < Tstop):
                if (Mag_status == 0):
                    try:
                        write_mag_on(1)
                    except:
                        print("магниты не включились")
                if (elapsed > Screen_shot):
                    try:
                        if (Screen_shot_stat == True):
                            screenshott(1)
                            self.new_shot=False
                    except:
                        print("screenshot failed")
        if (elapsed > Tstop):
            if (Screen_shot_stat == False):
                self.new_shot_screen=True
            if (Mag_status == 1):
                try:
                    write_mag_on(0)
                except:
                    print("не удалось выключить магниты")

        return 1


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
        self.screenshot_time=6.0
        self.T_stop=10
        self.T_start=1
        self.auto_starter_on=0
        self.Mag_status=0
        self.new_shot_mag=True
        self.new_shot_screen = True
        #self.adc_device = tango.DeviceProxy("binp/nbi/adc0")
        #self.vasya_lastshottime = tango.AttributeProxy("test/nbi/vasya/lastshottime")
        super().init_device()
        """
        self.power_limit_value = self.config.get('power_limit', 50.0)
        self.power_limit.set_write_value(self.power_limit_value)
        self.configure_tango_logging()
        automag_screen_Cs_control_TangoServer.device_list.append(self)
        """

    def read_screenshottime(self):
        return self.screenshot_time
    def write_screenshottime(self, value):
        self.screenshot_time = value
    def read_Tstart(self):
        return self.T_start
    def write_Tstart(self, value):
        self.T_start = value
    def read_Tstop(self):
        return self.T_stop
    def write_Tstop(self, value):
        self.T_stop = value

    def read_Magstatus(self):
        self.Mag_status=self.auto_starter_on
        return self.Mag_status==1
    def read_autostarteron(self):
        return self.auto_starter_on==1
    def write_autostarteron(self, value):
        self.auto_starter_on = value






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
