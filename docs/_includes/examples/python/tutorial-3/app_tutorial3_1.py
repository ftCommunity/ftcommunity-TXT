#! /usr/bin/env python3
# -*- coding: utf-8 -*-
#
import sys
import ftrobopy                                              # Import the ftrobopy module
from TouchStyle import *

class FtcGuiApplication(TouchApplication):
    def __init__(self, args):
        TouchApplication.__init__(self, args)
        # create the empty main window
        w = TouchWindow("Tut_3_1")

        try:
            txt = ftrobopy.ftrobopy("localhost", 65000)      # connect to TXT's IO controller
        except:
            txt = None                                       # set TXT to "None" of connection failed

        if not txt:
            # display error if TXT could no be connected
            # error messages is centered and may span
            # over several lines
            err_msg = QLabel("Error connecting IO server")   # create the error message label
            err_msg.setWordWrap(True)                        # allow it to wrap over several lines
            err_msg.setAlignment(Qt.AlignCenter)             # center it horizontally
            w.setCentralWidget(err_msg)                      # attach it to the main output area
            
        w.show()
        self.exec_()        

if __name__ == "__main__":
    FtcGuiApplication(sys.argv)

