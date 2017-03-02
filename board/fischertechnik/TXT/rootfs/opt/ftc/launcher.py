#! /usr/bin/env python3
# -*- coding: utf-8 -*-

# launcher.py
# TouchUI launcher application.
# (c) 2016-2017 by Till Harbaum

import configparser, datetime
import sys, os, subprocess, threading
import socketserver, select, time, locale
import xml.etree.ElementTree as ET

from TouchStyle import *
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from PyQt4.QtNetwork import *

PLUGINS_DIR = "plugins"

# PTYs are not available on windows.
if platform.system() != 'Windows':
    import pty

THEME = "default"

# the following is meant to suppress unwanted clicks when scrolling
if TXT:
    MIN_CLICK_TIME = 0.1    # a click needs to be 100ms at least ...
else:
    MIN_CLICK_TIME = 0

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

class StatusPopup(QFrame):
    # the status bar at the screens top
    def __init__(self, plugins, bar, parent=None):
        QFrame.__init__(self, parent)
        self.setObjectName("statuspopup")
        self.setVisible(True)
        self.setAutoFillBackground(True)
        self.setWindowFlags(Qt.Popup)

        # open popup centered on top of parent
        self.move(parent.mapToGlobal(QPoint(0,bar.height())))

        self.messages = [ QLocale().toString(QDate.currentDate()) ]

        # get status messages from widgets
        for name in sorted(plugins):
            status = plugins[name].status()
            if status: self.messages.append(plugins[name].name() + ": " + status)

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
              Qt.AlignRight, QLocale().toString(QTime.currentTime(), QLocale.ShortFormat))

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
    power_button_pressed = pyqtSignal()

    def __init__(self,parent=None):
        QWidget.__init__(self, parent)
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

        self.main_widget.setLayout(self.layout)

        self.top_layout.addWidget(self.main_widget)

        self.setLayout(self.top_layout)

        # on arm (TXT) start thread to monitor power button
        if INPUT_EVENT_DEVICE:
            self.buttonThread = ButtonThread()
            self.connect( self.buttonThread, SIGNAL("power_button_released()"), self.on_power_button )
            self.buttonThread.start()

    def on_power_button(self):
        # only react if no app is currently running
        if self.main_widget.isActiveWindow():
            # try to get up one folder level
            self.power_button_pressed.emit()

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

class Icon(QPixmap):
    def __init__(self, name, parent=None):
        QPixmap.__init__(self, os.path.join(BASE, "media", name), parent)

    # let the user enter the name of a new folder
class FolderName(TouchKeyboard):
    def __init__(self, parent=None):
        TouchKeyboard.__init__(self, parent)

class FolderOpIcon(QToolButton):
    def __init__(self, type, parent=None):
        QToolButton.__init__(self, parent)

        shadow = QGraphicsDropShadowEffect(self)
        shadow.setOffset(QPointF(3,3))
        self.setGraphicsEffect(shadow)
        
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.setToolButtonStyle(Qt.ToolButtonIconOnly)
        pix = Icon(type + ".png")
        icon = QIcon(pix)
        self.setIcon(icon)
        self.setIconSize(pix.size())

# ========================== the central list of objects ===========================

class BaseItem(dict):
    def __init__(self, name):
        dict.__init__(self)
        self["name"] = name

class AppItem(dict):
    def __init__(self, name):
        BaseItem.__init__(self, name)

    def local_path(self):
        app_group, app_dir_name = os.path.split(self['dir'])
        return os.path.join(os.path.basename(app_group), app_dir_name)

class FolderItem(BaseItem):
    def __init__(self, name):
        BaseItem.__init__(self, name)
        self["apps"] = AppList(self)  # start with an empty app list
        self["icon"] = Icon("icon_folder.png")

    def updateIcon(self):
        self["apps"].sort()

        # start with a fresh icon
        self["icon"] = QPixmap(os.path.join(BASE, "media", "icon_folder.png"))

        # and create a folder icon of the first content icon
        painter = QPainter(self["icon"])
        painter.setRenderHint(QPainter.Antialiasing, True)
        painter.setRenderHint(QPainter.SmoothPixmapTransform, True)

        # positions and size of sub icons
        folder_grid = { 'x':3, 'y': 2 }
        offset = { 'x':1, 'y':16 }
        border = 2
        spacing = 2
        iw = int((64 - 2*border - (folder_grid['x']-1)*spacing)/folder_grid['x'])
        ih = int((64 - 2*border - (folder_grid['y']-1)*spacing)/folder_grid['y'])
        if ih > iw: ih = iw
        if ih < iw: iw = ih       

        sub_icons = 0
        for app in self["apps"]:
            # ignore all folders
            if "exec" in app and sub_icons < (folder_grid['x'] * folder_grid['y']):
                pos_x = offset['x'] + border + (iw+spacing) * int(sub_icons % folder_grid['x'])
                pos_y = offset['y'] + border + (ih+spacing) * int(sub_icons / folder_grid['x'])

                # add small versions of the app icon onto this
                painter.drawPixmap(QRect(pos_x,pos_y,iw,ih), app["icon"])
                sub_icons += 1
 
