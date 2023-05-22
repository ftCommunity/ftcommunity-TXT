# TouchStyle application
#
# Initially meant to implement a TXT Qt style. Now also includes
# additional functionality to communicate with the app launcher and
# the like
import os
import socket
import struct

from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

__version__ = '1.8'


TouchStyle_version = float(__version__)  # Kept for backward compatibility

# enable special features for the Fischertechnik TXT
# The TXT can be detected by the presence of /etc/fw-ver.txt
TXT = os.path.isfile("/etc/fw-ver.txt")
# TX-Pi?
TXPI = os.path.isfile('/etc/tx-pi')
# check for Fischertechnik community firmware app development settings
DEV = os.path.isfile("/etc/ft-cfw-dev.txt")


DEV_ORIENTATION = "PORTRAIT"

if DEV:
    TXT = False
    # versuche, die dev config zu lesen
    try:
        dcfile = open("/etc/ft-cfw-dev.txt", "r")
        for line in dcfile:
            if not ("#" in line):
                if "orientation" in line and "landscape" in line:
                    DEV_ORIENTATION = "LANDSCAPE"
        dcfile.close()
    except:
        pass
        
        

INPUT_EVENT_DEVICE = None

if TXT and not TXPI:  # The TX-Pi has no hardware button but is treated as TXT
    # TXT values
    INPUT_EVENT_DEVICE = "/dev/input/event1"
    INPUT_EVENT_CODE = 116
elif 'TOUCHUI_BUTTON_INPUT' in os.environ:
    (d, c) = os.environ.get('TOUCHUI_BUTTON_INPUT').split(':')
    INPUT_EVENT_DEVICE = d
    INPUT_EVENT_CODE = int(c)

INPUT_EVENT_FORMAT = 'llHHI'
INPUT_EVENT_SIZE = struct.calcsize(INPUT_EVENT_FORMAT)

STYLE_NAME = "themes/default/style.qss"




        
def getScreenSize():
    if TXT or TXPI:
        return QApplication.desktop().screenGeometry().size()

    if 'SCREEN' in os.environ:
        (w, h) = os.environ.get('SCREEN').split('x')
        return QSize(int(w), int(h))

    if DEV_ORIENTATION == "LANDSCAPE":
        return QSize(320, 240)
    
    return QSize(240, 320)
        


# background thread to monitor power button event device
class ButtonThread(QThread):
    power_button_released = pyqtSignal()
    
    def __init__(self):
        QThread.__init__(self)

    def __del__(self):
        self.wait()

    def run(self):
        in_file = open(INPUT_EVENT_DEVICE, "rb")
        event = in_file.read(INPUT_EVENT_SIZE)
        while event:
            (tv_sec, tv_usec, type, code, value) = struct.unpack(INPUT_EVENT_FORMAT, event)
            if type == 1 and code == INPUT_EVENT_CODE and value == 0:
                self.power_button_released.emit()
            event = in_file.read(INPUT_EVENT_SIZE)
        return

if INPUT_EVENT_DEVICE:
    BUTTON_THREAD = ButtonThread()
    BUTTON_THREAD.start()
else:
    BUTTON_THREAD = None


def TouchSetStyle(self):
    # try to find style sheet and load it
    base = os.path.dirname(os.path.realpath(__file__)) + "/"
    if os.path.isfile(base + STYLE_NAME):
        self.setStyleSheet("file:///" + base + STYLE_NAME)
    elif os.path.isfile("/opt/ftc/" + STYLE_NAME):
        self.setStyleSheet("file:///" + "/opt/ftc/" + STYLE_NAME)


class TouchMenu(QMenu):
    def __init__(self, parent=None):
        super(TouchMenu, self).__init__(parent)

    def on_button_clicked(self):
        pos = self.parent().mapToGlobal(QPoint(0, 40))
        self.popup(pos)


