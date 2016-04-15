#! /usr/bin/env python3
# -*- coding: utf-8 -*-
#

import sys, numpy, cv2, zbarlight
from TxtStyle import *
from PIL import Image

WIDTH=240
HEIGHT=(WIDTH*3/4)
FPS=10

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

        # hsv to rgb
        cv2.cvtColor(self.cvImage, cv2.COLOR_BGR2RGB, self.cvImage)
        self.mQImage = QImage(self.cvImage, width, height,
                              bytes_per_line, QImage.Format_RGB888)

        cv_img = cv2.cvtColor(self.cvImage, cv2.COLOR_RGB2GRAY)
        raw = Image.fromarray(cv_img)

        # extract results and display first code found
        codes = zbarlight.scan_codes('qrcode', raw)
        if codes:
            self.emit(SIGNAL('code(QString)'), codes[0].decode("UTF-8"))

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
        self.w = TxtWindow("ZBar")

        self.cw = CamWidget()

        if False:
            self.w.setCentralWidget(self.cw)
        else:
            vbox = QVBoxLayout()
            vbox.setSpacing(0)
            vbox.setContentsMargins(0,0,0,0)

            vbox.addWidget(self.cw)
            vbox.addStretch()

            self.lbl = QLabel()
            self.lbl.setObjectName("smalllabel")
            self.lbl.setAlignment(Qt.AlignCenter)
            vbox.addWidget(self.lbl)
            vbox.addStretch()

            self.connect( self.cw, SIGNAL("code(QString)"),
                          self.on_code_detected )

            self.w.centralWidget.setLayout(vbox)
        
            self.hide_timer = QTimer(self)
            self.hide_timer.timeout.connect(self.on_code_timeout)
            self.hide_timer.setSingleShot(True)

        self.w.show()
        self.exec_()        

    def on_code_detected(self,str):
        self.lbl.setText(str)
        self.hide_timer.start(1000)  # hide after 1 second

    def on_code_timeout(self):
        self.lbl.setText("")

if __name__ == "__main__":
    FtcGuiApplication(sys.argv)
