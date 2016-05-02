#! /usr/bin/env python3
# -*- coding: utf-8 -*-

# This is the fischertechnik community app launcher

# TODO: 
# - kill text app when window is being closed
# - Close text mode window with button

import configparser
import sys, os, subprocess, threading, math
import socketserver, select, pty

from TxtStyle import *
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from PyQt4.QtNetwork import *

THEME = "default"

CTRL_PORT = 9000
BUSY_TIMEOUT = 20

# make sure all file access happens relative to this script
base = os.path.dirname(os.path.realpath(__file__))

current_category = "All"
current_page = 0

# keep track of running app
app = None
app_executable = ""

# A fullscreen message dialog. Currently only used to show the
# "shutting down" message
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
class CategoryWidget(QComboBox):
    def __init__(self,categories):
        QComboBox.__init__(self)
        self.setObjectName("titlebar")
        self.setCategories(categories)
        
    def setCategories(self, categories):
        prev = self.currentText()
        
        self.clear()
        self.addItem("All")
        sel_idx = 0  # default category = 0 (All)
        for i in range(len(categories)):
            self.addItem(categories[i])
            if categories[i] == prev: sel_idx = i+1

        # if possible reselect the same category as before
        # "All" otherwise
        self.setCurrentIndex(sel_idx)

        # check if category has changed and emit activated signal
        if prev != "" and self.itemText(sel_idx) != prev:
            self.activated[str].emit(self.itemText(sel_idx))
       
# The TXT does not use windows. Instead we just paint custom 
# toplevel windows fullscreen
class TxtTopWidget(QWidget):
    def __init__(self,parent,categories):
        QWidget.__init__(self)
        # the setFixedSize is only needed for testing on a desktop pc
        # the centralwidget name makes sure the themes background 
        # gradient is being used
        self.setFixedSize(240, 320)
        self.setObjectName("centralwidget")

        # create a vertical layout and put all widgets inside
        self.layout = QVBoxLayout()
        self.category_w = CategoryWidget(categories)
        self.category_w.activated[str].connect(parent.set_category)
        self.layout.addWidget(self.category_w)
        self.layout.setContentsMargins(0,0,0,0)

        self.setLayout(self.layout)

    def setCategories(self, categories):
        self.category_w.setCategories(categories)
        
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

class BusyAnimation(QWidget):
    expired = pyqtSignal()

    def __init__(self, app, parent=None):
        super(BusyAnimation, self).__init__(parent)
        self.setWindowFlags(Qt.Popup | Qt.Window)
        self.setStyleSheet("background:transparent;")
        self.setAttribute(Qt.WA_TranslucentBackground)

        self.resize(64, 64)
        pos = parent.mapToGlobal(QPoint(0,0))
        self.move(pos + QPoint(parent.width()/2-32, parent.height()/2-32))

        self.step = 0
        self.app = app

        # create a timer to close this window after 10 seconds at most
        self.etimer = QTimer(self)
        self.etimer.setSingleShot(True)
        self.etimer.timeout.connect(self.timer_expired)
        self.etimer.start(BUSY_TIMEOUT * 1000)

        # animate at 5 frames/sec
        self.atimer = QTimer(self)
        self.atimer.timeout.connect(self.animate)
        self.atimer.start(200)

        # create small circle bitmaps for animation
        self.dark = self.draw(16, QColor("#808080"))
        self.bright = self.draw(16, QColor("#fcce04"))
        
    def draw(self, size, color):
        img = QImage(size, size, QImage.Format_ARGB32)
        img.fill(Qt.transparent)

        painter = QPainter(img)
        painter.setPen(Qt.white)
        painter.setRenderHint(QPainter.Antialiasing, True)
        painter.setBrush(QBrush(color))
        painter.drawEllipse(0, 0, img.width()-1, img.height()-1)
        painter.end()

        return img

    def timer_expired(self):
        # App launch expired without callback ...
        self.expired.emit()
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

        self.step += 45
        self.repaint()

    def close(self):
        self.etimer.stop()
        self.atimer.stop()
        super(BusyAnimation, self).close()
        super(BusyAnimation, self).deleteLater()

    def paintEvent(self, event):

        radius = min(self.width(), self.height())/2 - 16
        painter = QPainter()
        painter.begin(self)

        painter.setRenderHint(QPainter.Antialiasing)

        painter.translate(self.width()/2, self.height()/2)
        painter.rotate(45)
        painter.rotate(self.step)
        painter.drawImage(0,radius, self.bright)
        for i in range(7):
            painter.rotate(45)
            painter.drawImage(0,radius, self.dark)

        painter.end()

