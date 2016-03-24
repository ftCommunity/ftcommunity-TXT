import struct, os, platform
from PyQt4.QtCore import *
from PyQt4.QtGui import *

# TXT values
INPUT_EVENT_DEVICE = "/dev/input/event1"
INPUT_EVENT_CODE = 116

INPUT_EVENT_FORMAT = 'llHHI'
INPUT_EVENT_SIZE = struct.calcsize(INPUT_EVENT_FORMAT)

STYLE_NAME = "themes/default/style.qss"

# background thread to monitor power button event device
class ButtonThread(QThread):
    def __init__(self):
        QThread.__init__(self)

    def __del__(self):
        self.wait()
 
    def run(self):
        in_file = open(INPUT_EVENT_DEVICE, "rb")
        event = in_file.read(INPUT_EVENT_SIZE)
        while event:
            (tv_sec, tv_usec, type, code, value) = struct.unpack(INPUT_EVENT_FORMAT, event)
            print type, code, value
            if type == 1 and code == INPUT_EVENT_CODE and value == 0:
                self.emit( SIGNAL('power_button_released()'))   
            event = in_file.read(INPUT_EVENT_SIZE)
        return

def TxtSetStyle(self):
    # try to find style sheet and load it
    base = os.path.dirname(os.path.realpath(__file__)) + "/"
    if os.path.isfile(base + STYLE_NAME):
        self.setStyleSheet( "file:///" + base + STYLE_NAME)
    elif os.path.isfile("/opt/ftc/" + STYLE_NAME):
        self.setStyleSheet( "file:///" + "/opt/ftc/" + STYLE_NAME)

# The TXTs window title bar
class TxtTitle(QLabel):
    def __init__(self,parent,str):
        QLabel.__init__(self,str)
        self.setObjectName("titlebar")
        self.setAlignment(Qt.AlignCenter)
        self.close = QPushButton(self)
        self.close.setObjectName("closebut")
        self.close.clicked.connect(parent.close)
        self.close.move(200,6)
        self.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Fixed)

# The TXT does not use windows. Instead we just paint custom 
# toplevel windows fullscreen. This widget is closed when the 
# pwoer button is being pressed
class TxtBaseWidget(QWidget):
    def __init__(self):
        QWidget.__init__(self)
        self.setFixedSize(240, 320)
        self.setObjectName("centralwidget")
    
        # on arm (TXT) start thread to monitor power button
        if platform.machine() == "armv7l":
            self.buttonThread = ButtonThread()
            self.connect( self.buttonThread, SIGNAL("power_button_released()"), self.close )
            self.buttonThread.start()

        # TXT windows are always fullscreen on arm (txt itself)
        # and windowed else (e.g. on PC)
    def show(self):
        if platform.machine() == "armv7l":
            QWidget.showFullScreen(self)
        else:
            QWidget.show(self)

class TxtWindow(TxtBaseWidget):
    def __init__(self,str):
        TxtBaseWidget.__init__(self)

        # create a vertical layout and put all widgets inside
        self.layout = QVBoxLayout()
        self.layout.addWidget(TxtTitle(self,str))
        self.layout.setContentsMargins(0,0,0,0)

        # add an empty widget as the centralWidget
        self.centralWidget = QWidget()
        self.layout.addWidget(self.centralWidget)

        self.setLayout(self.layout)        

    def setCentralWidget(self,w):
        # remove the old central widget and add a new one
        self.centralWidget.deleteLater()
        self.centralWidget = w
        self.layout.addWidget(self.centralWidget)

class TxtDialog(QDialog):
    def __init__(self,title):
        QDialog.__init__(self)
        # the setFixedSize is only needed for testing on a desktop pc
        # the centralwidget name makes sure the themes background 
        # gradient is being used
        self.setFixedSize(240, 320)
        self.setObjectName("centralwidget")

        # create a vertical layout and put all widgets inside
        self.layout = QVBoxLayout()
        self.layout.addWidget(TxtTitle(self,title))
        self.layout.setContentsMargins(0,0,0,0)

        # add an empty widget as the centralWidget
        self.centralWidget = QWidget()
        self.layout.addWidget(self.centralWidget)

        self.setLayout(self.layout)        

    def setCentralWidget(self,w):
        # remove the old central widget and add a new one
        self.centralWidget.deleteLater()
        self.centralWidget = w
        self.layout.addWidget(self.centralWidget)

        # TXT windows are always fullscreen
    def exec_(self):
        QDialog.showFullScreen(self)
        QDialog.exec_(self)


class TxtApplication(QApplication):
    def __init__(self, args):
        QApplication.__init__(self, args)
        TxtSetStyle(self)
