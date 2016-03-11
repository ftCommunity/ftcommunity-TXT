#! /usr/bin/env python
# -*- coding: utf-8 -*-

import ConfigParser
import sys, os
from PyQt4.QtCore import *
from PyQt4.QtGui import *

# make sure all file access happens relative to this script
base = os.path.dirname(os.path.realpath(__file__))

# The TXTs window title bar
class TxtTitle(QLabel):
    def __init__(self,str):
        QLabel.__init__(self,str)
        self.setObjectName("titlebar")
        self.setAlignment(Qt.AlignCenter)

# The TXT does not use windows. Instead we just paint custom 
# toplevel windows fullscreen
class TxtTopWidget(QWidget):
    def __init__(self,str):
        QWidget.__init__(self)
        # the setFixedSize is only needed for testing on a desktop pc
        # the centralwidget name makes sure the themes background 
        # gradient is being used
        self.setFixedSize(240, 320)
        self.setObjectName("centralwidget")

        # create a vertical layout and put all widgets inside
        self.layout = QVBoxLayout()
        self.layout.addWidget(TxtTitle(str))
        self.layout.setContentsMargins(0,0,0,0)

        self.setLayout(self.layout)        

    def addWidget(self,w):
        self.layout.addWidget(w)

        # TXT windows are always fullscreen
    def show(self):
        # if the FTC_GUI_MANAGED enviroment variable is set we
        # don't go fullscreen. Useful for testing in a PC
        if os.environ.has_key('FTC_GUI_MANAGED'):
            QWidget.show(self)
        else:
            QWidget.showFullScreen(self)

class FtcGuiApplication(QApplication):
    def __init__(self, args):
        QApplication.__init__(self, args)
        # load stylesheet from the same place the script was loaded from
        with open(base + "/txt.qss","r") as fh:
            self.setStyleSheet(fh.read())
            fh.close()

        self.addWidgets()
        self.exec_()        

    def launch(self,clicked):
        executable = self.sender().property("executable").toString()
        print "Lauch " + executable
        os.system(str(executable + " &"))
        
    def addWidgets(self):
        self.w = TxtTopWidget("TXT")

        self.gridw = QWidget()
        self.gridw.setObjectName("icongrid")
        self.grid = QGridLayout()
        self.grid.setSpacing(0)
        self.grid.setContentsMargins(0,0,0,0)

        # search for apps
        iconnr = 0
        for app_dir in os.listdir(base + "/apps"):
            manifestfile = base + "/apps/" + app_dir + "/manifest"
            if os.path.isfile(manifestfile):
                manifest = ConfigParser.RawConfigParser()
                manifest.read(manifestfile)

                # get various fields from manifest
                appname = manifest.get('app', 'name')
                executable = base + "/apps/" + app_dir + "/" + manifest.get('app', 'exec')
                iconname = base + "/apps/" + app_dir + "/" + manifest.get('app', 'icon')

                # the icon consists of the icon and the text below in a vbox
                vboxw = QWidget()
                vboxw.setObjectName("icongrid")
                vbox = QVBoxLayout()
                vbox.setSpacing(0)
                vbox.setContentsMargins(0,0,0,0)
                vboxw.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)

                pix = QPixmap(iconname)
                icn = QIcon(pix)
                but = QPushButton()
                but.setIcon(icn)
                but.setIconSize(pix.size())
                but.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
                but.clicked.connect(self.launch)

                # set properties from manifest settings
                but.setProperty("executable", executable)
                but.setObjectName("iconbut")
                but.setFixedSize(QSize(72,72))
                vbox.addWidget(but)

                lbl = QLabel(appname)
                lbl.setObjectName("iconlabel")
                lbl.setAlignment(Qt.AlignCenter)
                lbl.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
                vbox.addWidget(lbl)

                vboxw.setLayout(vbox)
                self.grid.addWidget(vboxw,iconnr/3,iconnr%3)
                iconnr = iconnr + 1

        # fill rest of grid with empty widgets
        while iconnr < 9:
            empty = QWidget()
            empty.setObjectName("noicon")
            empty.setFixedSize(QSize(72,72))
            empty.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
            self.grid.addWidget(empty,iconnr/3,iconnr%3)
            iconnr = iconnr + 1

        self.gridw.setLayout(self.grid)
        self.w.addWidget(self.gridw);
        self.w.show() 
 
# Only actually do something if this script is run standalone, so we can test our 
# application, but we're also able to import this program without actually running
# any code.
if __name__ == "__main__":
    app = FtcGuiApplication(sys.argv)
