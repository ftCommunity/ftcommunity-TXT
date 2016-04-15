#! /usr/bin/env python3
# -*- coding: utf-8 -*-
#

import os, sys
from TxtStyle import *
from wedo import WeDo
from ctypes import *

class FtcGuiApplication(TxtApplication):
    def __init__(self, args):
        global wd
        TxtApplication.__init__(self, args)

        self.w = TxtWindow("WeDo")

        self.vbox = QVBoxLayout()

        try:
            wd = WeDo()
        except OSError as e:
            wd = None
            print(("Error", e))

        if wd == None:
            self.vbox.addStretch()
            err = QLabel("Error")
            err.setAlignment(Qt.AlignCenter)
            self.vbox.addWidget(err)
            lbl = QLabel("No WeDo hub found. Please make sure one is connected to the TXTs USB host port.")
            lbl.setObjectName("smalllabel")
            lbl.setWordWrap(True)
            lbl.setAlignment(Qt.AlignCenter)
        
            self.vbox.addWidget(lbl)
            self.vbox.addStretch()
        else:
            # everythings fine
            lbl = QLabel("Motor")
            lbl.setObjectName("smalllabel")
            lbl.setAlignment(Qt.AlignCenter)            
            self.vbox.addWidget(lbl)

            hbox_w = QWidget()
            hbox = QHBoxLayout()
            hbox_w.setLayout(hbox)
            
            but_l = QPushButton("Left")
            but_l.pressed.connect(self.on_mot_l_on)
            but_l.released.connect(self.on_mot_off)
            hbox.addWidget(but_l)

            but_r = QPushButton("Right")
            but_r.pressed.connect(self.on_mot_r_on)
            but_r.released.connect(self.on_mot_off)
            hbox.addWidget(but_r)
            
            self.vbox.addWidget(hbox_w)
            self.vbox.addStretch()

            timer = QTimer(self)
            timer.timeout.connect(self.update_sensors)
            timer.start(100);
    
            lbl = QLabel("Tilt")
            lbl.setObjectName("smalllabel")
            lbl.setAlignment(Qt.AlignCenter)            
            self.vbox.addWidget(lbl)
            self.tilt_lbl = QLabel("")
            self.tilt_lbl.setAlignment(Qt.AlignCenter)            
            self.vbox.addWidget(self.tilt_lbl)

            self.vbox.addStretch()

            lbl = QLabel("Distance")
            lbl.setObjectName("smalllabel")
            lbl.setAlignment(Qt.AlignCenter)            
            self.vbox.addWidget(lbl)
            self.dist_lbl = QLabel("")
            self.dist_lbl.setAlignment(Qt.AlignCenter)            
            self.vbox.addWidget(self.dist_lbl)
            
        self.w.centralWidget.setLayout(self.vbox)
        self.w.show() 
        self.exec_()        

    def update_sensors(self):
        global wd
        tilt = wd.tilt
        if tilt == None:
            self.tilt_lbl.setText("<no sensor>")
        elif tilt == 0:
            self.tilt_lbl.setText("flat")
        elif tilt == 1:
            self.tilt_lbl.setText("forward")
        elif tilt == 2:
            self.tilt_lbl.setText("left")
        elif tilt == 3:
            self.tilt_lbl.setText("right")
        elif tilt == 4:
            self.tilt_lbl.setText("backward")
        else:
            self.tilt_lbl.setText("whatever")
            
        dist = wd.distance
        if dist == None:
            self.dist_lbl.setText("<no sensor>")
        else:
            self.dist_lbl.setText("{:.1f}cm".format(dist))
            
    def on_mot_l_on(self):
        global wd
        wd.motor_a = -100
        
    def on_mot_r_on(self):
        global wd
        wd.motor_a = 100

    def on_mot_off(self):
        global wd
        wd.motor_a = 0
        
if __name__ == "__main__":
    FtcGuiApplication(sys.argv)
