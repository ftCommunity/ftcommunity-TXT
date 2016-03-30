#! /usr/bin/env python
# -*- coding: utf-8 -*-
#

import sys, numpy, cv2
from TxtStyle import *

WIDTH=240
HEIGHT=(WIDTH*3/4)
FPS=10

CAM_DEV = os.environ.get('FTC_CAM')
if CAM_DEV == None: CAM_DEV = 0
else:               CAM_DEV = int(CAM_DEV)

class SmallLabel(QLabel):
    def __init__(self, str, parent=None):
        super(SmallLabel, self).__init__(str, parent)
        self.setAlignment(Qt.AlignCenter)
        self.setObjectName("tinylabel")

class RangePopup(QFrame):
    def __init__(self, range, parent=None):
        super(RangePopup, self).__init__(parent)
        self.setWindowFlags(Qt.Popup)
        self.setObjectName("popup")

        self.resize(100, 160)

        # add content
        grid = QGridLayout()
        self.min = QSlider()
        self.min.setMaximum(255)
        self.min.setValue(range[0])
        self.max = QSlider()
        self.max.setMaximum(255)
        self.max.setValue(range[1])
        grid.addWidget(SmallLabel("min"),0,0)
        grid.addWidget(self.min,1,0)
        grid.addWidget(SmallLabel("max"),0,1)
        grid.addWidget(self.max,1,1)
        self.setLayout(grid)

        self.min.valueChanged.connect(self.min_changed)
        self.max.valueChanged.connect(self.max_changed)

        # open popup centered on top of parent
        pos = parent.mapToGlobal(QPoint(0,parent.height()))
        pos = pos - QPoint(-(parent.width()-self.width())/2, self.height())
        self.move(pos)

    def min_changed(self, val):
        if val > self.max.value():
            self.max.setValue(val)
        self.emit( SIGNAL('range_changed(int,int)'),  self.min.value(), self.max.value())   

    def max_changed(self, val):
        if val < self.min.value():
            self.min.setValue(val)
        self.emit( SIGNAL('range_changed(int,int)'),  self.min.value(), self.max.value())   
        
    def mouseReleaseEvent(self, QMouseEvent):
        self.close();

class RangeWidget(QToolButton):
    def __init__(self, str, range, parent=None):
        super(RangeWidget, self).__init__(parent)
        self.range = range
        self.setText(str)
        self.setPopupMode(QToolButton.InstantPopup)

    def on_range_changed(self, r_min, r_max):
        self.emit( SIGNAL('range_changed(int,int)'),  r_min, r_max)

    def mouseReleaseEvent(self, QMouseEvent):
        self.popup = RangePopup(self.range, self)
        self.connect( self.popup, SIGNAL("range_changed(int,int)"), self.on_range_changed )
        self.popup.show()

