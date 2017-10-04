#! /usr/bin/env python3
# -*- coding: utf-8 -*-
#
import sys, os, subprocess, time, re
from TouchStyle import *
from launcher import LauncherPlugin, MessageDialog
from PyQt4.QtCore import QTimer

class DisplaySettingsPlugin(LauncherPlugin):

    def __init__(self, application):
        LauncherPlugin.__init__(self, application)
        self.mainWindow = TouchWindow(QCoreApplication.translate("main", "Settings"))
        rotation = 0
        try:
          config = open("/etc/default/launcher", "r")
          re_match = re.search("SCREEN_ROTATION=(\d+)", config.readline())
          if re_match:
            rotation = int(re_match.group(1))
          config.close()
        except:
          pass
        self.vbox = QVBoxLayout()
        self.mainWindow.centralWidget.setLayout(self.vbox)
        self.rotate = QComboBox()
        self.rotate.addItem(QCoreApplication.translate("main", "Rotate 0°"))
        self.rotate.addItem(QCoreApplication.translate("main", "Rotate 90°"))
        self.rotate.addItem(QCoreApplication.translate("main", "Rotate 180°"))
        self.rotate.addItem(QCoreApplication.translate("main", "Rotate 270°"))
        rot_idx = int(rotation / 90)
        if (rot_idx < 4):
          self.rotate.setCurrentIndex(rot_idx)
        self.rotate.activated.connect(self.on_change_orientation)
        self.vbox.addWidget(self.rotate)
        self.calibrate = QPushButton(QCoreApplication.translate("main", "Calibrate touch"))
        self.calibrate.clicked.connect(self.on_calibrate_touchscreen)
        self.vbox.addWidget(self.calibrate)
        self.mainWindow.show()

    def on_calibrate_touchscreen(self):
        # make sure that only ts_calibrate reacts to touch events...
        old_window = self.mainWindow
        self.mainWindow = TouchBaseWidget()
        self.mainWindow.show()
        old_window.close()
        subprocess.run(["sudo", "/usr/bin/ts_calibrate"])
        self.restart_launcher(QCoreApplication.translate("main", "Activating new touch screen calibration..."))

    def on_change_orientation(self, index):
        rotation = index * 90
        config = open("/etc/default/launcher", "w")
        config.write("SCREEN_ROTATION=%i\n" % rotation)
        config.close()
        self.restart_launcher(QCoreApplication.translate("main", "Rotating screen to %i°...") % rotation)

    def restart_launcher(self, text):
        old_window = self.mainWindow
        self.mainWindow = TouchBaseWidget()
        layout = QVBoxLayout()
        layout.addStretch()

        lbl = QLabel(text)
        lbl.setWordWrap(True);
        lbl.setAlignment(Qt.AlignCenter)
        layout.addWidget(lbl)

        layout.addStretch()
        self.mainWindow.setLayout(layout)        
        self.mainWindow.show()
        old_window.close()
        # the 0 msec timer makes sure that the actual restart does
        # not happen before the message window has been displayed...
        QTimer.singleShot(0, self.do_restart_launcher)

    def do_restart_launcher(self):
        subprocess.run(["sudo", "/etc/init.d/S90launcher", "restart"])


if __name__ == "__main__":
    class FtcGuiApplication(TouchApplication):
        def __init__(self, args):
            super().__init__(args)
            module = DisplaySettingsPlugin(self)
            self.exec_()
    FtcGuiApplication(sys.argv)
else:
    def createPlugin(launcher):
        return DisplaySettingsPlugin(launcher)

