import logging
import sys
import time
import os.path
import numpy
import tango
from tango import DispLevel, AttrWriteType, DevState
from tango.server import attribute, command
from automag import screenshott
import datetime


sys.path.append('../TangoUtils')
from TangoServerPrototype import TangoServerPrototype
from TangoUtils import Configuration
from config_logger import config_logger
from log_exception import log_exception
dt=1
t0 = time.time()
OFF_PASSWORD = 'topsecret'
def write_mag_on(c):
    global mag1_start
    global mag2_start
    global qmag1_start
    global qmag2_start
    try:
        mag1_start.write(c)
    except:
        pass
    try:
        mag2_start.write(c)
    except:
        pass
    try:
        qmag1_start.write(c)
    except:
        pass
    try:
        qmag2_start.write(c)
    except:
        pass

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
        global dt
        adc_device=self.adc_device
        #vasya_lastshottime=self.vasya_lastshottime
        if self.w8==0:
            elapsed = adc_device.Elapsed
            if elapsed < self.T_stop:
                self.w8 = 1
                self.last_shot_time = time.time() - elapsed
                dt=0.01
                print("new_shot")
        else:

            elapsed = time.time()-self.last_shot_time
            #print(elapsed)

            #print(self.last_shot_time)
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
                        self.Mag_status=1
                        print("magnets on")
                    except:
                        print("магниты не включились")
                if (elapsed > Screen_shot):
                    try:
                        if (Screen_shot_stat == True):
                            screenshott(1)
                            print("screenshot")
                            self.new_shot_screen=False
                    except:
                        print("screenshot failed")
        if (elapsed > Tstop):
            if (Screen_shot_stat == False):
                self.new_shot_screen=True
            if (Mag_status == 1):
                try:
                    write_mag_on(0)
                    self.w8=0
                    self.Mag_status = 0
                    print("magnets off")
                except:
                    print("не удалось выключить магниты")
                    self.w8=0
                    self.Mag_status = 0
                dt=1

        return 1


    def init_device(self):
        self.screenshot_time=6.0
        self.T_stop=10
        self.T_start=1
        self.auto_starter_on=1
        self.Mag_status=0
        self.new_shot_mag=True
        self.new_shot_screen = True
        self.w8=0
        self.adc_device = tango.DeviceProxy("binp/nbi/adc0")
        #self.vasya_lastshottime = tango.AttributeProxy("test/nbi/vasya/lastshottime")
        super().init_device()
        automag_screen_Cs_control_TangoServer.device_list.append(self) #global dev=self

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
        #self.Mag_status=self.auto_starter_on
        return self.Mag_status==1
    def read_autostarteron(self):
        return self.auto_starter_on==1
    def write_autostarteron(self, value):
        self.auto_starter_on = value




sizeS=0

def looping():
    global time_lag,dt,sizeS
    time.sleep(dt)
    #print(time_lag)

    time.sleep(0.001)
    for dev in automag_screen_Cs_control_TangoServer.device_list:
        try:
            time_lag += dt
            if time_lag > 3:
                time_lag = 0
                fpath=screenshott(0)
                if abs(sizeS-(os.path.getsize(fpath)))<5000:
                    os.remove(fpath)
                    print("повтор!")
                else:
                    sizeS = (os.path.getsize(fpath))
                    print("5мин "+str(sizeS))
            try:
                auto_starter_on = dev.auto_starter_on#float(vasya_lastshottime.get_property('auto_starter_on')['auto_starter_on'][0])
                if (auto_starter_on == 1):
                    dev.mag_on(1)
            except:
                dev.mag_on_init(1)
        except:
            pass


time_lag=301
if __name__ == "__main__":
    print(1)
    try:
        mag1_start = tango.AttributeProxy("binp/nbi/magnet1/output_state")
        mag2_start = tango.AttributeProxy("binp/nbi/magnet2/output_state")
        qmag1_start = tango.AttributeProxy("binp/nbi/magnet3/output_state")
        qmag2_start = tango.AttributeProxy("binp/nbi/magnet4/output_state")
    except:
        pass
    automag_screen_Cs_control_TangoServer.run_server(event_loop=looping)

    #RFPowerTangoServer.run_server()
