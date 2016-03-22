#! /usr/bin/env python
# -*- coding: utf-8 -*-
#
import sys, os
from PyQt4.QtCore import *
from PyQt4.QtGui import *

# import TXT style
base = os.path.dirname(os.path.realpath(__file__)) + "/../../"
sys.path.append(base)
from txt import *

class FtcGuiApplication(QApplication):
    def __init__(self, args):
        QApplication.__init__(self, args)
        # load stylesheet from the same place the script was loaded from
        with open(base + "txt.qss","r") as fh:
            self.setStyleSheet(fh.read())
            fh.close()

        self.w = TxtWindow("Test 3")
        self.dummy = QWidget()
        ## the icongrid is transparent
        self.dummy.setObjectName("empty")
        self.w.addWidget(self.dummy)

        self.w.show() 

        self.exec_()        
 
if __name__ == "__main__":
    FtcGuiApplication(sys.argv)
