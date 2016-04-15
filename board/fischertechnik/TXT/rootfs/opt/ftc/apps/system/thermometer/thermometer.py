#! /usr/bin/env python3
# -*- coding: utf-8 -*-
#
# Based on:
# https://raw.githubusercontent.com/Slxe/Tutorials/master/python/Zetcode/Advanced%20PyQt4%20%28PySide%29%20Tutorial/06%20-%20Custom%20Widgets/thermometerwidget.py

import sys, os, math, ftrobopy
from TxtStyle import *

K2C = 273.0
B = 3900.0
R_N = 1500.0
T_N = K2C + 25.0


OFFSET = 10
SCALE_HEIGHT = 224

FILL_FACTOR = 0.8

SCALE_RADIUS = 7.5

BULB_RADIUS = 12.5
BULB_CENTER_V = 268
BULB_CENTER_H = 0

class Thermometer(QWidget):

    def __init__(self, parent):
        QWidget.__init__(self)
        self.value = 0

    def paintEvent(self, event):
        painter = QPainter()
        painter.begin(self)
        self.initDrawing(painter)
        self.drawTemperature(painter)
        self.drawBackground(painter)
        painter.end()

    def initDrawing(self, painter):
        self.m_min = 0.0
        self.m_max = 50.0

        painter.setRenderHint(QPainter.Antialiasing)
        painter.translate(self.width()/2.0, 0.0)
        painter.scale(self.height()/300.0, self.height()/300.0)

    def drawBackground(self, painter):
        path = QPainterPath()

        # BULB_CENTER_V = 268

        # Y coordinate of scale/bulb contact point
        contact = math.sqrt(BULB_RADIUS**2 - SCALE_RADIUS**2)

        # draw the bulb
        path.moveTo(                              -SCALE_RADIUS, BULB_CENTER_V-contact)
        path.quadTo(-BULB_RADIUS, BULB_CENTER_V-5, -BULB_RADIUS, BULB_CENTER_V)  # tl
        path.quadTo(-BULB_RADIUS, BULB_CENTER_V+10,         0.0, BULB_CENTER_V+BULB_RADIUS)           # bl
        path.quadTo( BULB_RADIUS, BULB_CENTER_V+10, BULB_RADIUS, BULB_CENTER_V)   # br
        path.quadTo( BULB_RADIUS, BULB_CENTER_V-5, SCALE_RADIUS, BULB_CENTER_V-contact)  # tr

        path.lineTo(SCALE_RADIUS, 25.0)                         # right scale side
        path.quadTo(SCALE_RADIUS, 12.5, 0, 12.5)                # topright scale
        path.quadTo(-SCALE_RADIUS, 12.5, -SCALE_RADIUS, 25.0)   # topleft scale
        path.lineTo(-SCALE_RADIUS, BULB_CENTER_V-11)            # left scale side

        p1 = QPointF(-2.0, 0.0)
        p2 = QPointF(12.5, 0.0)
        linearGrad = QLinearGradient(p1, p2)
        linearGrad.setSpread(QGradient.ReflectSpread)
#        linearGrad.setColorAt(1.0, QColor(0, 150, 225, 170))
        linearGrad.setColorAt(1.0, QColor(255, 255, 255, 170))
        linearGrad.setColorAt(0.0, QColor(255, 255, 255, 0))  # transparent

        painter.setBrush(QBrush(linearGrad))
        painter.setPen(Qt.white)
        painter.drawPath(path)

        pen = QPen(Qt.white)
        step = SCALE_HEIGHT / 10.0
        
        for i in range(11):
            pen.setWidthF(2.0)
            length = 6

            if i % 2:
                length = 2.5
                pen.setWidthF(1)

            painter.setPen(pen)
            painter.drawLine(-(SCALE_RADIUS+0.5), 28+i*step, -7*length, 28+i*step)

        if True:
            for i in range(0,11,2):
                num = self.m_min + i * (self.m_max - self.m_min) / 10
                val = "{:d}\xb0C".format(int(num))
                fm = painter.fontMetrics()
                size = fm.size(Qt.TextSingleLine, val)
                point = QPointF(2*OFFSET, 252-i*step+size.width()/10.0)
                
                painter.drawText(point, val)

    def setValue(self, value):
        self.value = value
        self.repaint()

    def drawTemperature(self, painter):
        color = QColor(255, 0, 0)

        scale = QLinearGradient(0.0, 0.0, 5.0, 0.0)
        bulb = QRadialGradient(0.0, 267.0, 10.0, -5.0, 262.0)

        scale.setSpread(QGradient.ReflectSpread)
        bulb.setSpread(QGradient.ReflectSpread)

        color.setHsv(color.hue(), color.saturation(), color.value())
        scale.setColorAt(1.0, color)
        bulb.setColorAt(1.0, color)

        color.setHsv(color.hue(), color.saturation()-200, color.value())
        scale.setColorAt(0.0, color)
        bulb.setColorAt(0.0, color)

        factor = self.value - self.m_min
        factor = (factor / self.m_max) - self.m_min

        # draw the "alcohol"
        temp = SCALE_HEIGHT * factor
        height = temp + OFFSET
        painter.setPen(Qt.NoPen)

        # fill the scale
        painter.setBrush(scale)
        painter.drawRect(-5, 252+OFFSET-height, 10, height)

        # fill the bulb
        painter.setBrush(bulb)
        bulb_fill_radius = BULB_RADIUS * FILL_FACTOR
        rect = QRectF(BULB_CENTER_H-bulb_fill_radius, 
                      BULB_CENTER_V-bulb_fill_radius, 
                      2*bulb_fill_radius, 2*bulb_fill_radius)
        painter.drawEllipse(rect)

class FtcGuiApplication(TxtApplication):
    def __init__(self, args):
        global txt
        
        TxtApplication.__init__(self, args)

        txt_ip = os.environ.get('TXT_IP')
        if txt_ip == None: txt_ip = "localhost"
        txt = ftrobopy.ftrobopy(txt_ip, 65000)

        # create the empty main window
        self.w = TxtWindow("Thermo")

        self.vbox = QVBoxLayout()
        
        self.the = Thermometer(self)
        self.the.setValue(0)
        self.vbox.addWidget(self.the)

        self.w.centralWidget.setLayout(self.vbox)

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_thermo)
        self.timer.start(250);

        self.w.show()

        # all outputs normal mode
        M = [ txt.C_OUTPUT, txt.C_OUTPUT, txt.C_OUTPUT, txt.C_OUTPUT ]
        I = [ (txt.C_RESISTOR,   txt.C_ANALOG ),
              (txt.C_SWITCH, txt.C_DIGITAL ),
              (txt.C_SWITCH, txt.C_DIGITAL ),
              (txt.C_SWITCH, txt.C_DIGITAL ),
              (txt.C_SWITCH, txt.C_DIGITAL ),
              (txt.C_SWITCH, txt.C_DIGITAL ),
              (txt.C_SWITCH, txt.C_DIGITAL ),
              (txt.C_SWITCH, txt.C_DIGITAL ) ]
        txt.setConfig(M, I)
        txt.updateConfig()

        self.exec_()
        
    def update_thermo(self):
        global txt
        r = txt.getCurrentInput(0)
        t = T_N * B / (B + T_N * math.log(r / R_N)) - K2C
        # limit values to thermometer graphic limit
        if t < -5: t = -5
        if t > 52: t = 52
        
        self.the.setValue(t)
        
if __name__ == "__main__":
    FtcGuiApplication(sys.argv)