class FolderUpItem(FolderItem):
    def __init__(self, name, apps):
        FolderItem.__init__(self, name)
        self["up_folder"] = True   # to ignore this when searching through the app tree
        self["apps"] = apps
        self["icon"] = Icon("icon_folder_up.png")

class AppList(list):
    ''' an app list contains a list of icons an folders
    and methods to work on them '''
    def __init__(self, parent_folder = None):
        list.__init__(self)
        self.parent_folder = parent_folder

    def dump(self):
        for a in self:
            if "exec" in a:        print(" " + a["name"])
            elif "up_folder" in a: print("<" + a["name"])
            else:                  print("+" + a["name"])

    def sort(self):
        ''' sort the current list '''
        # return a sorted list
        # This is actually rather tricky. Locale is being set after locading
        # the locale file
        list.sort(self, key=self.key_name_sort)

    def key_name_sort(self, value):
        # folders are always "in front" of apps and the "up" folder is
        # always first
        if "exec" in value:             c = "E"
        elif not "up_folder" in value:  c = "D"
        else:                           c = "C"
        return c + locale.strxfrm(value["name"])

    def append(self, item):
        # if it's a subfolder that's being appended, then add an appropriate
        # "up" entry to it and create the appropriate icon
        if isinstance(item, FolderItem):
            up_folder = FolderUpItem(item["name"], self)
            if "category" in item:
                up_folder["category"] = item["category"]

            item["apps"].insert(0, up_folder)
            # give FolderItem a reference to this list to allow is to move
            # up the hierarchy
            item["parent"] = self
            item.updateIcon()

        list.append(self, item)

    def getRoot(self):
        # check if there's a "up_folder" in this list
        # and return the root of that
        if "up_folder" in self[0]:
            return self[0]["apps"].getRoot()

        # otherwise this is the root
        return self

    def getPath(self):
        # assemble current path
        if "up_folder" in self[0]:
            if "category" in self[0]:
                name = "~" + self[0]["category"]
            else:
                # escape reserved characters
                name = self[0]["name"]
                name = name.replace("&", "&amp;")
                name = name.replace("~", "&tilda;")
                name = name.replace("/", "&slash;")

            path = self[0]["apps"].getPath() + "/" + name
        else:
            path = ""

        return path

    def filename(self):
        return os.path.join(os.path.expanduser("~"), ".launcher.xml")
    
        # export this whole list into an xml file
    def export(self):
        root = ET.Element("launcher")
        self.export_list(ET.SubElement(root, "apps"), True, self)
        ET.ElementTree(root).write(self.filename())    

    def export_list(self, parent, is_root, apps):
        for a in apps:
            if "exec" in a:
                # ignore apps on root level. This where they end up, anyway
                if not is_root:
                    ET.SubElement(parent, "app", path=a.local_path())
            elif not "up_folder" in a:
                folder = ET.SubElement(parent, "folder", name=a["name"])
                if "category" in a:
                    folder.set("category", a["category"])
                self.export_list(folder, False, a["apps"])

    def parse_tree(self, apps, elem, category_map):
        for child in elem:
            if child.tag == "folder" and "name" in child.attrib:
                # Translate folder names if they match a category
                folder = FolderItem(child.attrib["name"])
                if "category" in child.attrib:
                    if child.attrib["category"] in category_map:
                        folder["name"] = category_map[child.attrib["category"]]
                        folder["category"] = child.attrib["category"]
                
                apps.append(folder)
                self.parse_tree(folder["apps"], child, category_map)
                folder.updateIcon()
            if child.tag == "app" and "path" in child.attrib:
                # try to find app in self
                for c in self:
                    if "exec" in c and c.local_path() == child.attrib["path"]:
                        apps.append(c)  # add app to folders app list
                        self.remove(c)  # remove app from root app list
                
    def apply_tree(self, category_map):
        # try to load file, just bail out if anything goes wrong
        try:
            tree = ET.parse(self.filename())
        except:
            return False
            
        root = tree.getroot()
        if root.tag == "launcher":
            for child in root:
                if child.tag == "apps":
                    self.parse_tree(self, child, category_map)
        
        return True

    def getFolderList(self, folders):
        if len(folders) == 0:
            return self

        for a in self:
            if not "exec" in a:
                if folders[0].startswith("~"):
                    # search by category if that was given
                    if "category" in a:
                        if a["category"] == folders[0][1:]:
                            return a["apps"].getFolderList(folders[1:])
                else:
                    folder = folders[0]
                    folder = folder.replace("&slash;", "/")
                    folder = folder.replace("&tilda;", "~")
                    folder = folder.replace("&amp;", "&")

                    # otherwise search by name
                    if a["name"] == folder:
                        return a["apps"].getFolderList(folders[1:])
            
    # folder selection dialog
