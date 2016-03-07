#! /usr/bin/env python
# -*- coding: utf-8 -*-
# http://apps.javispedro.com/nit/hicg/
import sys, os
from PyQt4.QtCore import *
from PyQt4.QtGui import *

# make sure all file access happens relative to this script
base = os.path.dirname(os.path.realpath(__file__))

# The TXTs window title bar
class TxtTitle(QWidget):
    def __init__(self,str):
        QWidget.__init__(self)
        self.setObjectName("titlebar")
        self.hbox = QHBoxLayout()

        self.lbl = QLabel(str)
        self.lbl.setAlignment(Qt.AlignCenter)
        self.lbl.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Minimum)
        self.hbox.addWidget(self.lbl)

        self.setLayout(self.hbox)
        self.setVisible(True)

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
        appname = self.sender().property("appname").toString()
        print "Lauch " + appname
        app = str(base + "/apps/" + appname + "/" + appname + ".py &")
        os.system(app)
        
    def addWidgets(self):
        self.w = TxtTopWidget("TXT")

        self.gridw = QWidget()
        self.gridw.setObjectName("icongrid")
        self.grid = QGridLayout()
        self.grid.setSpacing(0)
        self.grid.setContentsMargins(0,0,0,0)

        # search for apps
        iconnr = 0
        for name in os.listdir(base + "/apps"):
            iconname = base + "/apps/" + name + "/icon.svg"
            if os.path.isfile(iconname):
                pix = QPixmap(iconname)
                icn = QIcon(pix)
                but = QPushButton()
                but.setIcon(icn)
                but.setIconSize(pix.size())
                but.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
                but.clicked.connect(self.launch)
                but.setProperty("appname", name)
                but.setObjectName("iconbut")
                but.setFixedSize(QSize(72,72))
                self.grid.addWidget(but,iconnr/3,iconnr%3)
                iconnr = iconnr + 1

        # fill rest of grid with empty widgets
        while iconnr < 9:
            empty = QWidget()
            empty.setObjectName("noicon")
            empty.setFixedSize(QSize(72,72))
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
