from PyQt4.QtCore import *
from PyQt4.QtGui import *

# The TXTs window title bar
class TxtTitle(QWidget):
    def __init__(self,base,str):
        QWidget.__init__(self)
        self.setObjectName("titlebar")
        self.hbox = QHBoxLayout()

        self.lbl = QLabel(str)
        self.lbl.setAlignment(Qt.AlignCenter)
        self.lbl.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Minimum)
        self.hbox.addWidget(self.lbl)

        self.close = QPushButton()
        pix = QPixmap(base + "closeicon.png")
        icn = QIcon(pix)
        but = QPushButton()
        self.close.setIcon(icn)
        self.close.setIconSize(pix.size())
        self.close.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Minimum)
        self.close.setObjectName("iconbut")
        self.close.clicked.connect(exit)
        self.hbox.addWidget(self.close)

        self.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Fixed)

        self.setLayout(self.hbox)

        self.setVisible(True)

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
        self.layout.addWidget(TxtTitle(base,str))
        self.layout.setContentsMargins(0,0,0,0)

        self.setLayout(self.layout)        

    def addWidget(self,w):
        self.layout.addWidget(w)

        # TXT windows are always fullscreen
    def show(self):
        QWidget.showFullScreen(self)