class FolderList(TouchDialog):
    selected = pyqtSignal(object)

    class FolderListWidget(QListWidget):
        selected = pyqtSignal(object)

        def __init__(self, apps, parent=None):
            QListWidget.__init__(self, parent)
            self.setUniformItemSizes(True)
            self.setViewMode(QListView.ListMode)
            self.setMovement(QListView.Static)
            self.setIconSize(QSize(32,32))

            # add all folders
            for a in apps:
                if not "exec" in a and not "up_folder" in a:
                    item = QListWidgetItem(QIcon(a["icon"]), a["name"])
                    item.setData(Qt.UserRole, a)
                    self.addItem(item)

            # react on clicks
            self.itemClicked.connect(self.onItemClicked)

        def onItemClicked(self, item):
            self.selected.emit(item.data(Qt.UserRole))            

    def __init__(self, apps, parent = None):
        super(FolderList, self).__init__(QCoreApplication.translate("Folder", "Select"), parent)
        self.list = self.FolderListWidget(apps, self)
        self.list.selected.connect(self.on_selected)
        self.setCentralWidget(self.list)

    def on_selected(self, folder):
        self.close()
        self.selected.emit(folder)

class AppPopup(QFrame):
    refresh = pyqtSignal()
    go_to_folder = pyqtSignal(object)

    HEIGHT = 124
    
    def __init__(self, parent=None):
        super(AppPopup, self).__init__(parent)
        self.setWindowFlags(Qt.Popup)
        self.setObjectName("popup")
        # remove bottom/right/left borders
        self.setStyleSheet("QFrame { border-bottom: 0; border-left: 0; border-right: 0; }");

        # find root window
        while parent and not parent.inherits("TouchTopWidget"):
            parent = parent.parent()

        # set size
        self.resize(parent.width(), self.HEIGHT)

        #
        vbox = QVBoxLayout(self)
        vbox.setContentsMargins(0,0,0,0)
        vbox.setSpacing(0)

        title = QLabel(self.parent().app["name"], self)
        title.setObjectName("titlebar")
        title.setAlignment(Qt.AlignCenter)
        title.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Fixed)
        vbox.addWidget(title)

        self.setLayout(vbox)

        # get access to the icongrid
        icongrid = self.parent().parent()

        # add three icons
        hbox_w = QWidget(self)
        hbox = QHBoxLayout()
        has_up_folder = False
        sub_folders = 0
        for a in icongrid.apps:
            if "up_folder" in a:
                has_up_folder = True
            elif not "dir" in a:
                sub_folders += 1

        # remove only works if the current folder is not the top folder ...
        if has_up_folder:
            if len(icongrid.apps) > 2:
                # ... and if there will be at least one app icon (plust the dir-up) left
                remove = FolderOpIcon("icon_remove_from_folder", self)
                remove.clicked.connect(self.on_remove)
                hbox.addWidget(remove)
            else:
                # otherwise remove the entire folder 
                remove_and_delete = FolderOpIcon("icon_remove_from_folder_and_delete_folder", self)
                remove_and_delete.clicked.connect(self.on_remove_and_delete)
                hbox.addWidget(remove_and_delete)

        # can only move into existing folder if there is at least one
        if sub_folders > 0:
            move = FolderOpIcon("icon_move_into_folder", self)
            move.clicked.connect(self.on_move)
            hbox.addWidget(move)

        move_new = FolderOpIcon("icon_move_into_new_folder", self)
        move_new.clicked.connect(self.on_move_new)
        hbox.addWidget(move_new)
        hbox_w.setLayout(hbox)
        vbox.addWidget(hbox_w)
        
        vbox.addStretch()
        self.setLayout(vbox)

        # open popup at the roots bottom
        pos = parent.mapToGlobal(QPoint(0,parent.height()-self.height()))
        self.move(pos)

    def app_move_one_folder_up(self):
        # parent is the appicon, parent.parent is the icongrid
        appicon = self.parent()
        icongrid = self.parent().parent()

        # remove from current app list
        if not icongrid.apps.parent_folder or not "parent" in icongrid.apps.parent_folder:
            return False
            
        # get the parent list
        # (it's the parent list referenced in the parent folder)
        parent_list = icongrid.apps.parent_folder["parent"]
        parent_list.append(appicon.app)

        # update grandparents folder icon if it exists
        if icongrid.apps.parent_folder["parent"].parent_folder:
            icongrid.apps.parent_folder["parent"].parent_folder.updateIcon()
            
        # and remove it from current list
        icongrid.apps.remove(appicon.app)

        # update parent icon
        icongrid.apps.parent_folder.updateIcon()

        return True
            
    def on_remove(self):
        self.close()

        self.app_move_one_folder_up()
        self.refresh.emit()

    def on_remove_and_delete(self):
        self.close()

        if self.app_move_one_folder_up():
            appicon = self.parent()
            icongrid = self.parent().parent()

            if icongrid.apps.parent_folder and "parent" in icongrid.apps.parent_folder:
                # remove the now empty folder
                parent_apps = icongrid.apps.parent_folder["parent"]
                parent_apps.remove(icongrid.apps.parent_folder)
                # go up one folder
                self.go_to_folder.emit(parent_apps)

            self.refresh.emit()        
        
    def on_move(self):
        self.close()

        icongrid = self.parent().parent()
        folder_list = FolderList(icongrid.apps, self)
        folder_list.selected.connect(self.on_move_to_folder)
        folder_list.show()
        folder_list.exec_()

    def move_to_folder(self, folder):
        # parent is the appicon, parent.parent is the icongrid
        appicon = self.parent()
        icongrid = self.parent().parent()

        # add app to new folder
        folder["apps"].append(appicon.app)

        # remove app from current folder
        icongrid.apps.remove(appicon.app)

        # generate icon for new folder
        folder.updateIcon()

        # and finally sort current list so the new icon
        # shows up in the right place
        icongrid.apps.sort()

        # the parent folder icon also may have to be redone
        if icongrid.apps.parent_folder:
            icongrid.apps.parent_folder.updateIcon()

    def on_move_to_folder(self, folder):
        self.move_to_folder(folder)
        self.refresh.emit()
        
    def on_move_new(self):
        self.close()

        # request name of new folder from user
        folder_name = FolderName(self)
        folder_name.titlebar.setText(QCoreApplication.translate("Folder", "New"))
        folder_name.text_changed.connect(self.on_new_folder)
        folder_name.show()
        folder_name.exec_()

    def on_new_folder(self, name):
        icongrid = self.parent().parent()

        # create a new folder in the current list
        folder = FolderItem(name)
        # and append it to the parent dir
        icongrid.apps.append(folder)

        self.move_to_folder(folder)

        # request refresh of current view since there's
        # now a new folder
        self.refresh.emit()

        # a toolbutton with drop shadow
