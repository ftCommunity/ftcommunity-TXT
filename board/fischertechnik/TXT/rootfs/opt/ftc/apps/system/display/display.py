#! /usr/bin/env python3
# -*- coding: utf-8 -*-
#
import sys, os, subprocess, time, re
from TouchStyle import *
from launcher import LauncherPlugin, MessageDialog

from PyQt5.QtCore import QTimer

class DisplaySettingsPlugin(LauncherPlugin):

    def __init__(self, application):
        LauncherPlugin.__init__(self, application)

        translator = QTranslator()
        path = os.path.dirname(os.path.realpath(__file__))
        translator.load(self.locale(), os.path.join(path, "display_"))
        self.installTranslator(translator)

        self.mainWindow = TouchWindow(QCoreApplication.translate("main", "Display"))
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
        self.rotate.addItem(QCoreApplication.translate("main", "Rotate 0"))
        self.rotate.addItem(QCoreApplication.translate("main", "Rotate 90"))
        self.rotate.addItem(QCoreApplication.translate("main", "Rotate 180"))
        self.rotate.addItem(QCoreApplication.translate("main", "Rotate 270"))
        rot_idx = int(rotation / 90)
        if (rot_idx < 4):
          self.rotate.setCurrentIndex(rot_idx)
        self.rotate.activated.connect(self.on_change_orientation)
        self.vbox.addWidget(self.rotate)
        self.calibrate = QPushButton(QCoreApplication.translate("main", "Calibrate\ntouchscreen"))
        self.calibrate.clicked.connect(self.on_calibrate_touchscreen)
        self.vbox.addWidget(self.calibrate)
        self.savecalibration = QPushButton(QCoreApplication.translate("main", "Save\ncalibration"))
        self.savecalibration.clicked.connect(self.on_unset_reset_calibration_flag)
        self.vbox.addWidget(self.savecalibration)
        self.mainWindow.show()

    def on_calibrate_touchscreen(self):
        # make sure that only ts_calibrate reacts to touch events...
        self.popup = TouchDialog("", self.mainWindow)
        self.popup.show()

        subprocess.run(["sudo", "/sbin/calibrate-touchscreen", "calibrate"])
        self.restart_launcher(QCoreApplication.translate("main", "Activating new touchscreen calibration..."))

    def on_change_orientation(self, index):
        rotation = index * 90
        config = open("/etc/default/launcher", "w")
        config.write("SCREEN_ROTATION=%i\n" % rotation)
        config.close()
        msg = QCoreApplication.translate("main", "Rotating screen to %i...")
        self.restart_launcher(msg % rotation)

    def restart_launcher(self, text):
        self.popup = TouchDialog("", self.mainWindow)
        layout = self.popup.layout
        layout.addStretch()

        lbl = QLabel(text)
        lbl.setWordWrap(True);
        lbl.setAlignment(Qt.AlignCenter)
        layout.addWidget(lbl)

        layout.addStretch()
        self.popup.show()
        
        # the timer makes sure that the actual restart does
        # not happen before the message window has been displayed...
        self.restartTimer = QTimer()
        self.restartTimer.singleShot(2000, self.do_restart_launcher)

    def do_restart_launcher(self):
        # We need to restart the X server and ourselves.
        cmd="sudo /etc/init.d/S90launcher restart"

        self.p = subprocess.Popen(args=cmd, shell=True,
                                  start_new_session=True,
                                  stdin=subprocess.DEVNULL,
                                  stdout=subprocess.DEVNULL,
                                  stderr=subprocess.DEVNULL)

    def unset_reset_calibration_flag(self):
        subprocess.run(["sudo", "/sbin/calibrate-touchscreen", "commit"])

    def on_unset_reset_calibration_flag(self):
        msg = TouchMessageBox(QCoreApplication.translate("main", "Save"), self.mainWindow)
        msg.addConfirm()
        msg.setCancelButton()
        msg.setText(QCoreApplication.translate("main", "Do you really want to save the current touchscreen calibration?"))
        msg.setPosButton(QCoreApplication.translate("main", "Save"))
        msg.setNegButton(QCoreApplication.translate("main", "No"))
        success, text = msg.exec_()
        if success == False or text == QCoreApplication.translate("main", "No"):
            return
        self.unset_reset_calibration_flag()


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

