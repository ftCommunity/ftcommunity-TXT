#! /usr/bin/env python
# -*- coding: utf-8 -*-
#

import sys, numpy, cv2
from TxtStyle import *

class CamWidget(QWidget):
    def __init__(self, parent=None):

        super(CamWidget, self).__init__(parent)

        self.cap = cv2.VideoCapture(0)
        # if(!cap.isOpened())  // check if we succeeded
        #   return -1;

        timer = QTimer(self)
        timer.timeout.connect(self.update)
        timer.start(1000)

    def grab(self):

        self.frame = self.cap.read()[1]
        # self.frame = cv2.imread("cat.jpg")
        
        self.cvImage = cv2.resize(self.frame, (240,180))

        height, width, byteValue = self.cvImage.shape
        bytes_per_line = byteValue * width

        cv2.cvtColor(self.cvImage, cv2.COLOR_BGR2RGB, self.cvImage)
        self.mQImage = QImage(self.cvImage, width, height, bytes_per_line, QImage.Format_RGB888)

    def paintEvent(self, QPaintEvent):
        #        print "paint", self.width(), self.height()
        self.grab()
        painter = QPainter()
        painter.begin(self)
        painter.drawImage(0, 0, self.mQImage)
        painter.end()


class FtcGuiApplication(TxtApplication):
    def __init__(self, args):
        TxtApplication.__init__(self, args)

        # create the empty main window
        self.w = TxtWindow("Camera")

        self.cw = CamWidget()
        self.w.setCentralWidget(self.cw)
        
        self.w.show()
        self.exec_()        

if __name__ == "__main__":
    FtcGuiApplication(sys.argv)
