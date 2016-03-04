#! /usr/bin/env python
# -*- coding: utf-8 -*-
#
import sys, os
from PyQt4.QtCore import *
from PyQt4.QtGui import *

# The TXT does not use windows. Instead we just paint custom 
# toplevel windows fullscreen
class TxtTopWidget(QWidget):
    def __init__(self):
        QWidget.__init__(self)
        # the setFixedSize is only needed for testing on a desktop pc
        # the centralwidget name makes sure the themes background 
        # gradient is being used
        self.setFixedSize(240, 320)
        self.setObjectName("centralwidget")

        # TXT windows are always fullscreen
    def show(self):
        QWidget.showFullScreen(self)

# http://stackoverflow.com/questions/18196799/how-can-i-show-a-pyqt-modal-dialog-and-get-data-out-of-its-controls-once-its-clo
class TxtDialog(QDialog):
    def __init__(self, parent = None):
        QWidget.__init__(self, parent)
        # the setFixedSize is only needed for testing on a desktop pc
        # the centralwidget name makes sure the themes background 
        # gradient is being used
        self.setFixedSize(240, 320)
        self.setObjectName("centralwidget")

        # TXT dialogs are always fullscreen
    def exec_(self):
        self.showFullScreen()
        return QDialog.exec_(self)

class FtcGuiApplication(QApplication):
    def __init__(self, args):
        QApplication.__init__(self, args)
        # load stylesheet from the same place the script was loaded from
        with open(os.path.dirname(os.path.realpath(__file__)) + "/txt.qss","r") as fh:
            self.setStyleSheet(fh.read())
            fh.close()

        self.addWidgets()
        self.exec_()        

    def about_dialog(self):
        self.aboutw = TxtDialog(self.w)
        # fill content area
 
        # create a vertical layout and put all widgets inside
        self.aboutw.layout = QVBoxLayout()
        self.aboutw.lbl = QLabel("About")
        self.aboutw.lbl.setAlignment(Qt.AlignCenter)
        self.aboutw.txt = QLabel("Fischertechnik TXT firmware community edition V0.0.\n\n"
                                 "(c) 2016 the ft:community")
        # make font 2/3 the size
        #        font = self.aboutw.txt.font()
        #        print font.pointSizeF()
        #        font.setPointSize(font.pointSizeF()/2)
        #        self.aboutw.txt.setFont(font)

        self.aboutw.txt.setObjectName("smalllabel")
        self.aboutw.txt.setWordWrap(True)
        self.aboutw.btn = QPushButton("OK")
        self.aboutw.btn.clicked.connect(self.aboutw.close)
        self.aboutw.layout.addWidget(self.aboutw.lbl)
        self.aboutw.layout.addWidget(self.aboutw.txt)
        self.aboutw.layout.addWidget(self.aboutw.btn)
        self.aboutw.setLayout(self.aboutw.layout)        
        self.aboutw.exec_()

    def addWidgets(self):
        self.w = TxtTopWidget()

        # create a label
        self.lbl = QLabel("Menu")
        self.lbl.setAlignment(Qt.AlignCenter)

        # and some buttons
        self.btn1 = QPushButton("About")
        self.btn1.clicked.connect(self.about_dialog)
        self.btn2 = QPushButton("Button 2")
        self.btn3 = QPushButton("Button 3")

        # and a combobox
        self.cbox = QComboBox()
        self.cbox.addItem("Entry 1")
        self.cbox.addItem("Entry 2")
        self.cbox.addItem("Entry 3")

        # create a vertical layout and put all widgets inside
        self.layout = QVBoxLayout()
        self.layout.addWidget(self.lbl)
        self.layout.addWidget(self.btn1)
        self.layout.addWidget(self.btn2)
        self.layout.addWidget(self.btn3)
        self.layout.addWidget(self.cbox)

        self.w.setLayout(self.layout)        
        self.w.show() 
 
# Only actually do something if this script is run standalone, so we can test our 
# application, but we're also able to import this program without actually running
# any code.
if __name__ == "__main__":
    app = FtcGuiApplication(sys.argv)