class CamWidget(QWidget):
    def __init__(self, parent=None):

        super(CamWidget, self).__init__(parent)
        
        self.show_src_img = False

        # setup sane initial values
        self.hsv_min = ( 9, 100, 100)
        self.hsv_max = ( 40, 215, 255)
        
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

        # bgr to hsv
        cv2.cvtColor(self.cvImage, cv2.COLOR_BGR2HSV, self.cvImage)

        self.thresh = cv2.inRange(self.cvImage, self.hsv_min, self.hsv_max)

        if self.show_src_img:
            # hsv to rgb
            cv2.cvtColor(self.cvImage, cv2.COLOR_HSV2RGB, self.cvImage)
            self.mQImage = QImage(self.cvImage, width, height,
                                  bytes_per_line, QImage.Format_RGB888)
        else:
            # thresh is a bw image stored as a grayscale image since
            # cv doesn't support monochrome bitmas. Qt doesn't support
            # grayscale (but monochrome). Se we need to convert back
            # to RGB
            self.thresh_rgb = cv2.cvtColor(self.thresh,cv2.COLOR_GRAY2RGB)
            self.mQImage = QImage(self.thresh_rgb, width, height,
                                  bytes_per_line, QImage.Format_RGB888)

    def on_h_changed(self, r_min, r_max):
        self.hsv_min = (r_min, self.hsv_min[1], self.hsv_min[2])
        self.hsv_max = (r_max, self.hsv_max[1], self.hsv_max[2])

    def on_s_changed(self, r_min, r_max):
        self.hsv_min = (self.hsv_min[0], r_min, self.hsv_min[2])
        self.hsv_max = (self.hsv_max[0], r_max, self.hsv_max[2])

    def on_v_changed(self, r_min, r_max):
        self.hsv_min = (self.hsv_min[0], self.hsv_min[1], r_min)
        self.hsv_max = (self.hsv_max[0], self.hsv_max[1], r_max)

    def mouseReleaseEvent(self, QMouseEvent):
        self.show_src_img = not self.show_src_img

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
        self.w = TxtWindow("ColoRange")

        self.cw = CamWidget()
        
        if False:
            self.w.setCentralWidget(self.cw)
        else:
            vbox = QVBoxLayout()
            vbox.setSpacing(0)
            vbox.setContentsMargins(0,0,0,0)

            vbox.addWidget(self.cw)
            vbox.addStretch()

            grid_w = QWidget()
            grid = QGridLayout()
            grid.setSpacing(0)
            grid.setContentsMargins(0,0,0,0)

            self.h_lbl = SmallLabel("000:255")
            self.show_h(self.cw.hsv_min[0], self.cw.hsv_max[0])
            grid.addWidget(self.h_lbl,0,0)

            h_range = (self.cw.hsv_min[0], self.cw.hsv_max[0])
            self.range_h = RangeWidget("H", h_range)
            self.connect( self.range_h, SIGNAL("range_changed(int,int)"), 
                          self.cw.on_h_changed )
            self.connect( self.range_h, SIGNAL("range_changed(int,int)"),
                          self.show_h )
            grid.addWidget(self.range_h,1,0)

            self.s_lbl = SmallLabel("")
            self.show_s(self.cw.hsv_min[1], self.cw.hsv_max[1])
            grid.addWidget(self.s_lbl,0,1)

            s_range = (self.cw.hsv_min[1], self.cw.hsv_max[1])
            self.range_s = RangeWidget("S", s_range)
            self.connect( self.range_s, SIGNAL("range_changed(int,int)"),
                          self.cw.on_s_changed )
            self.connect( self.range_s, SIGNAL("range_changed(int,int)"),
                          self.show_s )
            grid.addWidget(self.range_s,1,1)

            self.v_lbl = SmallLabel("")
            self.show_v(self.cw.hsv_min[2], self.cw.hsv_max[2])
            grid.addWidget(self.v_lbl,0,2)

            v_range = (self.cw.hsv_min[2], self.cw.hsv_max[2])
            self.range_v = RangeWidget("V", v_range)
            self.connect( self.range_v, SIGNAL("range_changed(int,int)"),
                          self.cw.on_v_changed )
            self.connect( self.range_v, SIGNAL("range_changed(int,int)"),
                          self.show_v )
            grid.addWidget(self.range_v,1,2)

            grid_w.setLayout(grid)

            vbox.addWidget(grid_w)
            self.w.centralWidget.setLayout(vbox)
        
            vbox.addStretch()

        self.w.show()
        self.exec_()        

    def show_h(self, h_min, h_max):
        self.h_lbl.setText("{:d}:{:d}".format(h_min,h_max))

    def show_s(self, s_min, s_max):
        self.s_lbl.setText("{:d}:{:d}".format(s_min,s_max))

    def show_v(self, v_min, v_max):
        self.v_lbl.setText("{:d}:{:d}".format(v_min,v_max))

if __name__ == "__main__":
    FtcGuiApplication(sys.argv)
