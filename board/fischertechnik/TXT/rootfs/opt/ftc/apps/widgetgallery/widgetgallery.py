#! /usr/bin/env python3
# -*- coding: utf-8 -*-
#

import sys
from TxtStyle import *

class FtcGuiApplication(TxtApplication):
    def __init__(self, args):
        TxtApplication.__init__(self, args)

        # create the empty main window
        w = TxtWindow("Widgets")

        self.tab = QTabWidget()

        # http://doc.qt.io/qt-4.8/widgets-and-layouts.html

        # ============= dial and lcdnumber widgets ================
        page = QWidget()
        vbox = QVBoxLayout()

        dial = QDial()
        dial.setNotchesVisible(True)
        vbox.addWidget(dial)

        lcd = QLCDNumber(2)
        vbox.addWidget(lcd)

        dial.valueChanged.connect(lcd.display)

        dial.setValue(50)

        page.setLayout(vbox)
        self.tab.addTab(page, "Dial")

        # ============= spinbox and progressbar widgets ================

        page = QWidget()
        vbox = QVBoxLayout()

        sb = QSpinBox()
        sb.lineEdit().setReadOnly(True)    # we don't have a keyboard in the TXT
        sb.setRange(0, 100)
        vbox.addWidget(sb)

        pb = QProgressBar()
        pb.setRange(0,100)
        vbox.addWidget(pb)
        
        sb.valueChanged.connect(pb.setValue)

        sb.setValue(50)

        page.setLayout(vbox)
        self.tab.addTab(page, "Bar")

        # ============= text with scrollbars ================
            
        #slider = QSlider(Qt.Horizontal)
        #vbox.addWidget(slider)

        page = QWidget()
        vbox = QVBoxLayout()

        text = QTextEdit("Lorem ipsum dolor sit amet, consetetur sadipscing elitr, sed diam nonumy eirmod tempor invidunt ut labore et dolore magna aliquyam erat, sed diam voluptua. At vero eos et accusam et justo duo dolores et ea rebum. Stet clita kasd gubergren, no sea takimata sanctus est Lorem ipsum dolor sit amet. Lorem ipsum dolor sit amet, consetetur sadipscing elitr, sed diam nonumy eirmod tempor invidunt ut labore et dolore magna aliquyam erat, sed diam voluptua. At vero eos et accusam et justo duo dolores et ea rebum. Stet clita kasd gubergren, no sea takimata sanctus est Lorem ipsum dolor sit amet.")
        vbox.addWidget(text)

        page.setLayout(vbox)
        self.tab.addTab(page, "Txt")

        w.setCentralWidget(self.tab)

        w.show()
        self.exec_()        
 
if __name__ == "__main__":
    FtcGuiApplication(sys.argv)
