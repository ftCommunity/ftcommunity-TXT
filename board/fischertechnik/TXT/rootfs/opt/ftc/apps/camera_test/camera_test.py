#! /usr/bin/env python
# -*- coding: utf-8 -*-
#

import sys, numpy, cv2
from TxtStyle import *

WIDTH=320
HEIGHT=(WIDTH*3/4)
FPS=10

# check if there's a camera device index supplied via
# the environment
CAM_DEV = os.environ.get('FTC_CAM')
if CAM_DEV == None: CAM_DEV = 0
else:               CAM_DEV = int(CAM_DEV)

class CamWidget(QWidget):
    def __init__(self, parent=None):

        super(CamWidget, self).__init__(parent)
        
        # initialize camera
        self.cap = cv2.VideoCapture(CAM_DEV)
        if self.cap.isOpened():
            self.cap.set(3,WIDTH)
            self.cap.set(4,HEIGHT)
            self.cap.set(5,FPS)

        timer = QTimer(self)
        timer.timeout.connect(self.update)
        timer.start(1000/FPS)

        qsp = QSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)
        qsp.setHeightForWidth(True)
        self.setSizePolicy(qsp)

    def sizeHint(self):
        return QSize(WIDTH,HEIGHT)

    def heightForWidth(self,w):
        return w*3/4
        
    def grab(self):
        self.frame = self.cap.read()[1]

        # expand/shrink to widget size
        wsize = (self.size().width(), self.size().height())
        self.cvImage = cv2.resize(self.frame, wsize)

        height, width, byteValue = self.cvImage.shape
        bytes_per_line = byteValue * width

        cv2.cvtColor(self.cvImage, cv2.COLOR_BGR2RGB, self.cvImage)
        self.mQImage = QImage(self.cvImage, width, height,
                              bytes_per_line, QImage.Format_RGB888)

    def paintEvent(self, QPaintEvent):
        painter = QPainter()
        painter.begin(self)

        if not self.cap.isOpened():
            painter.drawText(QRect(QPoint(0,0), self.size()),
                             Qt.AlignCenter, "No camera");
        else:
            self.grab()
            painter.drawImage(0,0,self.mQImage)
            
        painter.end()


class FtcGuiApplication(TxtApplication):
    def __init__(self, args):
        TxtApplication.__init__(self, args)

        # create the empty main window
        self.w = TxtWindow("Camera")

        self.cw = CamWidget()
        
        if False:
            self.w.setCentralWidget(self.cw)
        else:
            vbox = QVBoxLayout()
            vbox.addStretch()
            vbox.addWidget(self.cw)
            vbox.addStretch()
            self.w.centralWidget.setLayout(vbox)
        
        self.w.show()
        self.exec_()        

if __name__ == "__main__":
    FtcGuiApplication(sys.argv)
