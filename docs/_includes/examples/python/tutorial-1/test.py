#! /usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
from TouchStyle import *

class FtcGuiApplication(TouchApplication):
    def __init__(self, args):
        TouchApplication.__init__(self, args)

        # Creates an empty MainWindow
        w = TouchWindow("Test")
        w.show()
        self.exec_()        

if __name__ == "__main__":
    FtcGuiApplication(sys.argv)
