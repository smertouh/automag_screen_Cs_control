import sys
import time
import tango
import numpy
import PyTango
from tango import DeviceProxy, EventType
from tango.constants import ALL_EVENTS
import datetime
import scrreen
import os



try:
    adc_device = tango.DeviceProxy("binp/nbi/adc0")
    ap = tango.AttributeProxy("et7000_server/test/pet7_7026/ai00")
    vasya_lastshottime = tango.AttributeProxy("test/nbi/vasya/lastshottime")

    mag1_start = tango.AttributeProxy("binp/nbi/magnet1/output_state")
    mag2_start = tango.AttributeProxy("binp/nbi/magnet2/output_state")
    qmag1_start = tango.AttributeProxy("binp/nbi/magnet3/output_state")
    qmag2_start = tango.AttributeProxy("binp/nbi/magnet4/output_state")
except:
    print("устройства выключены")



def T_control(c):
    text = c.attr_value.value#pow(10,(1.667*c.attr_value.value-11.46))*1000
    global ap
    global ap1
    global flag

    if (flag==0):
        Tmax=float(ap.get_property('Tmax')['Tmax'][0])
        if (text>Tmax):
            ap1.write(1)
            flag=1
        else:
            flag=0
    else:
        Tmin=float(ap.get_property('Tmin')['Tmin'][0])
        if (text<Tmin):
            ap1.write(0)
            flag=0
        else:
            flag=1
    return 1
def write_mag_on(c):
    global mag1_start
    global mag2_start
    global qmag1_start
    global qmag2_start
    global vasya_lastshottime
    try:
        mag1_start.write(c)
    except:
        mag_on_init(1)
    try:
        mag2_start.write(c)
    except:
        mag_on_init(1)
    try:
        qmag1_start.write(c)
    except:
        mag_on_init(1)
    try:
        qmag2_start.write(c)
    except:
        mag_on_init(1)
    cc = {'Mag_status': c}
    vasya_lastshottime.put_property(cc)

def mag_on(c):
    global adc_device
    global vasya_lastshottime
    elapsed = adc_device.Elapsed
    try:
        Tstart=float(vasya_lastshottime.get_property('Tstart')['Tstart'][0])
        Tstop=float(vasya_lastshottime.get_property('Tstop')['Tstop'][0])
        Mag_status = float(vasya_lastshottime.get_property('Mag_status')['Mag_status'][0])
        Screen_shot= float(vasya_lastshottime.get_property('Screen_shot')['Screen_shot'][0])
        Screen_shot_stat= float(vasya_lastshottime.get_property('Screen_shot_stat')['Screen_shot_stat'][0])
    except:
        mag_on_init(1)

    if(elapsed>Tstart):
        if(elapsed<Tstop):
            if(Mag_status==0):
                try:
                    write_mag_on(1)
                except:
                    print("магниты не включились")
            if(elapsed>Screen_shot):
                try:
                    if(Screen_shot_stat==0):
                        screenshott(1)
                        cc = {'Screen_shot_stat': 1}
                        vasya_lastshottime.put_property(cc)
                except:
                    print("screenshot failed")
    if (elapsed > Tstop):
        if (Screen_shot_stat == 1):
            cc = {'Screen_shot_stat': 0}
            vasya_lastshottime.put_property(cc)
        if (Mag_status == 1):
            try:
                write_mag_on(0)
            except:
                print("не удалось выключить магниты")

    return 1

def mag_on_init(c):
    global vasya_lastshottime
    try:
        float(vasya_lastshottime.get_property('auto_starter_on')['auto_starter_on'][0])
        float(vasya_lastshottime.get_property('Tstart')['Tstart'][0])
        float(vasya_lastshottime.get_property('Tstop')['Tstop'][0])
        float(vasya_lastshottime.get_property('Mag_status')['Mag_status'][0])
        float(vasya_lastshottime.get_property('Screen_shot')['Screen_shot'][0])
        float(vasya_lastshottime.get_property('Screen_shot_stat')['Screen_shot_stat'][0])
    except:
        c = {'Tstart': 1, 'Tstop': 10, 'Mag_status':0,'Screen_shot':5,'Screen_shot_stat':0,'auto_starter_on':0}
        try:
            vasya_lastshottime.put_property(c)
        except:
            print("вася выключен")

def T_control_init(c):
    global ap
    global flag
    try:
        ap = tango.AttributeProxy("et7000_server/test/pet2_7015/ai00")
        float(ap.get_property('Tmax')['Tmax'][0])
        float(ap.get_property('Tmin')['Tmin'][0])
    except:
        ap = tango.AttributeProxy("et7000_server/test/pet2_7015/ai00")
        c = {'Tmax': 500, 'Tmin': 50}
        ap.put_property(c)

    try:
        ap = tango.AttributeProxy("et7000_server/test/pet2_7015/ai00")
        ap1 = tango.AttributeProxy("binp/nbi/adam5/do00")
        flag = ap1.read().value
        tango_pet2 = tango.DeviceProxy("et7000_server/test/pet2_7015")

        tango_pet2.poll_attribute("ai00", 1000)
        tango_pet2.subscribe_event("ai00", EventType.CHANGE_EVENT, T_control)
    except tango.DevFailed:
        print("pet02 offline")
    return 1


def screenshott(c):

    now = datetime.datetime.now()

    ss = now.strftime("%Y")

    s0 = "d:\\data\\screenshot\\" + ss
    if os.path.exists(s0):
        pass
    else:
        os.mkdir(s0)

    ss = now.strftime("%Y-%m")
    s0 = s0+"\\" + ss
    if os.path.exists(s0):
        pass
    else:
        os.mkdir(s0)


    ss = now.strftime("%Y-%m-%d")

    s0 = s0 + "\\" + ss
    if os.path.exists(s0):
        pass
    else:
        os.mkdir(s0)
    ss = now.strftime("%Y-%m-%d_%H_%M_%S")
    s=s0+"\\screen_"+ss+".png"
    scrreen.grab_screen(s)
    #time.sleep(5)
    return 1

def init_screenshott(c):


    try:
        tango_pet12 = tango.DeviceProxy("et7000_server/test/pet12_7018")

        tango_pet12.poll_attribute("ai03", 1000)
        tango_pet12.subscribe_event("ai03", EventType.CHANGE_EVENT, screenshott)
    except tango.DevFailed:
        print("pet12 offline")

if __name__ == "__main__":
    #T_control_init(1)
    mag_on_init(1)
    screenshott(0)

    time_lag=0
    while True:
        time_lag += 1
        if time_lag>300:
            time_lag=0
            screenshott(0)
        time.sleep(1)
        try:
            auto_starter_on = float(vasya_lastshottime.get_property('auto_starter_on')['auto_starter_on'][0])
            if (auto_starter_on==1):
                mag_on(1)
        except:
            mag_on_init(1)




