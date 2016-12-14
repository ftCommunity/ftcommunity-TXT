#! /usr/bin/env python3
# -*- coding: utf-8 -*-
#
import sys, os, socket
from TouchStyle import *

appdir = os.path.dirname(os.path.realpath(__file__))

class LanguageWindow(TouchWindow):
    closed = pyqtSignal()

    def __init__(self, str):
        TouchWindow.__init__(self, str)

    def closeEvent(self, evt):
        TouchWindow.closeEvent(self, evt)
        self.closed.emit()

class FtcGuiApplication(TouchApplication):
    def __init__(self, args):
        TouchApplication.__init__(self, args)

        locale_str = self.locale_read()
        self.translation_load(locale_str)

        # create the empty main window
        self.w = LanguageWindow(QCoreApplication.translate("main","Language"))

        self.vbox = QVBoxLayout()

        self.vbox.addStretch()

        self.icon = QLabel()
        self.icon.setAlignment(Qt.AlignCenter)
        self.icon.setPixmap(QPixmap(os.path.join(appdir, "english.png")))
        self.vbox.addWidget(self.icon)

        self.vbox.addStretch()

        self.lang_w = QComboBox()
        self.lang_w.activated[str].connect(self.set_lang)
        self.vbox.addWidget(self.lang_w)
   
        self.vbox.addStretch()

        self.update_gui()
        self.select_lang(locale_str)

        self.w.centralWidget.setLayout(self.vbox)

        self.w.closed.connect(self.closed)

        self.w.show()
        self.exec_()        

    def translation_load(self, str):
        if str != None: self.locale = QLocale(str)
        else:           self.locale = QLocale.system()
        self.translator = QTranslator()
        self.translator.load(self.locale, os.path.join(appdir, "language_"))
        self.installTranslator(self.translator)

    def update_gui(self):
        # set the possible language strings
        self.set_lang_names()

        # set updated language names
        self.lang_w.clear()
        langs = self.get_lang_names()
        for l in langs: self.lang_w.addItem(l)

    # write locale to  /etc/locale
    def locale_write(self, loc):
        with open("/etc/locale", "w") as f:
            print('LANG="'+loc+'"', file=f)
            print('LC_ALL="'+loc+'"', file=f)

        # request launcher rescan
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            # Connect to server and send data
            sock.connect(("localhost", 9000))
            sock.sendall(bytes("rescan\n", "UTF-8"))
        except socket.error as msg:
            pass

    # read locale from /etc/locale
    def locale_read(self):
        loc = None
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
        return loc
 
    def select_lang(self, id):
        icons = { 'en': 'english.png', 'de': 'german.png',
                  'nl': 'dutch.png',   'fr': 'french.png' }

        id = id.split('_')[0]    # only use the first two letters (de, en...)
        if not id in icons:
            id = 'en'

        self.icon.setPixmap(QPixmap(os.path.join(appdir, icons[id])))

        index = self.lang_w.findText(self.lang_names[id])
        if index >= 0: self.lang_w.setCurrentIndex(index)

    def set_lang(self, lang):
        key = list(self.lang_names.keys())[list(self.lang_names.values()).index(lang)]
        locale_str = self.locale_str(key).split('.')[0]
        
        # load new language
        self.translation_load(locale_str)
        self.update_gui()        

        # select right entry in combobox
        self.select_lang(key)

        # and set title
        self.w.titlebar.setText(QCoreApplication.translate("main","Language"))

    def locale_str(self, key):
        countries = { 'en': 'US', 'de': 'DE',
                      'nl': 'NL', 'fr': 'FR' }
        if not key in countries:
            key = 'en'

        return key+"_"+countries[key]+".UTF-8"

    def get_lang_names(self):
        rval = []
        for l in self.lang_names:
            rval.append(self.lang_names[l])
        return sorted(rval)

    def set_lang_names(self):
        self.lang_names = { 
            'en': QCoreApplication.translate("lang", "English"), 
            'de': QCoreApplication.translate("lang", "German"), 
            'nl': QCoreApplication.translate("lang", "Dutch"), 
            'fr': QCoreApplication.translate("lang", "French")
            }

    def closed(self):
        lang = self.lang_w.currentText()
        key = list(self.lang_names.keys())[list(self.lang_names.values()).index(lang)]
        loc = self.locale_str(key)

        if(loc.split('.')[0].split('_')[0] != 
           self.locale_read().split('_')[0]):
            
            self.locale_write(loc)
            
if __name__ == "__main__":
    FtcGuiApplication(sys.argv)
