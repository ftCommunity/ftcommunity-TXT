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

        self.w = TxtWindow("About")

        self.txt = QLabel("Fischertechnik TXT firmware "
                          "community edition V0.0.\n\n"
                          "(c) 2016 the ft:community")
        self.txt.setObjectName("smalllabel")
        self.txt.setWordWrap(True)
        self.txt.setAlignment(Qt.AlignCenter)
         
        self.w.addWidget(self.txt)

        self.w.show()
        self.exec_()        
 
if __name__ == "__main__":
    FtcGuiApplication(sys.argv)