class AppIcon(QToolButton):
    refresh = pyqtSignal()
    go_to_folder = pyqtSignal(object)

    def __init__(self, app, parent=None):
        QToolButton.__init__(self, parent)
        self.app = app

        self.setText(app["name"].replace("&", "&&"))

        self.setIcon(QIcon(app["icon"]))
        self.setIconSize(app["icon"].size())
        self.installEventFilter(self)

        # check if there's a VerticalScrollArea
        # in the family tree ...
        while parent and not parent.inherits("VerticalScrollArea"):
            parent = parent.parent()

        # ... and register its event filter to let it pre-filter
        # mouse events
        if parent:
            self.installEventFilter(parent)
            
        shadow = QGraphicsDropShadowEffect(self)
        shadow.setOffset(QPointF(3,3))
        self.setGraphicsEffect(shadow)

        self.setToolButtonStyle(Qt.ToolButtonTextUnderIcon)
        self.setObjectName("launcher-icon")

    def eventFilter(self, obj, event):
        if event.type() == 2000:
            # current this only doesn't do anything for folders
            if "dir" in self.app:
                # get all the app details from the IconGrid
                popup = AppPopup(self)
                popup.refresh.connect(self.on_refresh)
                popup.go_to_folder.connect(self.on_go_to_folder)
                popup.show()
            
        return False

    def on_refresh(self):
        self.refresh.emit()

    def on_go_to_folder(self, apps):
        self.go_to_folder.emit(apps)

        # hide shadow while icon is pressed
    def mousePressEvent(self, event):
        self.graphicsEffect().setEnabled(False)
        QToolButton.mousePressEvent(self,event)

    def mouseReleaseEvent(self, event):
        self.graphicsEffect().setEnabled(True)
        QToolButton.mouseReleaseEvent(self,event)
        
        # the main icon grid
