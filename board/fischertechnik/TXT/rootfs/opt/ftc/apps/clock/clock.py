#! /usr/bin/env python3
# -*- coding: utf-8 -*-
#
import sys, os
from TxtStyle import *

class AnalogClock(QWidget):

    # Emitted when the clock's time changes.
    timeChanged = pyqtSignal(QTime)

    # Emitted when the clock's time zone changes.
    timeZoneChanged = pyqtSignal(int)

    def __init__(self, parent=None):

        super(AnalogClock, self).__init__(parent)

        self.timeZoneOffset = 0

        timer = QTimer(self)
        timer.timeout.connect(self.update)
        timer.timeout.connect(self.updateTime)
        timer.start(1000)

        self.hourHand = QPolygon([
            QPoint(7, 8),
            QPoint(-7, 8),
            QPoint(0, -40)
        ])
        self.minuteHand = QPolygon([
            QPoint(7, 8),
            QPoint(-7, 8),
            QPoint(0, -70)
        ])

        self.hourColor = QColor(255,255,255)
        self.minuteColor = QColor(255, 255, 255, 192)

    def paintEvent(self, event):

        side = min(self.width(), self.height())
        time = QTime.currentTime()
        time = time.addSecs(self.timeZoneOffset * 3600)

        painter = QPainter()
        painter.begin(self)

        painter.setRenderHint(QPainter.Antialiasing)
        painter.translate(self.width() / 2, self.height() / 2)
        painter.scale(side / 200.0, side / 200.0)

        painter.setPen(Qt.NoPen)
        painter.setBrush(QBrush(self.hourColor))

        painter.save()
        painter.rotate(30.0 * ((time.hour() + time.minute() / 60.0)))
        painter.drawConvexPolygon(self.hourHand)
        painter.restore()

        painter.setPen(self.hourColor)

        for i in range(0, 12):
            painter.drawLine(88, 0, 96, 0)
            painter.rotate(30.0)

        painter.setPen(Qt.NoPen)
        painter.setBrush(QBrush(self.minuteColor))

        painter.save()
        painter.rotate(6.0 * (time.minute() + time.second() / 60.0))
        painter.drawConvexPolygon(self.minuteHand)
        painter.restore()

        painter.setPen(QPen(self.minuteColor))

        for j in range(0, 60):
            if (j % 5) != 0:
                painter.drawLine(92, 0, 96, 0)
            painter.rotate(6.0)

        painter.rotate(6.0 * time.second())
        painter.setPen(QPen(self.minuteColor))
        painter.drawLine(0, 0, 80, 0)

        painter.end()


    def updateTime(self):
        self.timeChanged.emit(QTime.currentTime())

    # The timeZone property is implemented using the getTimeZone() getter
    # method, the setTimeZone() setter method, and the resetTimeZone() method.

    # The getter just returns the internal time zone value.
    def getTimeZone(self):
        return self.timeZoneOffset

    # The setTimeZone() method is also defined to be a slot. The @pyqtSlot
    # decorator is used to tell PyQt which argument type the method expects,
    # and is especially useful when you want to define slots with the same
    # name that accept different argument types.

    @pyqtSlot(int)
    def setTimeZone(self, value):
        self.timeZoneOffset = value
        self.timeZoneChanged.emit(value)
        self.update()

    # Qt's property system supports properties that can be reset to their
    # original values. This method enables the timeZone property to be reset.
    def resetTimeZone(self):
        self.timeZoneOffset = 0
        self.timeZoneChanged.emit(0)
        self.update()

    # Qt-style properties are defined differently to Python's properties.
    # To declare a property, we call pyqtProperty() to specify the type and,
    # in this case, getter, setter and resetter methods.
    timeZone = pyqtProperty(int, getTimeZone, setTimeZone, resetTimeZone)

class FtcGuiApplication(TxtApplication):
    def __init__(self, args):
        TxtApplication.__init__(self, args)

        # create the empty main window
        self.w = TxtWindow("Clock")
        self.w.setCentralWidget(AnalogClock())
        self.w.show() 

        self.exec_()        
 
if __name__ == "__main__":
    FtcGuiApplication(sys.argv)
