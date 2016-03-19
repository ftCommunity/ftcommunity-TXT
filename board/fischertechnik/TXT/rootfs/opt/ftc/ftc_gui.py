#! /usr/bin/env python
# -*- coding: utf-8 -*-

# This is the fischertechnik community app launcher

import ConfigParser
import sys, os, subprocess, threading
import SocketServer

from PyQt4.QtCore import *
from PyQt4.QtGui import *
from PyQt4.QtNetwork import *

CTRL_PORT = 9000

# make sure all file access happens relative to this script
base = os.path.dirname(os.path.realpath(__file__))

class MessageDialog(QDialog):
    def __init__(self,base,str):
        QDialog.__init__(self)
        self.setFixedSize(240, 320)
        self.setObjectName("centralwidget")
        self.layout = QVBoxLayout()

        self.setLayout(self.layout)        

        self.layout.addStretch()

        lbl = QLabel(str)
        lbl.setWordWrap(True);
        lbl.setAlignment(Qt.AlignCenter)
        self.layout.addWidget(lbl)

        self.layout.addStretch()

    def exec_(self):
        QDialog.showFullScreen(self)
        QDialog.exec_(self)

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

        # create TCP server so other programs can request a icon list refresh
        # or launch an app
        self.tcpServer = QTcpServer(self)               
        self.tcpServer.listen(QHostAddress("0.0.0.0"), CTRL_PORT)
        self.connect(self.tcpServer, SIGNAL("newConnection()"), 
                    self.addConnection)
        self.connections = []

        self.addWidgets()
        self.exec_()        

    def addConnection(self):
        clientConnection = self.tcpServer.nextPendingConnection()
        self.connections.append(clientConnection)

        self.connect(clientConnection, SIGNAL("readyRead()"), 
                self.receiveMessage)
        self.connect(clientConnection, SIGNAL("disconnected()"), 
                self.removeConnection)
        self.connect(clientConnection, SIGNAL("error()"), 
                self.socketError)

    def receiveMessage(self):
        # check clients for data
        for s in self.connections:
            if s.canReadLine():
                line = str(s.readLine()).strip()
                cmd = line.split()[0]
                parm = line[len(cmd):].strip()
                if cmd == "rescan":
                    self.rescan.emit()
                elif cmd == "launch":
                    self.launch.emit(parm)
                elif cmd == "msg":
                    self.message.emit(parm)
                else:
                    print "Unknown command ", cmd

    def removeConnection(self):
        pass

    def socketError(self):
        pass

    def do_launch(self,clicked):
        executable = self.sender().property("executable").toString()
        print "Lauch " + executable 
        subprocess.Popen(str(executable))

    rescan = pyqtSignal()
    launch = pyqtSignal(str)
    message = pyqtSignal(str)

    @pyqtSlot()
    def on_rescan(self):
        self.addIcons(self.grid)

    @pyqtSlot(str)
    def on_launch(self, name):
        # check if there's an icon with that name
        for i in range(0,self.grid.count()):
            item = self.grid.itemAt(i)
            if item:
                if item.widget().property("appname").toString() == name:
                    executable = item.widget().property("executable").toString()
                    print "Lauch " + executable 
                    subprocess.Popen(str(executable))

    @pyqtSlot(str)
    def on_message(self, str):
        print "Message:", str
        MessageDialog(base, str).exec_()

    def addIcons(self, grid):
        # search for apps
        iconnr = 0
        for app_dir in sorted(os.listdir(base + "/apps")):
            app_path = base + "/apps/" + app_dir + "/"
            manifestfile = app_path + "manifest"
            if os.path.isfile(manifestfile) :
                manifest = ConfigParser.RawConfigParser()
                manifest.read(manifestfile)

                # get various fields from manifest
                appname = manifest.get('app', 'name')
                executable = app_path + manifest.get('app', 'exec')
                iconname = app_path + manifest.get('app', 'icon')

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
                but.clicked.connect(self.do_launch)

                # set properties from manifest settings on clickable icon to
                # allow click event to launch the matching app
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

                # check if there's already something and delete it
                previtem = grid.itemAtPosition(iconnr/3,iconnr%3);
                if previtem:
                    previtem.widget().deleteLater()

                # set properties on element stored in grid to 
                # allow network launch to get the executable name
                # from it
                vboxw.setProperty("appname", appname)
                vboxw.setProperty("executable", executable)
                grid.addWidget(vboxw,iconnr/3,iconnr%3)
                iconnr = iconnr + 1

        # fill rest of grid with empty widgets
        while iconnr < 9:
            empty = QWidget()
            empty.setObjectName("noicon")
            empty.setFixedSize(QSize(72,72))
            empty.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
            # check if there's already something
            previtem = grid.itemAtPosition(iconnr/3,iconnr%3);
            if previtem:
                previtem.widget().deleteLater()
            grid.addWidget(empty,iconnr/3,iconnr%3)
            iconnr = iconnr + 1


    def addWidgets(self):
        # receive signals from network server
        self.rescan.connect(self.on_rescan)
        self.launch.connect(self.on_launch)
        self.message.connect(self.on_message)

        self.w = TxtTopWidget("TXT")
        
        self.gridw = QWidget()
        self.gridw.setObjectName("icongrid")
        self.grid = QGridLayout()
        self.grid.setSpacing(0)
        self.grid.setContentsMargins(0,0,0,0)

        self.addIcons(self.grid)

        self.gridw.setLayout(self.grid)
        self.w.addWidget(self.gridw);
        self.w.show() 
 
# Only actually do something if this script is run standalone, so we can test our 
# application, but we're also able to import this program without actually running
# any code.
if __name__ == "__main__":
    app = FtcGuiApplication(sys.argv)
