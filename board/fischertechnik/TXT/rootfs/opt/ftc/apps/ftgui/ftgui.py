#! /usr/bin/env python
# -*- coding: utf-8 -*-
#
import sys, os, subprocess,time
from PyQt4.QtCore import *
from PyQt4.QtGui import *

# import TXT style
base = os.path.dirname(os.path.realpath(__file__)) + "/../../"
sys.path.append(base)
from txt import *

SCRIPT = "/opt/fischertechnik/start-txtcontrol"
#SCRIPT = "echo"

class FtcGuiApplication(QApplication):
    def __init__(self, args):
        QApplication.__init__(self, args)
        # load stylesheet from the same place the script was loaded from
        with open(base + "txt.qss","r") as fh:
            self.setStyleSheet(fh.read())
            fh.close()

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
#        subprocess.Popen([SCRIPT, "stop-main"])
#        time.sleep(3)
        print "done"

    def stop(self):
        print "Stopping GUI ..."
        subprocess.Popen([SCRIPT, "stop-main"])
        time.sleep(3)
        self.w.close()
        
        
if __name__ == "__main__":
    FtcGuiApplication(sys.argv)
