#! /usr/bin/env python3
# -*- coding: utf-8 -*-

# launcher.py
# TouchUI launcher application.
# (c) 2016 by Till Harbaum

import configparser, datetime
import sys, os, subprocess, threading
import socketserver, select, time

from TouchStyle import *
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from PyQt4.QtNetwork import *

# PTYs are not available on windows. Running text mode
# apps thus won't work there
if platform.system() != 'Windows':
    import pty

THEME = "default"

CTRL_PORT = 9000
BUSY_TIMEOUT = 20

# make sure all file access happens relative to this script
BASE = os.path.dirname(os.path.realpath(__file__))

# window size used on PC
if 'SCREEN' in os.environ:
    (w, h) = os.environ.get('SCREEN').split('x')
    WIN_WIDTH = int(w)
    WIN_HEIGHT = int(h)
else:
    WIN_WIDTH = 240
    WIN_HEIGHT = 320

# a simple dialog without any decorations (and this without
# the user being able to get rid of it by himself)
class PlainDialog(QDialog):
    def __init__(self):
        QDialog.__init__(self)
        if platform.machine() == "armv7l":
            size = QApplication.desktop().screenGeometry()
            self.setFixedSize(size.width(), size.height())
        else:
            self.setFixedSize(WIN_WIDTH, WIN_HEIGHT)

        self.setObjectName("centralwidget")

    def exec_(self):
        QDialog.showFullScreen(self)
        QDialog.exec_(self)

# A fullscreen message dialog. Currently only used to show the
# "shutting down" message
class MessageDialog(PlainDialog):
    def __init__(self,str):
        PlainDialog.__init__(self)

        self.layout = QVBoxLayout()
        self.layout.addStretch()

        lbl = QLabel(str)
        lbl.setWordWrap(True);
        lbl.setAlignment(Qt.AlignCenter)
        self.layout.addWidget(lbl)

        self.layout.addStretch()
        self.setLayout(self.layout)        

# A fullscreen confirmation dialog. This can be called by an external
# application via the built-in tcp server to e.g. get some user
# feedback.
class ConfirmationDialog(PlainDialog):
    def __init__(self,sock,str):
        self.sock = sock

        strings = str.split("\\n")
        
        PlainDialog.__init__(self)

        self.layout = QVBoxLayout()
        self.layout.addStretch()

        # display the message itself
        for s in strings:
            # a small label 
            if s.startswith("\\s"):
                lbl = QLabel(s[2:])
                lbl.setObjectName("smalllabel")
            elif s.startswith("\\t"):
                lbl = QLabel(s[2:])
                lbl.setObjectName("tinylabel")
            else:
                lbl = QLabel(s)
            
            lbl.setWordWrap(True);
            lbl.setAlignment(Qt.AlignCenter)
            self.layout.addWidget(lbl)
            self.layout.addStretch()

        # display a the "ok" + "cancel" buttons
        button_box = QWidget()
        button_layout = QHBoxLayout()
        button_box.setLayout(button_layout)

        button_layout.addStretch()

        self.ok_but = QPushButton(QCoreApplication.translate("Dialog", "Ok"))
        self.ok_but.clicked.connect(self.on_button_clicked)
        button_layout.addWidget(self.ok_but)

        button_layout.addStretch()

        self.cancel_but = QPushButton(QCoreApplication.translate("Dialog", "Cancel"))
        self.cancel_but.clicked.connect(self.on_button_clicked)
        button_layout.addWidget(self.cancel_but)

        button_layout.addStretch()

        self.layout.addWidget(button_box)
        self.layout.addStretch()
        self.setLayout(self.layout)        

    def on_button_clicked(self):
        # disable buttons so user doesn't click them again
        # before the dialog is close by the timer
        self.ok_but.setDisabled(True)
        self.cancel_but.setDisabled(True)
        
        # send button label back to tcp client
        self.sock.write(self.sender().text() + "\n")

        # close dialog after 1 second
        close_timer = QTimer(self)
        close_timer.setSingleShot(True)
        close_timer.timeout.connect(self.on_close_timer)
        close_timer.start(1000)

        self.sock.close()    # close tcp connection

    def on_close_timer(self):
        self.close()         # close dialog

