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
        w = TouchWindow("Tut_3_2")

        try:
            txt = ftrobopy.ftrobopy("localhost", 65000)      # connect to TXT's IO controller
        except:
            txt = None                                       # set TXT to "None" of connection failed

        if not txt:
	        # display error of TXT could no be connected
            # error messages is centered and may span
            # over several lines
            err_msg = QLabel("Error connecting IO server")   # create the error message label
            err_msg.setWordWrap(True)                        # allow it to wrap over several lines
            err_msg.setAlignment(Qt.AlignCenter)             # center it horizontally
            w.setCentralWidget(err_msg)                      # attach it to the main output area
        else:
            # initialization went fine. So the main gui
            # is being drawn
            button = QPushButton("Toggle O1")                # create a button labeled "Toggle O1"
            w.setCentralWidget(button)                       # attach it to the main output area

	    # configure all TXT outputs to normal mode
            M = [ txt.C_OUTPUT, txt.C_OUTPUT, txt.C_OUTPUT, txt.C_OUTPUT ]
            I = [ (txt.C_SWITCH, txt.C_DIGITAL ),
                  (txt.C_SWITCH, txt.C_DIGITAL ),
                  (txt.C_SWITCH, txt.C_DIGITAL ),
                  (txt.C_SWITCH, txt.C_DIGITAL ),
                  (txt.C_SWITCH, txt.C_DIGITAL ),
                  (txt.C_SWITCH, txt.C_DIGITAL ),
                  (txt.C_SWITCH, txt.C_DIGITAL ),
                  (txt.C_SWITCH, txt.C_DIGITAL ) ]
            txt.setConfig(M, I)
            txt.updateConfig()

        w.show()
        self.exec_()

if __name__ == "__main__":
    FtcGuiApplication(sys.argv)