class IconGrid(QWidget):
    launch = pyqtSignal(str)
    open_folder = pyqtSignal(list)

    def __init__(self, apps):
        QWidget.__init__(self)

        self.apps = apps
        self.setSizePolicy(QSizePolicy.Maximum, QSizePolicy.Maximum)

        self.grid = QGridLayout()
        self.grid.setSpacing(0)
        self.grid.setContentsMargins(0,10,0,10)
        self.setLayout(self.grid)

        # event to know the final size when creating
        # the icon grid
        self.installEventFilter(self)
        self.columns = 0
        self.button_app = None

    def eventFilter(self, obj, event):
        if event.type() == event.Resize:
            if self.width() != 0 and int(self.width()/80) != self.columns:
                # scale icon grid to use the full width
                self.columns = int(self.width()/80)
                self.createAppIcons()

                # make sure all columns are the same width
                w = int(self.width()/self.columns)
                for i in range(self.columns):
                    self.grid.setColumnMinimumWidth(i, w)

        return False

    def setButtonApp(self, app):
        self.button_app = app

    def getPath(self):
        # remove any trailing "/"
        return self.apps.getPath().lstrip("/")

    def setPath(self, path):
        # empty path given? Return root
        if path == "": return self.apps.getRoot()
        # otherwise try to set path
        self.setApps(self.apps.getRoot().getFolderList(path.split("/")))

    def createAppIcons(self):
        # remove all existing widgets from grid
        w = self.grid.takeAt(0)
        while w:
            w.widget().deleteLater()
            w = self.grid.takeAt(0)

        # create pages to hold every app
        index = 0
        for app in self.apps:
            # create a launch button for this app
            but = AppIcon(app, self)
            but.refresh.connect(self.on_refresh)
            but.go_to_folder.connect(self.on_go_to_folder)
            
            if "exec" in app:
                but.clicked.connect(self.do_launch)
            else:
                but.clicked.connect(self.do_open_folder)
                
            self.grid.addWidget(but, index/self.columns, index%self.columns, Qt.AlignCenter)
            index += 1

    def on_refresh(self):
        # the item tree has changed 

        # write updated tree to disk
        self.apps.getRoot().export()

        # refresh the view
        self.createAppIcons()

    def on_go_to_folder(self, apps):
        self.setApps(apps)

    def on_power_button(self):
        # check if we are in a sub folder
        if "up_folder" in self.apps[0]:
            self.setApps(self.apps[0]["apps"])
        elif self.button_app:
            print("Launch", self.button_app)
            self.launch.emit(self.button_app)

    def setApps(self, apps):
        if not apps: return

        self.apps = apps
        if self.columns > 0:
            self.createAppIcons()

    def do_launch(self,clicked):
        # get the executable name relative to the app dir
        if not "dir" in self.sender().app: return
        executable = os.path.join(self.sender().app.local_path(), self.sender().app['exec'])
        self.launch.emit(executable)

    def do_open_folder(self,clicked):
        name = self.sender().app["name"]
        for app in self.apps:
            # ignore apps
            if not "exec" in app and app["name"] == name:
                self.open_folder.emit(app["apps"])

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

class LauncherPlugin:
    def __init__(self, launcher):
        self.launcher = launcher
        self.translators = []
        self.mainWindow = None

    def exit(self):
        if self.mainWindow:
            self.mainWindow.close()
        for translator in self.translators:
            self.launcher.removeTranslator(translator)

    def installTranslator(self, translator):
        self.launcher.installTranslator(translator)
        self.translators.append(translator)

    def isClosed(self):
        return not (self.mainWindow and self.mainWindow.isVisible())
    def locale(self):
        try: return self.launcher.locale
        except: return QLocale.system()

# Adapter for running lightweight apps as launcher plugins. 
# Implements parts of the subprocess.Popen API (poll(), kill(), returncode)
# in order to keep changes to FtcGuiApplication as minimal as possible
class LauncherPluginAdapter:
    def __init__(self, launcher, module_script):
        self.returncode = None
        self.plugin = None
        import importlib, re
        module_name = re.search(BASE + "/(.+).py", module_script).group(1).replace("/", ".")
        module = importlib.reload(importlib.import_module(module_name))
        try:
            self.plugin = module.createPlugin(launcher)
        except:
            self.returncode = -1

    def poll(self):
        # Clean up if the plugin is finished but no return code has been set yet
        if self.returncode is None and self.plugin and self.plugin.isClosed():
            self.kill()
        return self.returncode

    def kill(self):
        if self.plugin:
            self.plugin.exit()
            self.plugin = None
            self.returncode = 0