# The TXTs window title bar
class CategoryWidget(QComboBox):
    def __init__(self,categories, parent = None):
        QComboBox.__init__(self, parent)
        self.setObjectName("titlebar")
        self.setCategories(categories)
        self.setContentsMargins(0,0,0,0)

    def setCategories(self, categories):
        prev = self.currentText()
        
        self.clear()
        self.addItem(QCoreApplication.translate("Category", "All"))
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
            return True
        else:
            return False

# the status bar at the screens top
PLUGINS_DIR = "plugins"

class StatusPopup(QFrame):
    def __init__(self, plugins, bar, parent=None):
        QFrame.__init__(self, parent)
        self.setObjectName("statuspopup")
        self.setVisible(True)
        self.setAutoFillBackground(True)
        self.setWindowFlags(Qt.Popup)

        # open popup centered on top of parent
        self.move(parent.mapToGlobal(QPoint(0,bar.height())))

        self.messages = [ QDate.currentDate().toString() ]

        # get status messages from widgets
        for name in sorted(plugins):
            status = plugins[name].status()
            if status: self.messages.append(plugins[name].name + ": " + status)

        self.setMinimumSize(parent.width(), bar.height())
        self.setMaximumSize(parent.width(), parent.height())

        vbox = QVBoxLayout()
        line = None
        for i in self.messages:
            label = QLabel(i)
            label.setObjectName("statuslabel")
            vbox.addWidget(label)
            if not line:
                line = QFrame()
                line.setFrameShape(QFrame.HLine)
                line.setObjectName("statusframe")
                vbox.addWidget(line)

        self.setLayout(vbox)
        self.adjustSize()

        parent.main_widget.setGraphicsEffect(QGraphicsBlurEffect(parent))

    def closeEvent(self, event):
        self.parent().main_widget.setGraphicsEffect(None)

class StatusBar(QWidget):
    def __init__(self, parent=None):
        QWidget.__init__(self, parent)
        self.setObjectName("statusbar")
        self.setVisible(True)
        self.setAutoFillBackground(True)

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update)
        self.timer.start(2000) # replant timer in ms

        # scan for plugins
        self.plugins = { }
        for file in os.listdir(os.path.join(BASE, PLUGINS_DIR)):
            if file.endswith(".py"):
                fname = os.path.splitext(os.path.basename(file))[0]
                self.plugins[fname] = __import__(PLUGINS_DIR+"."+fname,
                                            globals(), locals(), ['object']) 

    def mousePressEvent(self, event):
        popup = StatusPopup(self.plugins, self, self.parent())
        popup.show()

    # the whole status bar uses custom painting
    def paintEvent(self, event):
        painter = QPainter()
        painter.begin(self)

        # Explictely draw background. Rasp-Pi needs that ...
        painter.fillRect(self.rect(), self.palette().color(self.backgroundRole()))

        # draw the time at the very right
        painter.drawText(QRect(QPoint(0,0), self.size()),
              Qt.AlignRight, QTime.currentTime().toString("h:mm"));

        # draw all plugin icons fromt he left
        x = 0
        for name in sorted(self.plugins):
            plugin = self.plugins[name]
            # request icon from plugin
            icon = QPixmap(plugin.icon())
            if icon:
                painter.drawPixmap(x, 0, icon)
                x += icon.width()

        painter.end()

    def update(self):
        self.repaint()
       
# The TXT/RPi does not use windows. Instead we just paint custom 
# toplevel windows fullscreen
class TouchTopWidget(QWidget):
    def __init__(self,parent,categories):
        QWidget.__init__(self)
        # the setFixedSize is only needed for testing on a desktop pc
        # the centralwidget name makes sure the themes background 
        # gradient is being used
        if platform.machine() == "armv7l":
            size = QApplication.desktop().screenGeometry()
            self.setFixedSize(size.width(), size.height())
        else:
            self.setFixedSize(WIN_WIDTH, WIN_HEIGHT)

        self.setObjectName("centralwidget")

        # create a vertical layout for the statusbar
        self.top_layout = QVBoxLayout()
        self.top_layout.setSpacing(0)
        self.top_layout.setContentsMargins(0,0,0,0)

        self.statusbar = StatusBar(self)
        self.top_layout.addWidget(self.statusbar)

        # create a vertical layout for the main user interface
        self.main_widget = QWidget()
        self.layout = QVBoxLayout()
        self.layout.setSpacing(0)
        self.layout.setContentsMargins(0,0,0,0)

        self.category_w = CategoryWidget(categories, self.main_widget)
        self.category_w.activated[str].connect(parent.set_category)
        self.layout.addWidget(self.category_w)
        self.main_widget.setLayout(self.layout)

        self.top_layout.addWidget(self.main_widget)

        self.setLayout(self.top_layout)

    def setCategories(self, categories):
        return self.category_w.setCategories(categories)
        
    def addWidget(self,w):
        self.layout.addWidget(w)

        # TXT windows are always fullscreen
    def show(self):
        # go fullscreen on arm, stay windowed otherwise
        if platform.machine() == "armv7l":
            QWidget.showFullScreen(self)
        else:
            QWidget.show(self)

