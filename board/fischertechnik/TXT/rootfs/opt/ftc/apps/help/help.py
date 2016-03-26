#! /usr/bin/env python
# -*- coding: utf-8 -*-
#
import sys, os
from TxtStyle import *

class FtcGuiApplication(TxtApplication):
    def __init__(self, args):
        TxtApplication.__init__(self, args)

        # create the empty main window
        self.w = TxtWindow("Help")

        # and add some text
        self.txt = QLabel("Help "
                          "App under development\n\n"
                          "(c) 2016 the ft:community")
        self.txt.setObjectName("smalllabel")
        self.txt.setWordWrap(True)
        self.txt.setAlignment(Qt.AlignCenter)
         
        self.w.setCentralWidget(self.txt)

        self.w.show()
        self.exec_()        
 
if __name__ == "__main__":
    FtcGuiApplication(sys.argv)