class VerticalScrollArea(QScrollArea):
    TIMER_HZ = 25

    def __init__(self, content, parent=None):
        QScrollArea.__init__(self, parent)

        self.setWidgetResizable(True)
        self.setFrameStyle(QFrame.NoFrame)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setWidget(content)

        self.press_event = None
        self.dragging = None
        self.delayed_press = False
        self.drag_speed = None
        self.timer = None
        self.release_lock = None

    def eventFilter(self, obj, event):
        # first make sure the child widget uses the full possible width
        if event.type() == event.Resize:
            self.widget().setMinimumWidth(self.width())

        # just eat double clicks ...
        if event.type() == event.MouseButtonDblClick:
            return True

        # we also need to catch mouse events
        if event.type() == event.MouseButtonPress and event.button() == Qt.LeftButton:
            # a delayed event is just passed through
            if self.delayed_press:
                return False

            # any regular press within the release lock time is totally ignored
            if self.release_lock:
                return True
            
            self.drag_speed = None

            # stop any existing drag timer
            if self.timer:
                self.timer.stop()
                self.timer = None

            # start a timer used to check for long presses
            self.press_timer = QTimer(self)
            self.press_timer.timeout.connect(self.on_press_timer)
            self.press_timer.setSingleShot(True)
            self.press_timer.start(1000)

            # remember this event to be able to replay it later
            self.press_event = { "time": time.time(), "obj": obj, "event": QMouseEvent( event) }
            self.dragging = None

            # don't pass this event to the target now
            return True

        if(event.type() == event.MouseButtonRelease and 
           event.button() == Qt.LeftButton):

            # cancel any press timer that may still be running
            if self.press_timer:
                self.press_timer.stop()
                self.press_timer = None

            self.release_lock = int(250*self.TIMER_HZ/1000)   # lock for 250ms
            # processing of the release lock requires the timer
            if not self.timer:
                # start a timer that does some slow decelleration
                self.timer = QTimer(self)
                self.timer.timeout.connect(self.on_timer)
                self.timer.start(1000 / self.TIMER_HZ)
            
            # if the user was dragging don't forward any event
            if self.dragging:
                self.dragging = None
                self.press_event = None
                return True

            # check if the intercepted press event came from the same
            # object that now receives a release event. In that case
            # re-inject the intercepted event now
            if self.press_event and self.press_event["obj"] == obj:
                # the user was not dragging. But we've eaten the previous
                # button press event and we thus need to fake the press
                # event now
                if time.time() - self.press_event["time"] > MIN_CLICK_TIME:
                    self.delayed_press = True
                    QApplication.sendEvent(self.press_event["obj"], self.press_event["event"])
                    self.delayed_press = False
                    self.press_event = None

            return False

        if event.type() == event.MouseMove and obj == self.widget() and self.press_event:
            # we are only interested in the vertical distance

            # not dragging yet? Check if user has moved the mouse far enough vertically
            # to start dragging
            if not self.dragging:
                dist_y = self.press_event["event"].globalPos().y() - event.globalPos().y();
                if (abs(dist_y) > 20):
                    # cancel any long press timer that may still  be runinng
                    self.press_timer.stop()
                    self.press_timer = None
                
                    self.dragging = (event.globalPos().y(), self.verticalScrollBar().value())

                    # restart drag timer
                    self.last_drag_pos = None
                    if not self.timer:
                        # start a timer that does some slow decelleration
                        self.timer = QTimer(self)
                        self.timer.timeout.connect(self.on_timer)
                        self.timer.start(1000 / self.TIMER_HZ)

            if self.dragging:
                dist_y = self.dragging[0] - event.globalPos().y();
                self.verticalScrollBar().setValue(self.dragging[1] + dist_y)
        
        return False

    def on_press_timer(self):
        # send custom "long press" event to the object that would have received the
        # initial click
        QApplication.sendEvent(self.press_event["obj"], QEvent(2000))
   
        # and cancel any possible future dragging and clicking
        self.dragging = None
        self.press_event = None

    def on_timer(self):
        if self.release_lock:
            self.release_lock -= 1
        
        # measure speed while user still drags
        if self.dragging:
            if self.last_drag_pos:
                self.drag_speed = self.TIMER_HZ * (self.verticalScrollBar().value() - self.last_drag_pos)
            self.last_drag_pos = self.verticalScrollBar().value()
        elif self.drag_speed:
            # scroll ...
            self.verticalScrollBar().setValue(self.verticalScrollBar().value() + int(self.drag_speed/self.TIMER_HZ))

            if self.drag_speed:
                dec = 5 * (1000/self.TIMER_HZ)
                if self.drag_speed < -dec:
                    self.drag_speed += dec
                elif self.drag_speed > dec:
                    self.drag_speed -= dec
                else:
                    self.drag_speed = None

        if not self.dragging and not self.drag_speed and not self.release_lock:
            self.timer.stop()
            self.timer = None

