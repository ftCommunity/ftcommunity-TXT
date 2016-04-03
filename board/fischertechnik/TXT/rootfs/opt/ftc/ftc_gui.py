#! /usr/bin/env python3
# -*- coding: utf-8 -*-

# This is the fischertechnik community app launcher

import configparser
import sys, os, subprocess, threading, math
import socketserver

from PyQt4.QtCore import *
from PyQt4.QtGui import *
from PyQt4.QtNetwork import *

THEME = "default"

CTRL_PORT = 9000

# make sure all file access happens relative to this script
base = os.path.dirname(os.path.realpath(__file__))

current_cathegory = "All"
current_page = 0

# keep track of running app
app = None
app_executable = ""

class MessageDialog(QDialog):
    def __init__(self,str):
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
class TxtTitle(QComboBox):
    def __init__(self,cathegories):
        QComboBox.__init__(self)
        self.setObjectName("titlebar")
        self.addItem("All")
        for i in cathegories:
            self.addItem(i)
 
# The TXT does not use windows. Instead we just paint custom 
# toplevel windows fullscreen
class TxtTopWidget(QWidget):
    def __init__(self,parent,cathegories):
        QWidget.__init__(self)
        # the setFixedSize is only needed for testing on a desktop pc
        # the centralwidget name makes sure the themes background 
        # gradient is being used
        self.setFixedSize(240, 320)
        self.setObjectName("centralwidget")

        # create a vertical layout and put all widgets inside
        self.layout = QVBoxLayout()
        self.cathegory_w = TxtTitle(cathegories)
        self.cathegory_w.activated[str].connect(parent.set_cathegory)
        self.layout.addWidget(self.cathegory_w)
        self.layout.setContentsMargins(0,0,0,0)

        self.setLayout(self.layout)        

    def addWidget(self,w):
        self.layout.addWidget(w)

        # TXT windows are always fullscreen
    def show(self):
        # if the FTC_GUI_MANAGED enviroment variable is set we
        # don't go fullscreen. Useful for testing in a PC
        if 'FTC_GUI_MANAGED' in os.environ:
            QWidget.show(self)
        else:
            QWidget.showFullScreen(self)

# https://github.com/anjinkristou/Qt-busy-indicator/blob/master/busyindicator.cpp
class BusyAnimation(QFrame):
    def __init__(self, app, parent=None):
        super(BusyAnimation, self).__init__(parent)
        self.setWindowFlags(Qt.Popup | Qt.Window)
        self.setObjectName("popup")
        self.resize(64, 64)
        pos = parent.mapToGlobal(QPoint(0,0))
        self.move(pos + QPoint(parent.width()/2-32, parent.height()/2-32))

        self.step = 0
        self.app = app

        # create a timer to close this window after 10 seconds at most
        self.etimer = QTimer(self)
        self.etimer.setSingleShot(True)
        self.etimer.timeout.connect(self.expired)
        self.etimer.start(10000)

        # animate at 10 frames/sec
        self.atimer = QTimer(self)
        self.atimer.timeout.connect(self.animate)
        self.atimer.start(100)

    def expired(self):
        # App launch expired without callback ...
        self.close()

    def animate(self):
        # if the app isn't running anymore then stop the
        # animation. This typically only happens for non-txt-styled
        # apps or with apps crashing.
        #
        # We might tell the user that the app ended unpexpectedly
        if self.app.poll():
            self.close()
            return

        # this is ugly ... we should be able to prevent
        # it not become invisble in the first place ...
        if not self.isVisible():
            self.show()

        self.step += 0.25
        self.repaint()

    def close(self):
        super(BusyAnimation, self).close()
        super(BusyAnimation, self).deleteLater()

    def paintEvent(self, event):
        radius = min(self.width(), self.height())/2.5
        painter = QPainter()
        painter.begin(self)

        painter.setRenderHint(QPainter.Antialiasing)
        painter.translate(self.width() / 2, self.height() / 2)
        painter.scale(radius, radius)

        painter.setPen(QPen(Qt.white))
        painter.setBrush(QBrush(QColor("#fcce04")))
        painter.drawEllipse(QPointF(0,0), math.cos(self.step), math.sin(self.step))

        painter.end()