class BusyAnimation(QWidget):
    expired = pyqtSignal()

    def __init__(self, app, parent=None):
        super(BusyAnimation, self).__init__(parent)

        self.resize(64, 64)
        
        # center relative to parent
        self.move(QPoint(parent.width()/2-32, parent.height()/2-32))

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
        # We might tell the user that the app ended unexpectedly
        if self.app.poll():
            self.close()
            return

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

class TextmodeDialog(TouchDialog):
    def __init__(self,title,parent):
        TouchDialog.__init__(self, title, parent)
        
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
        TouchDialog.close(self)

        # a toolbutton with drop shadow
class AppButton(QToolButton):
    def __init__(self):
        QToolButton.__init__(self)

        shadow = QGraphicsDropShadowEffect(self)
        shadow.setOffset(QPointF(3,3))
        self.setGraphicsEffect(shadow)

        self.setToolButtonStyle(Qt.ToolButtonTextUnderIcon)
        self.setObjectName("launcher-icon")

        # hide shadow while icon is pressed
    def mousePressEvent(self, event):
        self.graphicsEffect().setEnabled(False)
        QToolButton.mousePressEvent(self,event)

    def mouseReleaseEvent(self, event):
        self.graphicsEffect().setEnabled(True)
        QToolButton.mouseReleaseEvent(self,event)

        # the main icon grid
class IconGrid(QStackedWidget):
    def __init__(self, apps, cat):
        QStackedWidget.__init__(self)

        self.apps = apps
        self.current_apps = self.filterCategory(self.apps, cat)

        # event to know the final size when creating
        # the icon grid
        self.installEventFilter(self)

    def eventFilter(self, obj, event):
        if event.type() == event.Resize:
            # print("resize to", self.width(), self.height())
            # icon grid
            self.columns = int(self.width()/80)
            self.rows = int(self.height()/80)
            self.createPages()
        return False

    def createPages(self):
        # remove all pages that might already be there
        while self.count():
            w = self.widget(self.count()-1)
            self.removeWidget(w)
            w.deleteLater()

        icons_per_page = self.columns * self.rows
        page = None

        # create pages to hold every app
        for app in self.current_apps:
            # create a new page if necessary
            if not page:
                index = 0

                # create grid widget for page
                page = QWidget()
                grid = QGridLayout()
                grid.setSpacing(0)
                grid.setContentsMargins(0,0,0,0)
                page.setLayout(grid)

                # if this isn't the first page, then add a "prev" arrow
                if self.count():
                    but = self.createIcon(os.path.join(BASE, "prev.png"), self.do_prev)
                    grid.addWidget(but, 0, 0, Qt.AlignCenter)
                    index = 1

            # get app details
            app_group, app_dir_name = os.path.split(app['dir'])
            app_group_name = os.path.basename(app_group)
            app_local_dir = os.path.join(app_group_name, app_dir_name)
            executable = os.path.join(app_local_dir, app['exec'])

            if 'managed' in app: managed = app['managed']
            else:                managed = "Yes"

            # use icon file if one is mentioned in the manifest
            if 'icon' in app:    iconname = os.path.join(app['dir'], app['icon'])
            else:                iconname = os.path.join(BASE, "icon.png")

            # create a launch button for this app
            but = self.createIcon(iconname, self.do_launch, app['name'], executable)
            grid.addWidget(but, index/self.columns, index%self.columns, Qt.AlignCenter)

            # check if this is the second last icon on page
            # and if there are at least two more icons to be added. Then we need a
            # "next page" arrow
            if index == icons_per_page - 2:
                if self.current_apps.index(app) < len(self.current_apps)-2:
                    index = icons_per_page - 1
                    but = self.createIcon(os.path.join(BASE, "next.png"), self.do_next)
                    grid.addWidget(but, index/self.columns, index%self.columns, Qt.AlignCenter)

            # advance position counters
            index += 1
            if index == icons_per_page:
                self.addWidget(page)
                page = None
                   
        # fill last page with empty icons
        while index < icons_per_page:
            self.addWidget(page)
            empty = self.createIcon()
            grid.addWidget(empty, index/self.columns, index%self.columns, Qt.AlignCenter)
            index += 1

    # handler of the "next" button
    def do_next(self):
        self.setCurrentIndex(self.currentIndex()+1)

    # handler of the "prev" button
    def do_prev(self):
        self.setCurrentIndex(self.currentIndex()-1)

    # create an icon with label
    def createIcon(self, iconfile=None, on_click=None, appname=None, executable=None):
        button = AppButton()

        button.setText(appname)
        button.setProperty("executable", executable)

        if iconfile:
            pix = QPixmap(iconfile)
            button.setIcon(QIcon(pix))
            button.setIconSize(pix.size())

        if on_click:
            button.clicked.connect(on_click)

        return button

        # filter all apps for the given category
    def filterCategory(self, apps, cat):
        if cat == QCoreApplication.translate("Category", "All"):
            return apps

        # extract all those that have a manifest file an check for
        # current category
        app_list = []
        for app in apps:
            if 'category' in app and app['category'] == cat:
                app_list.append(app)

        return app_list

    def setCategory(self, cat):
        self.current_apps = self.filterCategory(self.apps, cat)
        self.createPages()

    def setApps(self, apps):
        self.apps = apps

    launch = pyqtSignal(str)
    def do_launch(self,clicked):
        self.launch.emit(str(self.sender().property("executable")))