# The TXTs window title bar
class TouchTitle(QLabel):
    def __init__(self, str, parent=None):
        super(TouchTitle, self).__init__(str, parent)
        self.setObjectName("titlebar")
        self.setAlignment(Qt.AlignCenter)
        self.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Fixed)
        self.close = QPushButton(self)
        self.close.setObjectName("closebut")
        self.parent = parent
        self.close.clicked.connect(parent.close)
        self.close.move(self.width() - 40, self.height() // 2 - 20)
        self.installEventFilter(self)
        self.menubut = None
        self.confbut = None

    def eventFilter(self, obj, event):
        if event.type() == event.Resize:
            self.close.move(self.width() - 40, self.height() // 2 - 20)
            if self.menubut:
                self.menubut.move(8, self.height() // 2 - 20)
            if self.confbut:
                self.confbut.move(8, self.height() // 2 - 20)
        return False

    def addMenu(self):
        self.menubut = QPushButton(self)
        self.menubut.setObjectName("menubut")
        self.menubut.move(8, self.height() // 2 - 20)
        self.menu = TouchMenu(self.menubut)
        self.menubut.clicked.connect(self.menu.on_button_clicked)
        return self.menu

    def addConfirm(self):
        self.confbut = QPushButton(self)
        self.confbut.setObjectName("confirmbut")
        self.confbut.move(8, self.height() // 2 - 20)
        self.confbut.setDefault(True)
        self.confbut.clicked.connect(self.parent.close)
        return self.confbut
    
    def setCancelButton(self):
        self.close.setObjectName("cancelbut")


# The TXT does not use windows. Instead we just paint custom toplevel
# windows fullscreen. This widget is closed when the pwoer button is
# being pressed.
#
# To do: This class notifies the launcher which should be de-coupled.
class TouchBaseWidget(QWidget):
    def __init__(self):
        QWidget.__init__(self)
        self.setFixedSize(getScreenSize())
        self.setObjectName("centralwidget")

        if BUTTON_THREAD:
            BUTTON_THREAD.power_button_released.connect(self.close)

    # TXT windows are always fullscreen on arm (txt itself)
    # and windowed else (e.g. on PC)
    def show(self):
        if TXT or TXPI and not DEV:
            QWidget.showFullScreen(self)
        else:
            QWidget.show(self)
        # send a message to the launcher once the main widget has been
        # drawn for the first time
        self.notify_launcher()

    def notify_launcher(self):
        # send a signal so launcher knows that the app
        # is up and can stop the busy animation
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            # Connect to server and send data
            sock.connect(("localhost", 9000))
            sock.sendall(bytes("app-running {}\n".format(os.getpid()), "UTF-8"))
        except socket.error as msg:
            pass
        finally:
            sock.close()



class TouchWindow(TouchBaseWidget):
    def __init__(self,str):
        TouchBaseWidget.__init__(self)
        # create a vertical layout and put all widgets inside
        self.layout = QVBoxLayout()
        self.titlebar = TouchTitle(str, self)
        self.layout.addWidget(self.titlebar)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(0)
        # add an empty widget as the centralWidget
        self.centralWidget = QWidget()
        self.layout.addWidget(self.centralWidget)
        self.setLayout(self.layout)

    def setCentralWidget(self, w):
        # remove the old central widget and add a new one
        self.centralWidget.deleteLater()
        self.centralWidget = w
        self.layout.addWidget(self.centralWidget)

    def addMenu(self):
        return self.titlebar.addMenu()


class TouchDialog(QDialog):
    def __init__(self,title,parent):
        QDialog.__init__(self,parent)

        # the setFixedSize is only needed for testing on a desktop pc
        # the centralwidget name makes sure the themes background 
        # gradient is being used
        self.setFixedSize(getScreenSize())
        self.setObjectName("centralwidget")

        # create a vertical layout and put all widgets inside
        self.layout = QVBoxLayout()
        if title:
            self.titlebar = TouchTitle(title, self)
            self.layout.addWidget(self.titlebar)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(0)

        # add an empty widget as the centralWidget
        self.centralWidget = QWidget()
        self.layout.addWidget(self.centralWidget)
        self.setLayout(self.layout)

    def setCentralWidget(self, w):
        # remove the old central widget and add a new one
        self.centralWidget.deleteLater()
        self.centralWidget = w
        self.layout.addWidget(self.centralWidget)

    def addMenu(self):
        return self.titlebar.addMenu()

    def addConfirm(self):
        return self.titlebar.addConfirm()
    
    def setCancelButton(self):
        return self.titlebar.setCancelButton()
        
    # TXT windows are always fullscreen
    def exec_(self):
        if TXT or TXPI and not DEV:
            QWidget.showFullScreen(self)
        else:
            QWidget.show(self)
        QDialog.exec_(self)


class TouchMessageBox(TouchDialog):
    """ Versatile MessageBox for TouchUI
        
        msg = TouchMessageBox(title, parent)
        
        Methods:
        
        msg.addConfirm() adds confirm button at the left of the title
        msg.setCancelButton() changes style of the close icon to cancel icon
        
        msg.addPixmap(QPixmap) adds a QPixmap to be shown on top of the message text
        msg.setPixmapBelow() places the pixmap below the text (inbetween text and buttons), defalt is above the text
        
        msg.setText(text) sets message text, default ist empty string
        msg.setPosButton(pos_button_text) sets text for positive button, default is None (no button)
        msg.setNegButton(neg_button_text) sets text for negative button, default is None (no button)
        
        msg.setTextSize(size) set 4- big 3 - normal (default); 2 - smaller; 1 - smallest
        msg.setBtnTextSize(size)
        
        msg.alignTop() aligns message text to top of the window
        msg.alignCenter() centers text in window (default)
        msg.alignBottom() aligns message text to bottom of the window
    
        msg.buttonsVertical(bool=True) arrange buttons on top of each other (True, default) or side-by-side (False)
        msg.buttonsHorizontal(bool=True) see above...
        
        Return values:
        
        (success, text) = msg.exec_()
        success == True if one of the buttons or the confirm button was used
        success == False if MessageBox was closed by its close icon (top right)
        
        text == None if MessageBox was closed by its close icon
        text == pos_button_text | neg_button_text depending on which button was clicked
    """
    
    
    def __init__(self,title,parent):
        TouchDialog.__init__(self, title, parent)
        self.buttVert = True
        self.align = 2
        self.textSize = 3
        self.btnTextSize = 3
        self.pixmap = None
        self.pmapalign = 1
        self.text = ""
        self.text_okay = None
        self.text_deny = None
        self.confbutclicked = False
        self.confirm = None
        self.result = ""
        
    def addConfirm(self):
        self.confirm = self.titlebar.addConfirm()
        self.confirm.clicked.connect(self.on_confirm)
        
    def addPixmap(self, pmap: QPixmap):
        self.pixmap=pmap

    def setPixmapBelow(self):
        self.pmapalign = 2

    def buttonsVertical(self, flag=True):
        self.buttVert = flag

    def buttonsHorizontal(self, flag=True):
        self.buttVert = not flag

    def setText(self, text):
        self.text = text

    def setPosButton(self, text):
        self.text_okay = text

    def setNegButton(self, text):
        self.text_deny = text

    def setTextSize(self, size):
        if size > 0 and size < 5:
            self.textSize = size
        else:
            self.textSize = 3

    def setBtnTextSize(self, size):
        if size > 0 and size < 5:
            self.btnTextSize = size
        else:
            self.btnTextSize = 3

    def alignTop(self):
        self.align = 1

    def alignCenter(self):
        self.align = 2

    def alignBottom(self):
        self.align = 3

    def on_confirm(self):
        self.confbutclicked = True
        self.close()
        
    def on_select(self):
        self.result = self.sender().text()
        self.close()
     
    def exec_(self):
        self.result = ""
        self.layout = QVBoxLayout()
        
        # the pixmap ist (in case of pmapalign=1
        if self.pixmap and self.pmapalign==1:
            ph = QHBoxLayout()
            ph.addStretch()
            p = QLabel()
            p.setPixmap(self.pixmap)
            ph.addWidget(p)
            ph.addStretch()
            self.layout.addLayout(ph)
            
        # text horiontal alignment in vbox
        if self.align > 1:
            self.layout.addStretch()
        
        # the message is:
        textfield = QTextEdit(self.text)#QLabel(self.text)

        if self.textSize == 4:
            textfield.setObjectName("biglabel")
        elif self.textSize == 3:
            textfield.setObjectName("smalllabel")
        elif self.textSize == 2:
            textfield.setObjectName("smallerlabel")
        elif self.textSize == 1:
            textfield.setObjectName("tinylabel")

        textfield.setAlignment(Qt.AlignCenter)
        textfield.setReadOnly(True)
        self.layout.addWidget(textfield)
        
        # the pixmap ist (in case of pmapalign=1
        if self.pixmap and self.pmapalign == 2:
            ph = QHBoxLayout()
            ph.addStretch()
            p = QLabel()
            p.setPixmap(self.pixmap)
            ph.addWidget(p)
            ph.addStretch()
            self.layout.addLayout(ph)
        
        
        # the buttons are:
        if not (self.text_okay==None and self.text_deny==None):
            butbox = QWidget()
            if self.buttVert:
                blayou = QVBoxLayout()
            else:
                blayou = QHBoxLayout()
            butbox.setLayout(blayou)
            if self.buttVert:
                blayou.addStretch()

        if self.text_okay is not None:
            but_okay = QPushButton(self.text_okay)

            if self.btnTextSize == 4:
                but_okay.setObjectName("biglabel")
            elif self.btnTextSize == 3:
                but_okay.setObjectName("smalllabel")
            elif self.btnTextSize == 2:
                but_okay.setObjectName("smallerlabel")
            elif self.btnTextSize == 1:
                but_okay.setObjectName("tinylabel")
            
            but_okay.clicked.connect(self.on_select)
        
            blayou.addWidget(but_okay)

        if self.text_deny is not None:
            but_deny = QPushButton(self.text_deny)

            if self.btnTextSize == 4:
                but_deny.setObjectName("biglabel")
            elif self.btnTextSize == 3:
                but_deny.setObjectName("smalllabel")
            elif self.btnTextSize == 2:
                but_deny.setObjectName("smallerlabel")
            elif self.btnTextSize == 1:
                but_deny.setObjectName("tinylabel")

            but_deny.clicked.connect(self.on_select)

            blayou.addWidget(but_deny)
        
        # finalize layout
        if self.align < 3:
            self.layout.addStretch()
        
        if not (self.text_okay==None and self.text_deny==None):
            self.layout.addWidget(butbox)
        
        self.centralWidget.setLayout(self.layout)
        
        # and run...
        TouchDialog.exec_(self)
        if self.confbutclicked == True:
            return True, None
        if self.result:
            return True, self.result
        if self.confirm != None:
            return False, None
        return None, None


class TouchApplication(QApplication):
    def __init__(self, args):
        QApplication.__init__(self, args)        
        import touch_keyboard
        self.installEventFilter(touch_keyboard.TouchHandler(self))
        TouchSetStyle(self)


class BusyAnimation(QWidget):
    """Shows a busy animation on top of any application.
    """
    expired = pyqtSignal()
    BUSY_TIMEOUT = 20

    def __init__(self, app, parent=None):
        super(BusyAnimation, self).__init__(parent)
        self.resize(64, 64)
        # center relative to parent
        self.move(QPoint(parent.width() // 2 - 32, parent.height() // 2 - 32))
        self.step = 0
        self.app = app
        # create a timer to close this window after 10 seconds at most
        self.etimer = QTimer(self)
        self.etimer.setSingleShot(True)
        self.etimer.timeout.connect(self.timer_expired)
        self.etimer.start(BUSY_TIMEOUT * 1000)
        # animate at 5 frames/sec
        self.atimer = QTimer(self)
        self.atimer.timeout.connect(self.animate)
        self.atimer.start(200)
        # create small circle bitmaps for animation
        self.dark = self.draw(16, QColor("#808080"))
        self.bright = self.draw(16, QColor("#fcce04"))

    def draw(self, size, color):
        img = QImage(size, size, QImage.Format_ARGB32)
        img.fill(Qt.transparent)
        painter = QPainter(img)
        painter.setPen(Qt.white)
        painter.setRenderHint(QPainter.Antialiasing, True)
        painter.setBrush(QBrush(color))
        painter.drawEllipse(0, 0, img.width() - 1, img.height() - 1)
        painter.end()
        return img

    def timer_expired(self):
        # App launch expired without callback ...
        self.expired.emit()

    def animate(self):
        # if the app isn't running anymore then stop the
        # animation. This typically only happens for non-txt-styled
        # apps or with apps crashing.
        #
        # We might tell the user that the app ended unexpectedly
        if self.app.poll():
            self.close()
            return
        self.step += 45
        self.repaint()

    def close(self):
        self.etimer.stop()
        self.atimer.stop()
        super(BusyAnimation, self).close()
        super(BusyAnimation, self).deleteLater()

    def paintEvent(self, event):
        radius = min(self.width(), self.height()) // 2 - 16
        painter = QPainter()
        painter.begin(self)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.translate(self.width() // 2, self.height() // 2)
        painter.rotate(45)
        painter.rotate(self.step)
        painter.drawImage(0, radius, self.bright)
        for i in range(7):
            painter.rotate(45)
            painter.drawImage(0, radius, self.dark)
        painter.end()