class TextmodeDialog(TxtDialog):
    def __init__(self,title,parent):
        TxtDialog.__init__(self, title, parent)
        
        self.txt = QTextEdit()
        self.txt.setReadOnly(True)
        self.setCentralWidget(self.txt)

        self.p = None

    def update(self):
        if self.p:
            # select
            if select.select([self.fd], [], [], 0)[0]:
                output = os.read(self.fd, 100)
                if output: self.append(str(output, "utf-8"))

            if self.p.poll() != None:
                if self.p.returncode != 0:
                    self.txt.setTextColor(Qt.yellow)
                    self.txt.append("[" + str(self.p.returncode) + "]")

                self.p = None
                self.timer.stop()

    def poll(self, p,fd):
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update)
        self.timer.start(10)
        
        self.fd = fd
        self.p = p

    def append(self, str):
        self.txt.moveCursor(QTextCursor.End)
        self.txt.insertPlainText(str)

    def close(self):
        self.timer.stop()
        TxtDialog.close(self)
        
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
        # popup may have expired in the meantime
        if self.popup:
            self.popup.close()

    def launch_textmode_app(self, executable, name):
        global app, app_executable
        dialog = TextmodeDialog(name, self.w)

        app_executable = executable
        master_fd, slave_fd = pty.openpty()
        app = subprocess.Popen(str(executable), stdout=slave_fd, stderr=slave_fd)
        dialog.poll(app, master_fd)
        dialog.exec_()
        os.close(master_fd)
        os.close(slave_fd)

    def launch_app(self, executable, managed, name):
        global app, app_executable

        if self.app_is_running():
            print("Still one app running!")
            return

        # get managed state
        if managed.lower() == "text":
            self.launch_textmode_app(executable, name)
            return
     
        # run the executable
        app_executable = executable
        app = subprocess.Popen(str(executable))

        # display some busy icon
        self.popup = BusyAnimation(app, self.w)
        self.popup.expired.connect(self.on_busyExpired)
        self.popup.show()

    def on_busyExpired(self):
        self.popup = None
        
    def do_launch(self,clicked):
        self.launch_app(str(self.sender().property("executable")),
                        str(self.sender().property("managed")),
                        str(self.sender().property("appname")))

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
        self.categories = self.scan_categories()
        self.w.setCategories(self.categories)
        current_page = 0
        self.addIcons(self.grid)

    @pyqtSlot(QTcpSocket)
    def on_get_app(self, s):
        global app_executable
        if self.app_is_running():
            # only return the <group>/<app>/<exec> part of the path
            app_dir, app_exec_name = os.path.split(app_executable)
            app_group, app_dir_name = os.path.split(app_dir)
            app_group_name = os.path.basename(app_group)
            s.write(os.path.join(app_group_name, app_dir_name, app_exec_name))
        s.write("\n")

    @pyqtSlot()
    def on_stop_app(self):
        global app
        if self.app_is_running():
            app.kill()
            while app.poll() == None:
                pass

    # return a list of directories containing apps
    # searches under /opt/ftc/apps/<group>/<app>
    # the returned list is srted by the name of the apps
    # as stored in the manifest file
    def scan_app_dirs(self):
        app_base = os.path.join(base, "apps")
        # scan for app group dirs first
        app_groups = os.listdir(app_base)
        # then scan for app dirs inside
        app_dirs = []
        for i in app_groups:
            try:
                app_group_dirs = os.listdir(os.path.join(app_base, i))
                for a in app_group_dirs:
                    # build full path of the app dir
                    app_dir = os.path.join(app_base, i, a)
                    # check if there's a manifest inside that dir
                    manifestfile = os.path.join(app_dir, "manifest")
                    if os.path.isfile(manifestfile):
                        # get app name
                        manifest = configparser.RawConfigParser()
                        manifest.read(manifestfile)
                        appname = manifest.get('app', 'name')
                        app_dirs.append((appname, os.path.join(app_base, i, a)))
            except:
                print("Failed: ", i)
                pass
                
        # sort list by apps name
        app_dirs.sort(key=lambda tup: tup[0])

        # return a list of only the directories of the now sorted list
        return ([x[1] for x in app_dirs])

    @pyqtSlot(str)
    def on_launch(self, name):
        # search for an app with that name
        # get list of all subdirectories in the application directory
        app_dirs = self.scan_app_dirs()

        # extract all those that have a manifest file
        for app_dir in app_dirs:
            app_group, app_dir_name = os.path.split(app_dir)
            app_group_name = os.path.basename(app_group)
            app_local_dir = os.path.join(app_group_name, app_dir_name)
            manifestfile = os.path.join(app_dir, "manifest")
            manifest = configparser.RawConfigParser()
            manifest.read(manifestfile)
            if manifest.has_option('app', 'exec'):
                if os.path.join(app_local_dir, manifest.get('app', 'exec')) == name:
                    if manifest.has_option('app', 'managed'):
                        managed = manifest.get('app', 'managed')
                    else:
                        managed = "Yes"

                    self.launch_app(os.path.join(app_dir, manifest.get('app', 'exec')), 
                                    managed, manifest.get('app', 'name'))

    @pyqtSlot(str)
    def on_message(self, str):
        MessageDialog(str).exec_()

    # read the manifet files of all installed apps and scan them
    # for their category. Generate a unique set of categories from this
    def scan_categories(self):
        # get list of all subdirectories in the application directory
        app_dirs = self.scan_app_dirs()

        # extract all those that have a manifest file
        categories = set()
        for app_dir in app_dirs:
            manifestfile = os.path.join(app_dir, "manifest")
            manifest = configparser.RawConfigParser()
            manifest.read(manifestfile)
            if manifest.has_option('app', 'category'):
                categories.add(manifest.get('app', 'category'))
            else:
                print("App has no category:", app_dir)

        return sorted(categories)

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
    def createIcon(self, iconfile=None, on_click=None, appname=None, executable=None, managed="Yes"):
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
            but.setProperty("appname", appname)
            but.setProperty("executable", executable)
            but.setProperty("managed", managed)
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
        vboxw.setProperty("managed", managed)
        
        return vboxw

    # add and icon to the grid. Remove any previous icon
    def addIcon(self, grid, w, index):
        previtem = grid.itemAtPosition(index/3, index%3);
        if previtem: previtem.widget().deleteLater()
        grid.addWidget(w,index/3, index%3)

    # add all icons to the grid
    def addIcons(self, grid):
        global current_page
        global current_category

        iconnr = 0

        # get list of all directories in the application directory
        app_dirs = self.scan_app_dirs()

        # extract all those that have a manifest file an check for
        # current category
        app_list = []
        for app_dir in app_dirs:
            if current_category == "All":
                app_list.append(app_dir)
            else:
                manifestfile = os.path.join(app_dir, "manifest")
                manifest = configparser.RawConfigParser()
                manifest.read(manifestfile)
                try:
                    if(manifest.get('app', 'category') == current_category):
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
            manifestfile = os.path.join(app_dir, "manifest")
            manifest = configparser.RawConfigParser()
            manifest.read(manifestfile)

            # get various fields from manifest
            appname = manifest.get('app', 'name')
            executable = os.path.join(app_dir, manifest.get('app', 'exec'))

            if manifest.has_option('app', 'managed'):
                managed = manifest.get('app', 'managed')
            else:
                managed = "Yes"

            # use icon file if one is mentioned in the manifest
            if manifest.has_option('app', 'icon'):
                iconname = os.path.join(app_dir, manifest.get('app', 'icon'))
            else:
                iconname = os.path.join(base, "icon.png")
        
            # check if this app is on the current page
            if (iconnr >= icon_1st and iconnr <= icon_last):
                # print("Paint page", page, "iconnr", iconnr)

                # number of this icon in srceen
                icon_on_screen = iconnr - icon_1st
                if current_page > 0: icon_on_screen += 1

                # set properties on element stored in grid to 
                # allow network launch to get the executable name
                # from it
                but = self.createIcon(iconname, self.do_launch, appname, executable, managed)
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

    def set_category(self, cat):
        global current_category
        global current_page
        if current_category != cat:
            current_category = cat
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

        self.categories = self.scan_categories()
        self.w = TxtTopWidget(self, self.categories)

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