# built-in TCP server so other programs can request a icon list refresh
# or launch an app
class TcpServer(QTcpServer):
    # singnals emitted by network server
    rescan = pyqtSignal()
    launch = pyqtSignal(str)
    message = pyqtSignal(str)
    confirm = pyqtSignal(QTcpSocket,str)
    get_app = pyqtSignal(QTcpSocket)
    stop_app = pyqtSignal()
    app_running = pyqtSignal(int)
    enable_logging = pyqtSignal(bool)

    def __init__(self):
        QTcpServer.__init__(self)

        self.listen(QHostAddress("0.0.0.0"), CTRL_PORT)
        self.newConnection.connect(self.addConnection)
        self.connections = []
        

    def addConnection(self):
        clientConnection = self.nextPendingConnection()
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
                    elif cmd == "confirm":
                        self.confirm.emit(s,parm)
                    elif cmd == "quit":
                        s.write("Bye\n")
                        s.close()
                    elif cmd == "get-app":
                        self.get_app.emit(s)
                    elif cmd == "stop-app" or cmd == "stop":
                        self.stop_app.emit()
                    elif cmd == "app-running":
                        self.app_running.emit(int(parm))
                    elif cmd == "logging-start":
                        self.enable_logging.emit(True)
                    elif cmd == "logging-stop":
                        self.enable_logging.emit(False)
                    else:
                        s.write("Unknown command\n")
                        print("Unknown command ", cmd)

    def removeConnection(self):
        pass

    def socketError(self):
        pass
        

