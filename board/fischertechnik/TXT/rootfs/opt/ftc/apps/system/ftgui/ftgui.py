#! /usr/bin/env python3
# -*- coding: utf-8 -*-
#
import sys, os, subprocess,time
from TxtStyle import *

SCRIPT = "/opt/fischertechnik/start-txtcontrol"

# subclass the txtwidget to catch the close event
class FTGUIBaseWidget(TxtBaseWidget):
    def __init__(self):
        TxtBaseWidget.__init__(self)

    def close(self):
        subprocess.Popen(["sudo", SCRIPT, "stop-main"])
        time.sleep(3)
        TxtBaseWidget.close(self)

class FtcGuiApplication(TxtApplication):
    def __init__(self, args):
        TxtApplication.__init__(self, args)

        self.w = FTGUIBaseWidget()
        self.w.show()

        subprocess.Popen(["sudo", SCRIPT, "start-main"])
        self.exec_()
        
if __name__ == "__main__":
    FtcGuiApplication(sys.argv)
