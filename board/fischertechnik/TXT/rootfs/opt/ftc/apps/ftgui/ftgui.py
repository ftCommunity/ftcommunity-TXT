#! /usr/bin/env python
# -*- coding: utf-8 -*-
#
import sys, os, subprocess,time
from TxtStyle import *

SCRIPT = "/opt/fischertechnik/start-txtcontrol"

class FtcGuiApplication(TxtApplication):
    def __init__(self, args):
        TxtApplication.__init__(self, args)

        self.w = QWidget()
        self.w.setFixedSize(240, 320)
        self.w.setObjectName("centralwidget")

        # start thread to monitor power button
        self.buttonThread = ButtonThread()
        self.connect( self.buttonThread, SIGNAL("power_button_released()"), self.stop )
        self.buttonThread.start()
        self.w.showFullScreen()

        subprocess.Popen([SCRIPT, "start-main"])
        self.exec_()

    def stop(self):
        subprocess.Popen([SCRIPT, "stop-main"])
        time.sleep(3)
        self.w.close()
        
        
if __name__ == "__main__":
    FtcGuiApplication(sys.argv)
