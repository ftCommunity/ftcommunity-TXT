import struct
from PyQt4.QtCore import *
from PyQt4.QtGui import *

# TXT values
INPUT_EVENT_DEVICE = "/dev/input/event1"
INPUT_EVENT_CODE = 116

# test on PC: F1 on (my) keyboard
#INPUT_EVENT_DEVICE = "/dev/input/event17"
#INPUT_EVENT_CODE = 59

INPUT_EVENT_FORMAT = 'llHHI'
INPUT_EVENT_SIZE = struct.calcsize(INPUT_EVENT_FORMAT)

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
    

# The TXTs window title bar
class TxtTitle(QLabel):
    def __init__(self,parent,str):
        QLabel.__init__(self,str)
        self.setObjectName("titlebar")
        self.setAlignment(Qt.AlignCenter)
        self.close = QPushButton(self)
        self.close.setObjectName("closebut")
        self.close.clicked.connect(parent.close)
        self.close.move(200,8)

        self.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Fixed)

        # start thread to monitor power button
        self.buttonThread = ButtonThread()
        self.connect( self.buttonThread, SIGNAL("power_button_released()"), parent.close )
        self.buttonThread.start()

# The TXT does not use windows. Instead we just paint custom 
# toplevel windows fullscreen
class TxtWindow(QWidget):
    def __init__(self,str):
        QWidget.__init__(self)
        # the setFixedSize is only needed for testing on a desktop pc
        # the centralwidget name makes sure the themes background 
        # gradient is being used
        self.setFixedSize(240, 320)
        self.setObjectName("centralwidget")

        # create a vertical layout and put all widgets inside
        self.layout = QVBoxLayout()
        self.layout.addWidget(TxtTitle(self,str))
        self.layout.setContentsMargins(0,0,0,0)

        self.setLayout(self.layout)        

    def addWidget(self,w):
        self.layout.addWidget(w)

    def addStretch(self):
        self.layout.addStretch()

        # TXT windows are always fullscreen
    def show(self):
        QWidget.showFullScreen(self)