class FtcGuiApplication(TouchApplication):
    def __init__(self, args):
        TouchApplication.__init__(self, args)

        # enable i18n
        translator = QTranslator()
        path = os.path.dirname(os.path.realpath(__file__))
        translator.load(QLocale.system(), os.path.join(path, "launcher_"))
        self.installTranslator(translator)

        # populate category map now that the i18n is in place. Everything not
        # covered will only show up in the "all" category
        self.category_map = {
            "system":   QCoreApplication.translate("Category", "System"),
            "settings": QCoreApplication.translate("Category", "System"), # deprecated settings category
            "models":   QCoreApplication.translate("Category", "Models"),
            "model":    QCoreApplication.translate("Category", "Models"),
            "tools":    QCoreApplication.translate("Category", "Tools"),
            "tool":     QCoreApplication.translate("Category", "Tools"),
            "demos":    QCoreApplication.translate("Category", "Demos"),
            "demo":     QCoreApplication.translate("Category", "Demos"),
            "tests":    QCoreApplication.translate("Category", "Demos"),   # deprecated "tests" category
            "test":     QCoreApplication.translate("Category", "Demos")    # deprecated "test" category
        };

        # load stylesheet from the same place the script was loaded from
        self.setStyleSheet( "file:///" + BASE + "/themes/" + THEME + "/style.qss")

        self.app_process = None

        # create TCP server so other programs can request a icon list refresh
        # or launch an app
        self.tcpServer = TcpServer()

        # receive signals from network server
        self.tcpServer.rescan.connect(self.on_rescan)
        self.tcpServer.launch.connect(self.on_launch)
        self.tcpServer.message.connect(self.on_message)
        self.tcpServer.confirm.connect(self.on_confirm)
        self.tcpServer.app_running.connect(self.on_app_running)
        self.tcpServer.enable_logging.connect(self.on_enable_logging)
        self.tcpServer.get_app.connect(self.on_get_app)
        self.tcpServer.stop_app.connect(self.on_stop_app)

        self.log_file = None

        self.addWidgets()
        self.exec_()        

    def app_is_running(self):
        if self.app_process == None:
            return False

        return self.app_process.poll() == None

    # this signal is received when an app reports it
    # has been launched
    @pyqtSlot(int)
    def on_app_running(self, pid):
        # popup may have expired in the meantime
        if self.popup:
            self.popup.close()

    # this signal is received when app logging is to be 
    # enabled
    @pyqtSlot(bool)
    def on_enable_logging(self, on):
        if self.log_file:
            self.log_file.write("Logging stopped at: " + datetime.datetime.now().isoformat() + "\n")
            self.log_file.close()
            self.log_file = None

        if on:
            self.log_file = open("/tmp/app.log", 'w')
            self.log_file.write("Logging started at: " + datetime.datetime.now().isoformat() + "\n")
            self.log_file.flush()

    def launch_textmode_app(self, executable, name):
        dialog = TextmodeDialog(name, self.w)

        self.app_executable = executable
        master_fd, slave_fd = pty.openpty()
        self.app_process = subprocess.Popen(str(executable), stdout=slave_fd, stderr=slave_fd)
        dialog.poll(self.app_process, master_fd)
        dialog.exec_()
        os.close(master_fd)
        os.close(slave_fd)

    def launch_app(self, executable, managed, name):
        if self.app_is_running():
            return

        # get managed state
        if managed.lower() == "text":
            self.launch_textmode_app(executable, name)
            return
     
        # run the executable
        self.app_executable = executable

        # assume that we can just launch enything under non-windows
        if platform.system() != 'Windows':
            if self.log_file:
                self.log_file.write("Application: " + executable + "\n")
                self.log_file.write("Application started at: " + datetime.datetime.now().isoformat() + "\n")
                self.log_file.flush()
                self.log_master_fd, self.log_slave_fd = pty.openpty()
                self.app_process = subprocess.Popen(str(executable), stdout=self.log_slave_fd, stderr=self.log_slave_fd)

                # start a timer to monitor the ptys
                self.log_timer = QTimer()
                self.log_timer.timeout.connect(self.on_log_timer)
                self.log_timer.start(100)
            else:
                self.app_process = subprocess.Popen(str(executable))
        else:
            # under windows assume it's a python script that is
            # to be launched and run that with pythonw (without console)
            os.environ['PYTHONPATH'] = BASE
            self.app_process = subprocess.Popen( ("pythonw", str(executable)) )

        # display some busy icon
        self.popup = BusyAnimation(self.app_process, self.w)
        self.popup.expired.connect(self.on_busyExpired)
        self.popup.show()

    def on_log_timer(self):
        # check if process is still alive
        if self.app_is_running():
            if select.select([self.log_master_fd], [], [], 0)[0]:
                output = os.read(self.log_master_fd, 100)
                if output: 
                    self.log_file.write(str(output, "utf-8"))
                    self.log_file.flush()
        else:
            # write good-byte to log
            self.log_file.write("Application ended with return value " + str(self.app_process.returncode) + "\n")
            self.log_file.flush()

            # close any open ptys
            os.close(self.log_master_fd)
            os.close(self.log_slave_fd)

            # remove timer
            self.log_timer = None

    def on_busyExpired(self):
        self.popup = None
 
    @pyqtSlot()
    def on_rescan(self):
        # rescan all apps
        self.apps = self.scan_app_dirs()

        # inform icon grid about new apps list. This will not
        # redraw anything as this will happen when the categories
        # are updated
        self.icons.setApps(self.apps)

        # extract categories
        categories = self.get_categories(self.apps)
        if categories != self.categories:
            self.categories = categories

            # set new categories
            if not self.w.setCategories(self.categories):
                # cathegory hasn't changed. So we need to redraw the icon 
                # since the apps listed in the current category may have changed
                # a refresh can be forced by setting the current category again
                self.icons.setCategory(self.current_category)
        else:
            # the same when the list of categories hasn't changed at all
            self.icons.setCategory(self.current_category)

    @pyqtSlot(QTcpSocket)
    def on_get_app(self, s):
        if self.app_is_running():
            # only return the <group>/<app>/<exec> part of the path
            app_dir, app_exec_name = os.path.split(self.app_executable)
            app_group, app_dir_name = os.path.split(app_dir)
            app_group_name = os.path.basename(app_group)
            s.write(os.path.join(app_group_name, app_dir_name, app_exec_name))
        s.write("\n")

    @pyqtSlot()
    def on_stop_app(self):
        if self.app_is_running():
            self.app_process.kill()
            while self.app_process.poll() == None:
                pass

            # give app a second to terminate
            # fix for https://github.com/ftCommunity/ftcommunity-TXT/issues/50
            time.sleep(1)

    # read a number of entries from the manifest and return them 
    # as a dictionary
    def manifest_import(self, manifest):
        entries = ( "managed", "exec", "name", "icon" );
        appinfo = { }
        for i in entries:
            if manifest.has_option('app', i):
                appinfo[i] = manifest.get('app', i)

        # overwrite with locale specific values
        loc = QLocale.system().name().split('_')[0].strip().lower()
        for i in entries:
            if manifest.has_option(loc, i):
                appinfo[i] = manifest.get(loc, i)

        # the category needs special treatment as it maps 
        # onto a limited set of pre-defined categories
        if manifest.has_option('app', "category"):
            c = manifest.get('app', "category").lower()
            if c in self.category_map:
                appinfo['category'] = self.category_map[c];

        return appinfo

    # return a list of directories containing apps
    # searches under /opt/ftc/apps/<group>/<app>
    # the returned list is srted by the name of the apps
    # as stored in the manifest file
    def scan_app_dirs(self):
        app_base = os.path.join(BASE, "apps")
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
                        manifest.read_file(open(manifestfile, "r", encoding="utf8"))
                        appname = manifest.get('app', 'name')

                        appinfo = self.manifest_import(manifest) 
                        appinfo["dir"] = os.path.join(app_base, i, a)

                        app_dirs.append((appname, appinfo))
            except:
                pass
                
        # sort list by apps name
        app_dirs.sort(key=lambda tup: tup[0])

        # return a list of only the appinfo of the now sorted list
        return ([x[1] for x in app_dirs])

    @pyqtSlot(str)
    def on_launch(self, name):
        # the given name is of the form group/app/executable
        # self.apps contains all dirs of apps like /opt/ftc/apps/group/app
        # we need to match this
        app_dir = os.path.dirname(os.path.join(BASE, "apps", name))
        app = next((app for app in self.apps if app["dir"] == app_dir), None)

        if app and 'exec' in app:
            if 'managed' in app: managed = app['managed']
            else:                managed = "Yes"
                
            self.launch_app(os.path.join(app_dir, app['exec']), managed, app['name'])

    def on_message(self, str):
        MessageDialog(str).exec_()

    def on_confirm(self,sock,str):
        ConfirmationDialog(sock,str).exec_()

    # read the manifet files of all installed apps and scan them
    # for their category. Generate a unique set of categories from this
    def get_categories(self, apps):
        categories = set()
        for i in apps:
            if "category" in i:
                categories.add(i["category"])

        return sorted(categories)

    def set_category(self, cat):
        if self.current_category != cat:
            self.current_category = cat
            self.icons.setCategory(cat)

    def addWidgets(self):
        # scan for available apps
        self.apps = self.scan_app_dirs()

        # extract category information
        self.current_category = QCoreApplication.translate("Category", "All")
        self.categories = self.get_categories(self.apps)
        self.w = TouchTopWidget(self, self.categories)

        # create icon grid
        self.icons = IconGrid(self.apps, self.current_category)
        self.icons.launch.connect(self.on_launch)

        self.w.addWidget(self.icons);
        self.w.show() 
 
# Only actually do something if this script is run standalone, so we can test our 
# application, but we're also able to import this program without actually running
# any code.
if __name__ == "__main__":
    FtcGuiApplication(sys.argv)
