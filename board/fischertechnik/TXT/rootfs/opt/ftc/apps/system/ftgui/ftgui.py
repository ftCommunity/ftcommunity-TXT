#! /usr/bin/env python3
# -*- coding: utf-8 -*-
#
import sys, os, subprocess,time
from TouchStyle import *
from launcher import LauncherPlugin

SCRIPT = "/opt/fischertechnik/start-txtcontrol"

# subclass the txtwidget to catch the close event
class FTGUIBaseWidget(TouchBaseWidget):
    def __init__(self):
        TouchBaseWidget.__init__(self)

    def close(self):
        subprocess.Popen(["sudo", SCRIPT, "stop-main"])
        time.sleep(3)
        TouchBaseWidget.close(self)

class FtcGuiPlugin(LauncherPlugin):
    def __init__(self, application):
        LauncherPlugin.__init__(self, application)

        self.w = FTGUIBaseWidget()
        self.w.show()

        subprocess.Popen(["sudo", SCRIPT, "start-main"])

if __name__ == "__main__":
    class FtcGuiApplication(TouchApplication):
        def __init__(self, args):
            super().__init__(args)
            module = FtcGuiPlugin(self)
            self.exec_()
    FtcGuiApplication(sys.argv)
else:
    def createPlugin(launcher):
        return FtcGuiPlugin(launcher)