class FtcGuiApplication(QApplication):
    def __init__(self, args):
        QApplication.__init__(self, args)
        # load stylesheet from the same place the script was loaded from
        self.setStyleSheet( "file:///" + base + "/themes/" + THEME + "/style.qss")

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
                line = str(s.readLine(), "utf-8").strip()
                if len(line) > 0:
                    cmd = line.split()[0]
                    parm = line[len(cmd):].strip()
                    if cmd == "rescan":
                        self.rescan.emit()
                    elif cmd == "launch":
                        self.launch.emit(parm)
                    elif cmd == "msg":
                        self.message.emit(parm)
                    elif cmd == "quit":
                        s.write("Bye\n")
                        s.close()
                    elif cmd == "get-app":
                        self.get_app.emit(s)
                    elif cmd == "stop-app":
                        self.stop_app.emit()
                    elif cmd == "app-running":
                        self.app_running.emit(int(parm))
                    else:
                        s.write("Unknown command\n")
                        print("Unknown command ", cmd)

    def removeConnection(self):
        pass

    def socketError(self):
        pass

    def app_is_running(self):
        global app

        if app == None:
            return False

        return app.poll() == None

    # this signal is received when an app reports it
    # has been launched
    @pyqtSlot(int)
    def on_app_running(self, pid):
        self.popup.close()

    def launch_app(self, executable):
        global app, app_executable
        print("Lauch " + executable)

        if self.app_is_running():
            print("Still one app running!")
            return

        app_executable = executable
        app = subprocess.Popen(str(executable))

        # display some busy icon
        self.popup = BusyAnimation(app, self.w)
        self.popup.show()
        
    def do_launch(self,clicked):
        self.launch_app(str(self.sender().property("executable")))

    rescan = pyqtSignal()
    launch = pyqtSignal(str)
    message = pyqtSignal(str)
    get_app = pyqtSignal(QTcpSocket)
    stop_app = pyqtSignal()
    app_running = pyqtSignal(int)

    @pyqtSlot()
    def on_rescan(self):
        global current_page
        # return to page 0 as the number of icons may have
        # been changed and the current page may not exist anymore
        current_page = 0
        self.addIcons(self.grid)

    @pyqtSlot(QTcpSocket)
    def on_get_app(self, s):
        global app_executable
        if self.app_is_running():
            s.write(app_executable)
        s.write("\n")

    @pyqtSlot()
    def on_stop_app(self):
        global app
        if self.app_is_running():
            app.kill()
            while app.poll() == None:
                pass

    @pyqtSlot(str)
    def on_launch(self, name):
        print("Net req to launch", name)

        # search for an app with that name
        # get list of all subdirectories in the application directory
        app_dirs = sorted(os.listdir(base + "/apps"))

        # extract all those that have a manifest file
        for app_dir in app_dirs:
            app_path = base + "/apps/" + app_dir + "/"
            manifestfile = app_path + "manifest"
            if os.path.isfile(manifestfile):
                manifest = configparser.RawConfigParser()
                manifest.read(manifestfile)
                if manifest.has_option('app', 'exec'):
                    if app_dir + "/" + manifest.get('app', 'exec') == name:
                        executable = app_path + manifest.get('app', 'exec')
                        self.launch_app(executable)

    @pyqtSlot(str)
    def on_message(self, str):
        MessageDialog(str).exec_()

    # read the manifet files of all installed apps and scan them
    # for their cathegory. Generate a unique set of cathegories from this
    def scan_cathegories(self):
        # get list of all subdirectories in the application directory
        app_dirs = sorted(os.listdir(base + "/apps"))

        # extract all those that have a manifest file
        cathegories = set()
        for app_dir in app_dirs:
            app_path = base + "/apps/" + app_dir + "/"
            manifestfile = app_path + "manifest"
            if os.path.isfile(manifestfile):
                manifest = configparser.RawConfigParser()
                manifest.read(manifestfile)
                if manifest.has_option('app', 'cathegory'):
                    cathegories.add(manifest.get('app', 'cathegory'))
                else:
                    print("App has no cathegory:", app_dir)

        return sorted(cathegories)

    # handler of the "next" button
    def do_next(self):
        global current_page
        current_page += 1
        self.addIcons(self.grid)

    # handler of the "prev" button
    def do_prev(self):
        global current_page
        current_page -= 1
        self.addIcons(self.grid)

    # create an icon with label
    def createIcon(self, iconfile=None, on_click=None, appname=None, executable=None):
        # the icon consists of the icon and the text below in a vbox
        vboxw = QWidget()
        vbox = QVBoxLayout()
        vbox.setSpacing(0)
        vbox.setContentsMargins(0,0,0,0)
        vboxw.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        if iconfile:
            pix = QPixmap(iconfile)
            icn = QIcon(pix)
            but = QPushButton()
            but.setIcon(icn)
            but.setIconSize(pix.size())
            but.clicked.connect(on_click)
            # set properties from manifest settings on clickable icon to
            # allow click event to launch the appropriate app
            but.setProperty("executable", executable)
            but.setFlat(True)
        else:
            but = QWidget()

        but.setFixedSize(QSize(72,72))
        but.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        vbox.addWidget(but)

        lbl = QLabel(appname)
        lbl.setObjectName("iconlabel")
        lbl.setAlignment(Qt.AlignCenter)
        lbl.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        vbox.addWidget(lbl)

        vboxw.setLayout(vbox)
        vboxw.setProperty("appname", appname)
        vboxw.setProperty("executable", executable)
        
        return vboxw

    # add and icon to the grid. Remove any previous icon
    def addIcon(self, grid, w, index):
        previtem = grid.itemAtPosition(index/3, index%3);
        if previtem: previtem.widget().deleteLater()
        grid.addWidget(w,index/3, index%3)

    # add all icons to the grid
    def addIcons(self, grid):
        global current_page
        global current_cathegory

        iconnr = 0

        # get list of all directories in the application directory
        app_dirs = sorted(os.listdir(base + "/apps"))

        # extract all those that have a manifest file an check for
        # current cathegory
        app_list = []
        for app_dir in app_dirs:
            manifestfile = base + "/apps/" + app_dir + "/manifest"
            if os.path.isfile(manifestfile):
                if current_cathegory == "All":
                    app_list.append(app_dir)
                else:
                    manifest = configparser.RawConfigParser()
                    manifest.read(manifestfile)
                    try:
                        if(manifest.get('app', 'cathegory') == current_cathegory):
                            app_list.append(app_dir)
                    except configparser.NoOptionError:
                        pass

        # calculate icons to be displayed on current page
        apps = len(app_list)

        icon_1st = 0
        icon_last = 7       # the first page can hold 8 icons
        if current_page > 0:
            icon_1st += 8   # first page holds 8 icons
            icon_last += 7  # the secong page holds 7 icons
            if current_page > 1:    # all further pages hold 7 icons
                icon_1st += 7*(current_page-1)
                icon_last += 7*(current_page-1)

        # if the current page is the last one then one more icon fits
        # since no "next" arrow is needed
        if apps <= icon_last+2:
            icon_last += 1

        # if this is not the first page then there's a prev button
        if current_page > 0:
            # the prev button is always icon 0 on screen
            # but = self.createSimpleIcon("prev", self.do_prev)
            but = self.createIcon(base + "/prev.png", self.do_prev)
            self.addIcon(grid, but, 0)

        # scan through the list of all applications
        for app_dir in app_list:
            app_path = base + "/apps/" + app_dir + "/"
            manifestfile = app_path + "manifest"
            manifest = configparser.RawConfigParser()
            manifest.read(manifestfile)

            # get various fields from manifest
            appname = manifest.get('app', 'name')
            executable = app_path + manifest.get('app', 'exec')
            iconname = app_path + manifest.get('app', 'icon')
        
            # check if this app is on the current page
            if (iconnr >= icon_1st and iconnr <= icon_last):
                # print("Paint page", page, "iconnr", iconnr)

                # number of this icon in srceen
                icon_on_screen = iconnr - icon_1st
                if current_page > 0: icon_on_screen += 1

                # set properties on element stored in grid to 
                # allow network launch to get the executable name
                # from it
                but = self.createIcon(iconname, self.do_launch, appname, executable)
                self.addIcon(grid, but, icon_on_screen)

            iconnr = iconnr + 1

        # is there another page? Then display the "next" icon
        # print("iconnr after paint", iconnr, "last", icon_last)
        if iconnr > icon_last+1:
            # print("Next PAGE")
            but = self.createIcon(base + "/next.png", self.do_next)
            # the next button is always icon 8 on screen
            self.addIcon(grid, but, 8)
            
        # fill rest of grid with empty widgets
        while iconnr < icon_last+1:
            icon_on_screen = iconnr - icon_1st
            if current_page > 0: icon_on_screen += 1

            # print("Adding space for", icon_on_screen)
            empty = self.createIcon()
            self.addIcon(grid, empty, icon_on_screen)
            iconnr = iconnr + 1

    def set_cathegory(self, cath):
        global current_cathegory
        global current_page
        if current_cathegory != cath:
            current_cathegory = cath
            current_page = 0
            self.addIcons(self.grid)

    def addWidgets(self):
        global current_page

        # receive signals from network server
        self.rescan.connect(self.on_rescan)
        self.launch.connect(self.on_launch)
        self.message.connect(self.on_message)
        self.app_running.connect(self.on_app_running)
        self.get_app.connect(self.on_get_app)
        self.stop_app.connect(self.on_stop_app)

        self.cathegories = self.scan_cathegories()
        self.w = TxtTopWidget(self, self.cathegories)

        self.gridw = QWidget()
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
    FtcGuiApplication(sys.argv)
