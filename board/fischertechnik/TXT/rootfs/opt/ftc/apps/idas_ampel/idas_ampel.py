#! /usr/bin/env python3
# -*- coding: utf-8 -*-
#

import os, sys
import ftrobopy
from TxtStyle import *

# the output ports
PED_GRN=0
PED_RED=1
CAR_RED=2
CAR_YLW=3
CAR_GRN=4

class FtcGuiApplication(TxtApplication):
    def __init__(self, args):
        global txt
        global state
        txt_ip = os.environ.get('TXT_IP')
        if txt_ip == None: txt_ip = "localhost"
        try:
            txt = ftrobopy.ftrobopy(txt_ip, 65000)
        except:
            txt = None

        TxtApplication.__init__(self, args)
        self.w = TxtWindow("Ampel")

        # create a vbox layout for the content area
        vbox = QVBoxLayout()

        but = QCheckBox("blinken")
        but.stateChanged.connect(self.blink_toggle)
        vbox.addWidget(but)

        vbox.addStretch()

        vbox.addWidget(QLabel("Grünphase:"))
        self.dial = QDial()
        self.dial.setNotchesVisible(True)
        self.dial.setRange(2, 60)
        self.green_time_lbl = QLabel()
        self.green_time_lbl.setObjectName("smalllabel")
        self.green_time_lbl.setAlignment(Qt.AlignCenter)   
        self.dial.valueChanged.connect(self.green_time_changed)
        self.dial.setValue(10)

        vbox.addWidget(self.dial)
        vbox.addWidget(self.green_time_lbl)

        self.w.centralWidget.setLayout(vbox)

        # poll button at 10 Hz
        state = "idle"
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.do_ampel)
        self.timer.start(100);

        if txt:
            # all outputs normal mode
            M = [ txt.C_OUTPUT, txt.C_OUTPUT, txt.C_OUTPUT, txt.C_OUTPUT ]
            I = [ (txt.C_SWITCH, txt.C_DIGITAL ),
                  (txt.C_SWITCH, txt.C_DIGITAL ),
                  (txt.C_SWITCH, txt.C_DIGITAL ),
                  (txt.C_SWITCH, txt.C_DIGITAL ),
                  (txt.C_SWITCH, txt.C_DIGITAL ),
                  (txt.C_SWITCH, txt.C_DIGITAL ),
                  (txt.C_SWITCH, txt.C_DIGITAL ),
                  (txt.C_SWITCH, txt.C_DIGITAL ) ]
            txt.setConfig(M, I)
            txt.updateConfig()

        self.w.show() 
        self.exec_()        

    def green_time_changed(self, val):
        self.green_time_lbl.setText("{:d} Sekunden".format(val))

    def blink_toggle(self):
        global txt
        global state
        if state != "blinking_on" and state != "blinking_off":
            txt.setPwm(PED_RED,0)   # pedestrians: red off
            txt.setPwm(PED_GRN,0)   # pedestrians: green off
            txt.setPwm(CAR_RED,0)   # cars: red off
            txt.setPwm(CAR_GRN,0)   # cars: green off
            txt.setPwm(CAR_YLW,512) # cars: yellow on
            self.timer.setSingleShot(False)
            self.timer.start(1000)  # wait one second
            state = "blinking_on"
        else:
            txt.setPwm(CAR_YLW,0)   # cars: yellow off
            self.timer.setSingleShot(False)
            self.timer.start(100)
            state = "idle"
        
    def do_ampel(self):
        global txt
        global state

        print("Timer in state", state)
        
        if state == "idle":
            # button pressed
            if txt.getCurrentInput(0):
                self.timer.setSingleShot(True)
                txt.setPwm(PED_RED,512) # pedestrians: red on
                txt.setPwm(CAR_GRN,512) # cars: green on
                self.timer.start(5000)  # wait five seconds
                state = "wait_cars_green"
                
        elif state == "wait_cars_green":
            txt.setPwm(CAR_YLW,512)  # cars: yellow on
            txt.setPwm(CAR_GRN,0)    # cars: green off
            self.timer.start(2000)   # wait two seconds
            state = "wait_cars_yellow"
            
        elif state == "wait_cars_yellow":
            txt.setPwm(CAR_YLW,0)    # cars: yellow off
            txt.setPwm(CAR_RED,512)  # cars: red on
            self.timer.start(2000)   # wait two seconds
            state = "wait_cars_red"

        elif state == "wait_cars_red":
            txt.setPwm(PED_RED,0)    # pedestrians: red off
            txt.setPwm(PED_GRN,512)  # pedestrians: green on
            self.timer.start(self.dial.value() * 1000)   # wait X seconds
            state = "wait_ped_green"

        elif state == "wait_ped_green":
            txt.setPwm(PED_RED,512)  # pedestrians: red on
            txt.setPwm(PED_GRN,0)    # pedestrians: green off
            self.timer.start(2000)   # wait two seconds
            state = "wait_ped_red"

        elif state == "wait_ped_red":
            txt.setPwm(CAR_YLW,512)  # cars: yellow on
            self.timer.start(2000)   # wait two seconds
            state = "wait_cars_yellow2"

        elif state == "wait_cars_yellow2":
            txt.setPwm(CAR_RED,0)    # cars: red off
            txt.setPwm(CAR_YLW,0)    # cars: yellow off
            txt.setPwm(CAR_GRN,512)  # cars: green on
            self.timer.start(5000)   # wait five seconds
            state = "wait_cars_green2"

        elif state == "wait_cars_green2":
            txt.setPwm(CAR_GRN,0)    # cars: green off
            txt.setPwm(PED_RED,0)    # pedestrians: red off
            self.timer.setSingleShot(False)
            self.timer.start(100)    # poll button
            state = "idle"

        elif state == "blinking_on":
            txt.setPwm(CAR_YLW,0)    # cars: yellow off
            state = "blinking_off"

        elif state == "blinking_off":
            txt.setPwm(CAR_YLW,512)  # cars: yellow on
            state = "blinking_on"

        else:
            print("Unknown state", state)
                
if __name__ == "__main__":
    FtcGuiApplication(sys.argv)
