from PyQt4.QtCore import *
from PyQt4.QtGui import *

# The TXTs window title bar
class TxtTitle(QLabel):
    def __init__(self,parent,base,str):
        QLabel.__init__(self,str)
        self.setObjectName("titlebar")
        self.setAlignment(Qt.AlignCenter)
        self.close = QPushButton(self)
        pix = QPixmap(base + "closeicon.png")
        icn = QIcon(pix)
        self.close.setIcon(icn)
        self.close.setIconSize(pix.size())
        self.close.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Minimum)
        self.close.setObjectName("iconbut")
        self.close.clicked.connect(parent.close)
        self.close.move(200,8)

        self.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Fixed)

# The TXT does not use windows. Instead we just paint custom 
# toplevel windows fullscreen
class TxtWindow(QWidget):
    def __init__(self,base,str):
        QWidget.__init__(self)
        # the setFixedSize is only needed for testing on a desktop pc
        # the centralwidget name makes sure the themes background 
        # gradient is being used
        self.setFixedSize(240, 320)
        self.setObjectName("centralwidget")

        # create a vertical layout and put all widgets inside
        self.layout = QVBoxLayout()
        self.layout.addWidget(TxtTitle(self,base,str))
        self.layout.setContentsMargins(0,0,0,0)

        self.setLayout(self.layout)        

    def addWidget(self,w):
        self.layout.addWidget(w)

    def addStretch(self):
        self.layout.addStretch()

        # TXT windows are always fullscreen
    def show(self):
        QWidget.showFullScreen(self)

