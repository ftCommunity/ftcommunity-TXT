#! /usr/bin/env python3
# -*- coding: utf-8 -*-
#
import sys
import os
import configparser
from TouchStyle import *
from subprocess import Popen, call, PIPE
import socket
import array
import struct
import fcntl
import string
import platform
import shlex
import time
import urllib.request
import json
from _thread import start_new_thread
import ssl
from PyQt4 import QtCore
global w
CONFIG_FILE = '/media/sdcard/data/config.conf'
LOCAL_PATH = os.path.dirname(os.path.realpath(__file__))


class Language():

    def __init__(self, path, default_language):
        self.path = path
        self.default_language = default_language

        try:
            config = configparser.RawConfigParser()
            config.read(CONFIG_FILE)
            self.language = config.get('general', 'language')
        except:
            self.language = self.default_language

        try:
            self.global_error = False
            self.translation = configparser.RawConfigParser()
            self.translation.read(self.path)
        except:
            self.global_error = True

    def get_string(self, key):
        if self.global_error == False:
            try:
                return(self.string_transform(self.translation.get(self.language, key)))
            except:
                pass

            try:
                return(self.string_transform(self.translation.get(self.default_language, key)))
            except:
                pass
        return('missingno')

    def string_transform(self, string):
        transform = [
            ('&Auml;', 'Ä'), ('&auml;', 'ä'),
            ('&Ouml;', 'Ö'), ('&ouml;', 'ö'),
            ('&Uuml;', 'Ü'), ('&uuml;', 'ü')
        ]
        for t in transform:
            string = string.replace(t[0], t[1])
        return(string)

translation = Language(LOCAL_PATH + '/translation', 'EN')


class LanguageDialog(TouchDialog):

    def __init__(self, parent):
        self.avaible_languages = ['EN', 'DE']
        TouchDialog.__init__(self, translation.get_string('w_language_name'), parent)
        self.vbox = QVBoxLayout()
        self.vbox.addStretch()
        self.vbox.addWidget(QLabel(translation.get_string('w_language_lang_select')))
        self.lang_select = QComboBox()
        self.lang_select.addItems(self.avaible_languages)
        self.vbox.addWidget(self.lang_select)
        self.vbox.addStretch()
        self.save_but = QPushButton(translation.get_string('w_language_save'))
        self.save_but.clicked.connect(self.save)
        self.vbox.addWidget(self.save_but)
        self.vbox.addStretch()
        self.centralWidget.setLayout(self.vbox)
        try:
            config = configparser.RawConfigParser()
            config.read(CONFIG_FILE)
            self.lang_select.setCurrentIndex(self.avaible_languages.index(config.get('general', 'language')))
        except:
            pass

    def save(self):
        print(self.lang_select.currentText())
        config = configparser.ConfigParser()
        cfgfile = open(CONFIG_FILE, 'w')
        config.add_section('general')
        config.set('general', 'language', self.lang_select.currentText())
        config.write(cfgfile)
        cfgfile.close()
        self.close()


class AppButton(QToolButton):

    def __init__(self):
        QToolButton.__init__(self)

        shadow = QGraphicsDropShadowEffect(self)
        shadow.setOffset(QPointF(3, 3))
        self.setGraphicsEffect(shadow)

        self.setToolButtonStyle(Qt.ToolButtonTextUnderIcon)
        self.setObjectName("launcher-icon")

        # hide shadow while icon is pressed
    def mousePressEvent(self, event):
        self.graphicsEffect().setEnabled(False)
        QToolButton.mousePressEvent(self, event)

    def mouseReleaseEvent(self, event):
        self.graphicsEffect().setEnabled(True)
        QToolButton.mouseReleaseEvent(self, event)


