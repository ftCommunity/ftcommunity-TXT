#! /usr/bin/env python3
# -*- coding: utf-8 -*-
#
import sys, os
from TxtStyle import *
from launcher import LauncherPlugin
from PyQt5 import QtCore

VERSION_FILE = "/etc/fw-ver.txt"

class LicenseDialog(TxtDialog):
    def __init__(self,title,lic,parent):
        TxtDialog.__init__(self, title, parent)
        
        txt = QTextEdit()
        txt.setReadOnly(True)
        txt.setTextInteractionFlags (QtCore.Qt.NoTextInteraction)    
        QScroller.grabGesture(txt.viewport(), QScroller.LeftMouseButtonGesture);

        # load gpl from disk
        name = os.path.join(os.path.dirname(os.path.realpath(__file__)), lic)
        text=open(name, encoding="utf-8").read()
        txt.setPlainText(text)

        self.setCentralWidget(txt)

class SmallLabel(QLabel):
    def __init__(self, str, parent=None):
        super(SmallLabel, self).__init__(str, parent)
        self.setObjectName("smalllabel")
        self.setWordWrap(True)

class VersionWidget(QWidget):
    def __init__(self,title,str,parent=None):
        super(VersionWidget,self).__init__(parent)
        vbox = QVBoxLayout()
        vbox.addWidget(QLabel(title))
        vbox.addWidget(SmallLabel(str))
        self.setLayout(vbox)

class VersionsDialog(TxtDialog):
    def str_from_file(self, fname):
        try:
            return open(fname).readline().rstrip("\0").strip()
        except:
            return None

    def __init__(self,title,parent):
        TxtDialog.__init__(self, title, parent)

        vbox_w = QWidget(self.centralWidget)

        # add various version info
        vbox = QVBoxLayout()

        # ---------- Raspberry Pi version ----------
        if self.str_from_file("/sys/firmware/devicetree/base/model"):
            vbox.addWidget(VersionWidget(QCoreApplication.translate("VersionsDialog", "System"),
                                         self.str_from_file("/sys/firmware/devicetree/base/model")))

        if self.str_from_file("/etc/tx-pi-ver.txt"):
            vbox.addWidget(VersionWidget(QCoreApplication.translate("VersionsDialog", "TX-Pi Version"),
                                         self.str_from_file("/etc/tx-pi-ver.txt")))
        
        # -------- firmware version ------------
        if self.str_from_file(VERSION_FILE):
            vbox.addWidget(VersionWidget(QCoreApplication.translate("VersionsDialog", "Firmware"),
                                         self.str_from_file(VERSION_FILE)))

        # --------- kernel version -----------
        if self.str_from_file("/proc/version"):
            vbox.addWidget(VersionWidget(QCoreApplication.translate("VersionsDialog", "Linux"),
                                         self.str_from_file("/proc/version").split()[2]))

        # --------- python version ----------
        py_ver_str = ""
        for i in range(len(sys.version_info)):
            py_ver_str += str(sys.version_info[i])
            if(i < 2): py_ver_str += "."
        vbox.addWidget(VersionWidget("Python", py_ver_str))

        # --------- ftrobopy version ----------
        try:
            import ftrobopy
            vbox.addWidget(VersionWidget("ftrobopy", ftrobopy.version()))
        except:
            pass

        # --------- qt -----------
        vbox.addWidget(VersionWidget("Qt", QT_VERSION_STR))

        vbox.addWidget(VersionWidget("PyQt", PYQT_VERSION_STR))

        # -------- opencv -------
        try:
            import cv2
            # --------- ftrobopy version ----------
            vbox.addWidget(VersionWidget("opencv", cv2.__version__))
        except:
            pass

        
        vbox_w.setLayout(vbox)

        # put everything inside a scroll area
        scroll = QScrollArea(self.centralWidget)
        QScroller.grabGesture(scroll, QScroller.LeftMouseButtonGesture);
        
        scroll.setWidget(vbox_w)

        self.setCentralWidget(scroll)
        
class AboutPlugin(LauncherPlugin):
    def __init__(self, application):
        LauncherPlugin.__init__(self, application)

        translator = QTranslator()
        path = os.path.dirname(os.path.realpath(__file__))
        translator.load(self.locale(), os.path.join(path, "about_"))
        self.installTranslator(translator)
        
        # create the empty main window
        self.mainWindow = TxtWindow(QCoreApplication.translate("FtcGuiApplication","About"))

        menu = self.mainWindow.addMenu()
        menu_ver = menu.addAction(QCoreApplication.translate("FtcGuiApplication","Versions"))
        menu_ver.triggered.connect(self.show_version)

        menu.addSeparator()
        
        menu_lic_gpl = menu.addAction(QCoreApplication.translate("FtcGuiApplication","GPL license"))
        menu_lic_gpl.triggered.connect(self.show_license_gpl)
        menu_lic_lgpl = menu.addAction(QCoreApplication.translate("FtcGuiApplication","LGPL license"))
        menu_lic_lgpl.triggered.connect(self.show_license_lgpl)
        menu_lic_mit = menu.addAction(QCoreApplication.translate("FtcGuiApplication","MIT license"))
        menu_lic_mit.triggered.connect(self.show_license_mit)

        self.vbox = QVBoxLayout()

        self.vbox.addStretch()
        
        # and add some text
        self.txt = QLabel(QCoreApplication.translate("FtcGuiApplication",
                                                     "Firmware for fischertechnik - "
                                                     "community edition"))
        self.txt.setObjectName("smalllabel")
        self.txt.setWordWrap(True)
        self.txt.setAlignment(Qt.AlignCenter)
        self.vbox.addWidget(self.txt)

        self.vbox.addStretch()

        self.c = QLabel(QCoreApplication.translate("FtcGuiApplication","(c) 2016-2024 the ft:community"))
        self.c.setObjectName("tinylabel")
        self.c.setWordWrap(True)
        self.c.setAlignment(Qt.AlignCenter)
        self.vbox.addWidget(self.c)

        self.vbox.addStretch()
        self.mainWindow.centralWidget.setLayout(self.vbox)

        self.mainWindow.show()
 
    def show_license_gpl(self):
        dialog = LicenseDialog(QCoreApplication.translate("FtcGuiApplication", "GPL"),
                               QCoreApplication.translate("FtcGuiApplication", "gpl.txt"), self.mainWindow)
        dialog.exec_()

    def show_license_lgpl(self):
        dialog = LicenseDialog(QCoreApplication.translate("FtcGuiApplication", "LGPL"),
                               QCoreApplication.translate("FtcGuiApplication", "lgpl.txt"), self.mainWindow)
        dialog.exec_()

    def show_license_mit(self):
        dialog = LicenseDialog(QCoreApplication.translate("FtcGuiApplication", "MIT"),
                               QCoreApplication.translate("FtcGuiApplication", "mit.txt"), self.mainWindow)
        dialog.exec_()

    def show_version(self):
        dialog = VersionsDialog(QCoreApplication.translate("FtcGuiApplication", "Versions"), self.mainWindow)
        dialog.exec_()

if __name__ == "__main__":
    class FtcGuiApplication(TouchApplication):
        def __init__(self, args):
            super().__init__(args)
            module = AboutPlugin(self)
            self.exec_()
    FtcGuiApplication(sys.argv)
else:
    def createPlugin(launcher):
        return AboutPlugin(launcher)