class Launcher(TouchApplication):
    def __init__(self, args):
        TouchApplication.__init__(self, args)

        # category setup also loads the locale
        self.category_setup()

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

    # read locale from /etc/locale
    def locale_read(self):
        loc = None
        try:
            with open("/etc/locale", "r") as f:
                for line in f:
                    # ignore everything behind hash
                    line = line.split('#')[0].strip()
                    if "=" in line:
                        parts = line.split('=')
                        var, val = parts[0].strip(), parts[1].strip()
                        if var == "LC_ALL":
                            # remove quotation marks if present
                            if (val[0] == val[-1]) and val.startswith(("'", '"')):
                                val = parts[1][1:-1]
                            # remove encoding if present
                            loc = val.split('.')[0]
        except:
            pass

        return loc
                        
    def app_is_running(self):
        if self.app_process == None:
            return False

        return self.app_process.poll() == None

    # this signal is received when an app reports it
    # has been launched
    def on_app_running(self, pid):
        # popup may have expired in the meantime
        if self.popup:
            self.popup.close()

    # this signal is received when app logging is to be 
    # enabled
    def on_enable_logging(self, on):
        if self.log_file:
            self.log_file.write("Logging stopped at: " + datetime.datetime.now().isoformat() + "\n")
            self.log_file.close()
            self.log_file = None

        if on:
            self.log_file = open("/tmp/app.log", 'w')
            self.log_file.write("Logging started at: " + datetime.datetime.now().isoformat() + "\n")
            self.log_file.flush()

    def settings_file(self):
        return os.path.join(os.path.expanduser("~"), ".launcher.config")

    def settings_save(self):
        config = configparser.RawConfigParser()
        config.add_section('view')
        config.set("view", 'path', self.icons.getPath())
        config.set("view", "min_click_time", MIN_CLICK_TIME)

        # save the 'button_launch' option if it exists
        try:
            config.set("view", "button_launch", self.button_launch)
        except AttributeError:
            pass
        
        try:
            with open(self.settings_file(), 'w') as configfile:
                config.write(configfile)
        except:
            pass

    def settings_load(self):
        if not os.path.isfile(self.settings_file()):
            return False

        config = configparser.RawConfigParser()
        config.read(self.settings_file())

        if config.has_option('view', 'button_launch'):
            self.button_launch = config.get('view', 'button_launch')
            self.icons.setButtonApp(self.button_launch)

        # get view path 
        if config.has_option('view', 'path'):
            path = config.get('view', 'path')
            self.icons.setPath(path)
        
        if config.has_option('view', 'min_click_time'):
            global MIN_CLICK_TIME
            MIN_CLICK_TIME = float(config.get("view", "min_click_time"))

        return True

    def launch_app(self, executable, managed, name):
        self.settings_save()

        if self.app_is_running():
            return

        # get managed state
        if managed.lower() == "text":
            # text mode apps will be handled by Raphaels new external system
            return
     
        # run the executable
        self.app_executable = executable

        if managed.lower() == "launcher-plugin":
            self.app_process = LauncherPluginAdapter(self, executable)
        else:
            # assume that we can just launch enything under non-windows
            if platform.system() != 'Windows':

                # give app the current locale
                locale = self.locale.name()
                env = os.environ.copy()
                env["LANGUAGE"] = locale
                env["LANG"] = locale
                env["LC_ALL"] = locale

                if self.log_file:
                    self.log_file.write("Application: " + executable + "\n")
                    self.log_file.write("Application started at: " + datetime.datetime.now().isoformat() + "\n")
                    self.log_file.flush()
                    self.log_master_fd, self.log_slave_fd = pty.openpty()
                    self.app_process = subprocess.Popen(str(executable), env=env, stdout=self.log_slave_fd, stderr=self.log_slave_fd)

                    # start a timer to monitor the ptys
                    self.log_timer = QTimer()
                    self.log_timer.timeout.connect(self.on_log_timer)
                    self.log_timer.start(100)
                else:
                    self.app_process = subprocess.Popen(str(executable), env=env)
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

    def category_setup(self):
        # reload locale
        locale_str = self.locale_read()
        if locale_str != None: self.locale = QLocale(locale_str)
        else:                  self.locale = QLocale.system()

        # this is needed for proper icon sorting, date display ...
        # but may fail if the requested locale isn't present
        try:
            QLocale.setDefault(self.locale)
            locale.setlocale(locale.LC_ALL, self.locale.name()+".UTF-8")
        except:
            pass

        self.translator = QTranslator()
        self.translator.load(self.locale, os.path.join(BASE, "launcher_"))
        self.installTranslator(self.translator)

        # try to load translations for all plugins
        self.plugin_translator = {}
        for file in os.listdir(os.path.join(BASE, PLUGINS_DIR)):
            if file.endswith(".py"):
                fname = os.path.splitext(os.path.basename(file))[0]
                self.plugin_translator[fname] = QTranslator()
                self.plugin_translator[fname].load(self.locale, os.path.join(BASE, PLUGINS_DIR, fname+"_"))
                self.installTranslator(self.plugin_translator[fname])

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

    def on_rescan(self):
        # re-translate categories as the language app may have triggered this
        self.category_setup()

        # rescan all apps
        self.apps = self.scan_app_dirs()

        self.icons.setApps(self.apps)

    def on_get_app(self, s):
        if self.app_is_running():
            # only return the <group>/<app>/<exec> part of the path
            app_dir, app_exec_name = os.path.split(self.app_executable)
            app_group, app_dir_name = os.path.split(app_dir)
            app_group_name = os.path.basename(app_group)
            s.write(os.path.join(app_group_name, app_dir_name, app_exec_name))
        s.write("\n")

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
    def manifest_import(self, dir, manifest):
        entries = ( "managed", "exec", "name", "icon" );
        app = AppItem("")
        app["dir"] = dir

        # load all entries from manifest
        for i in entries:
            if manifest.has_option('app', i):
                app[i] = manifest.get('app', i)

        # overwrite with locale specific values
        loc = self.locale.name().split('_')[0].strip().lower()
        for i in entries:
            if manifest.has_option(loc, i):
                app[i] = manifest.get(loc, i)

        # the category needs special treatment as it maps 
        # onto a limited set of pre-defined categories
        if manifest.has_option('app', "category"):
            # cat_id is the untranslated lowercase name which allows us
            # to retranslate if the user changes the language
            app['cat_id'] = manifest.get('app', "category").lower()
            if app['cat_id'] in self.category_map:
                app['category'] = self.category_map[app['cat_id']];

        # replace icon name by actual pixmap
        if 'icon' in app:
            app['icon'] = QPixmap(os.path.join(dir, app['icon']))
        else:
            app['icon'] = Icon("icon_app.png")
                
        return app

    # return a list of directories containing apps
    # searches under /opt/ftc/apps/<group>/<app>
    # the returned list is srted by the name of the apps
    # as stored in the manifest file
    def scan_app_dirs(self):
        loc = self.locale.name().split('_')[0].strip().lower()
        app_base = os.path.join(BASE, "apps")
        # scan for app group dirs first
        app_groups = os.listdir(app_base)
        # then scan for app dirs inside
        root_applist = AppList()
        for i in app_groups:
            try:
                app_group_dirs = os.listdir(os.path.join(app_base, i))
                for a in app_group_dirs:
                    # build full path of the app dir
                    app_dir = os.path.join(app_base, i, a)
                    # check if there's a manifest inside that dir
                    manifestfile = os.path.join(app_dir, "manifest")
                    if os.path.isfile(manifestfile):
                        # get app info
                        manifest = configparser.RawConfigParser()
                        manifest.read_file(open(manifestfile, "r", encoding="utf8"))

                        app = self.manifest_import(app_dir, manifest) 
                        root_applist.append(app)
            except:
                pass

        # try to apply folder hierarchy from xml file. 
        # if no folder hierarchy exists, build one from the categories
        # embedded in the manifests
        if not root_applist.apply_tree(self.category_map):
            # TODO: Move this into the AppList class
            
            # get categories
            categories = { }
            for i in root_applist:
                if "category" in i:
                    categories[i["category"]] = i["cat_id"]

            # create a folder for each category
            for c in categories:
                folder = FolderItem(c)
                folder["category"] = categories[c]

                # move all apps into the category/folder
                for app in root_applist:
                    if "category" in app and app["category"] == c:
                        folder["apps"].append(app)

                # and remove them from the main app list
                for app in folder["apps"]:
                    if "exec" in app:
                        root_applist.remove(app)

                # append new folder to list of apps.
                # This also prepends the "Up" folder
                root_applist.append(folder)

        root_applist.sort()
        return root_applist

    # walk through the apps tree trying to find a specific app
    def search_app(self, apps, app_dir):
        for app in apps:
            # only real apps contain a "dir" entry. Folders don't
            if "dir" in app:
                if app["dir"] == app_dir:
                    return app
            else:
                # make sure we don't follow the "Up" dir
                if not "up_folder" in app:
                    a = self.search_app(app["apps"], app_dir)
                    if a: 
                        return a
        return None

    def on_launch(self, name):
        # the given name is of the form group/app/executable
        # self.apps contains all dirs of apps like /opt/ftc/apps/group/app
        # we need to match this
        app_dir = os.path.dirname(os.path.join(BASE, "apps", name))

        app = self.search_app(self.apps, app_dir)

        if app and 'exec' in app:
            if 'managed' in app: managed = app['managed']
            else:                managed = "Yes"
                
            self.launch_app(os.path.join(app_dir, app['exec']), managed, app['name'])

    def translations(self):
        # the pylupdate4 program will find these ...
        QCoreApplication.translate("Messages", "Shutting down...")
        QCoreApplication.translate("Messages", "Rebooting...")

    def on_message(self, str):
        str = QCoreApplication.translate("Messages", str)
        MessageDialog(str).exec_()

    def on_confirm(self,sock,str):
        ConfirmationDialog(sock,str).exec_()

    def on_open_folder(self, apps):
        self.icons.setApps(apps)

    def addWidgets(self):
        # scan for available apps
        self.apps = self.scan_app_dirs()

        self.w = TouchTopWidget()

        # create icon grid
        self.icons = IconGrid(self.apps)
        self.icons.open_folder.connect(self.on_open_folder)
        self.icons.launch.connect(self.on_launch)

        # connect power button to icon grid
        self.w.power_button_pressed.connect(self.icons.on_power_button)

        # create a scrollarea for the icons
        self.scroll = VerticalScrollArea(self.icons, self.w)
        self.w.addWidget(self.scroll);

        # try to load current settings
        self.settings_load()

        self.w.show() 
 
# Only actually do something if this script is run standalone, so we can test our 
# application, but we're also able to import this program without actually running
# any code.
if __name__ == "__main__":

    # run websockify in the background to allow noVNC to connect to 
    # the qt embedded built-in vnc server
    try:
        import _thread, websockify
        from websockify.websocket import *
        from websockify.websocketproxy import *
        _thread.start_new_thread(websockify.websocketproxy.websockify_init, ())
    except:
        pass

    Launcher(sys.argv)