class IconGrid(QStackedWidget):

    def __init__(self, apps):
        QStackedWidget.__init__(self)
        self.TILE_STYLE = """
        QPushButton {width: 100px; font-size: 13px; color:white; border-radius: 0; border-style: none; height: 75px}
        QPushButton:pressed {background-color: #123456}
        """
        self.TILE_LABEL = """
        QLabel {text-align: center; font-size: 15px; color:white}
        """
        self.apps = apps
        self.installEventFilter(self)

    def eventFilter(self, obj, event):
        if event.type() == event.Resize:
            self.columns = int(self.width() / 80)
            self.rows = int(self.height() / 80)
            self.createPages()
        return False

    def createPages(self):
        # remove all pages that might already be there
        while self.count():
            w = self.widget(self.count() - 1)
            self.removeWidget(w)
            w.deleteLater()

        icons_per_page = self.columns * self.rows
        page = None
        icons_total = 0
        # create pages to hold every app
        for name, data in sorted(self.apps.items()):
            # create a new page if necessary
            if not page:
                index = 0
                # create grid widget for page
                page = QWidget()
                grid = QGridLayout()
                grid.setSpacing(0)
                grid.setContentsMargins(0, 0, 0, 0)
                page.setLayout(grid)

                # if this isn't the first page, then add a "prev" arrow
                if self.count():
                    but = self.createIcon(os.path.join(LOCAL_PATH, "prev.png"), self.do_prev, 'Previous')
                    grid.addWidget(but, 0, 0, Qt.AlignCenter)
                    index = 1

            executable = data[0]

            # use icon file if one is mentioned in the manifest
            iconname = LOCAL_PATH + '/' + data[1]

            # create a launch button for this app
            but = self.createIcon(iconname, self.do_launch, name, executable)
            grid.addWidget(but, index / self.columns, index % self.columns, Qt.AlignCenter)

            # check if this is the second last icon on page
            # and if there are at least two more icons to be added. Then we need a
            # "next page" arrow
            if index == icons_per_page - 2:
                if icons_total < len(self.apps) - 2:
                    index = icons_per_page - 1
                    but = self.createIcon(os.path.join(LOCAL_PATH, "next.png"), self.do_next, 'Next')
                    grid.addWidget(but, index / self.columns, index % self.columns, Qt.AlignCenter)

            # advance position counters
            index += 1
            if index == icons_per_page:
                self.addWidget(page)
                page = None

        # fill last page with empty icons
        while index < icons_per_page:
            self.addWidget(page)
            empty = self.createIcon()
            grid.addWidget(empty, index / self.columns, index % self.columns, Qt.AlignCenter)
            index += 1
        icons_total += 1

    # handler of the "next" button
    def do_next(self):
        print('NEXT')
        self.setCurrentIndex(self.currentIndex() + 1)

    # handler of the "prev" button
    def do_prev(self):
        print('PREV')
        self.setCurrentIndex(self.currentIndex() - 1)

    # create an icon with label
    def createIcon(self, iconfile=None, on_click=None, appname=None, executable=None):
        if appname == None:
            button = AppButton()
            button.setText(appname)
            button.setProperty("executable", executable)
            return button
        buttonbox = QVBoxLayout()
        iconlabel = QLabel()
        pixmap = QPixmap(iconfile)
        iconlabel.setPixmap(pixmap)
        iconlabel.setAlignment(Qt.AlignCenter)
        txt = QLabel(appname)
        txt.setStyleSheet(self.TILE_LABEL)
        txt.setAlignment(Qt.AlignCenter)
        buttonbox.addWidget(iconlabel)
        buttonbox.addWidget(txt)
        button = QPushButton()
        button.setStyleSheet(self.TILE_STYLE)
        button.setLayout(buttonbox)
        if on_click:
            button.clicked.connect(on_click)
        button.setProperty("executable", executable)
        return button

    def do_launch(self, clicked):
        exec = self.sender().property("executable")
        dialog = exec(w)
        dialog.exec_()


class FtcGuiApplication(TouchApplication):

    def __init__(self, args):
        TouchApplication.__init__(self, args)
        global w
        self.w = TouchWindow(translation.get_string('app_name'))
        self.icons = IconGrid({translation.get_string('menu_language'): [LanguageDialog, 'icons/language.png']})
        self.vbox = QVBoxLayout()
        self.vbox.addWidget(self.icons)
        self.w.centralWidget.setLayout(self.vbox)
        self.w.show()
        w = self.w
        self.exec_()


if __name__ == "__main__":
    FtcGuiApplication(sys.argv)
