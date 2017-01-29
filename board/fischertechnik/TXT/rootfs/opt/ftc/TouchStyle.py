# TouchStyle application
#
# Initially meant to implement a TXT Qt style. Now also includes
# additional functionality to communicate with the app launcher and
# the like

TouchStyle_version = 1.3

import struct, os, platform, socket
from PyQt4.QtCore import *
from PyQt4.QtGui import *

# enable special features for the Fischertechnik TXT
# The TXT can be detected by the presence of /etc/fw-ver.txt
TXT = os.path.isfile("/etc/fw-ver.txt")

if TXT:
    # TXT values
    INPUT_EVENT_DEVICE = "/dev/input/event1"
    INPUT_EVENT_CODE = 116

    INPUT_EVENT_FORMAT = 'llHHI'
    INPUT_EVENT_SIZE = struct.calcsize(INPUT_EVENT_FORMAT)

STYLE_NAME = "themes/default/style.qss"

# window size used on PC
if 'SCREEN' in os.environ:
    (w, h) = os.environ.get('SCREEN').split('x')
    WIN_WIDTH = int(w)
    WIN_HEIGHT = int(h)
else:
    WIN_WIDTH = 240
    WIN_HEIGHT = 320

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
            if type == 1 and code == INPUT_EVENT_CODE and value == 0:
                self.emit( SIGNAL('power_button_released()'))   
            event = in_file.read(INPUT_EVENT_SIZE)
        return

def TouchSetStyle(self):
    # try to find style sheet and load it
    base = os.path.dirname(os.path.realpath(__file__)) + "/"
    if os.path.isfile(base + STYLE_NAME):
        self.setStyleSheet( "file:///" + base + STYLE_NAME)
    elif os.path.isfile("/opt/ftc/" + STYLE_NAME):
        self.setStyleSheet( "file:///" + "/opt/ftc/" + STYLE_NAME)

class TouchMenu(QMenu):
    def __init__(self, parent=None):
        super(TouchMenu, self).__init__(parent)

    def on_button_clicked(self):
        pos = self.parent().mapToGlobal(QPoint(0,40))
        self.popup(pos)

# The TXTs window title bar
class TouchTitle(QLabel):
    def __init__(self,str,parent=None):
        super(TouchTitle, self).__init__(str, parent)
        self.setObjectName("titlebar")
        self.setAlignment(Qt.AlignCenter)
        self.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Fixed)
        self.close = QPushButton(self)
        self.close.setObjectName("closebut")
        self.parent=parent
        self.close.clicked.connect(parent.close)
        self.close.move(self.width()-40,self.height()/2-20)
        self.installEventFilter(self)
        self.menubut = None
        self.confbut = None

    def eventFilter(self, obj, event):
        if event.type() == event.Resize:
            self.close.move(self.width()-40,self.height()/2-20)
            if self.menubut:
                self.menubut.move(8,self.height()/2-20)
            if self.confbut:
                self.confbut.move(8,self.height()/2-20)
        return False

    def addMenu(self):
        self.menubut = QPushButton(self)
        self.menubut.setObjectName("menubut")
        self.menubut.move(8,self.height()/2-20)
        self.menu = TouchMenu(self.menubut)
        self.menubut.clicked.connect(self.menu.on_button_clicked)
        return self.menu
   
    def addConfirm(self):
        self.confbut = QPushButton(self)
        self.confbut.setObjectName("confirmbut")
        self.confbut.move(8,self.height()/2-20)
        self.confbut.clicked.connect(self.parent.close)
        return self.confbut
    
    def setCancelButton(self):
        self.close.setObjectName("cancelbut")
        
# The TXT does not use windows. Instead we just paint custom 
# toplevel windows fullscreen. This widget is closed when the 
# pwoer button is being pressed
class TouchBaseWidget(QWidget):
    def __init__(self):
        QWidget.__init__(self)
        if platform.machine() == "armv7l":
            size = QApplication.desktop().screenGeometry()
            self.setFixedSize(size.width(), size.height())
        else:
            self.setFixedSize(WIN_WIDTH, WIN_HEIGHT)

        self.setObjectName("centralwidget")

        if TXT:
            self.subdialogs = []

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

    def unregister(self,child):
        if TXT:
            self.subdialogs.remove(child)

    def register(self,child):
        if TXT:
            self.subdialogs.append(child)
        
    def close(self):
        if TXT:
            for i in self.subdialogs: i.close()

        super(TouchBaseWidget, self).close()

class TouchWindow(TouchBaseWidget):
    def __init__(self,str):
        TouchBaseWidget.__init__(self)

        # create a vertical layout and put all widgets inside
        self.layout = QVBoxLayout()
        self.titlebar = TouchTitle(str, self)
        self.layout.addWidget(self.titlebar)
        self.layout.setContentsMargins(0,0,0,0)
        self.layout.setSpacing(0)

        # add an empty widget as the centralWidget
        self.centralWidget = QWidget()
        self.layout.addWidget(self.centralWidget)

        self.setLayout(self.layout)        

    def setCentralWidget(self,w):
        # remove the old central widget and add a new one
        self.centralWidget.deleteLater()
        self.centralWidget = w
        self.layout.addWidget(self.centralWidget)

    def addMenu(self):
        return self.titlebar.addMenu()

class TouchDialog(QDialog):
    def __init__(self,title,parent):
        QDialog.__init__(self,parent)

        # for some odd reason the childern are not registered
        # as child windows on the txt

        if TXT:
            # search for a matching root parent widget
            while parent and not (parent.inherits("TouchBaseWidget") or parent.inherits("TouchDialog")):
                parent = parent.parent()

            self.parent = parent

            if parent:
                parent.register(self)
        
            self.setParent(parent)

        # the setFixedSize is only needed for testing on a desktop pc
        # the centralwidget name makes sure the themes background 
        # gradient is being used
        if platform.machine() == "armv7l":
            size = QApplication.desktop().screenGeometry()
            self.setFixedSize(size.width(), size.height())
        else:
            self.setFixedSize(WIN_WIDTH, WIN_HEIGHT)
        self.setObjectName("centralwidget")

        # create a vertical layout and put all widgets inside
        self.layout = QVBoxLayout()
        self.titlebar = TouchTitle(title, self)
        self.layout.addWidget(self.titlebar)
        self.layout.setContentsMargins(0,0,0,0)
        self.layout.setSpacing(0)

        # add an empty widget as the centralWidget
        self.centralWidget = QWidget()
        self.layout.addWidget(self.centralWidget)

        self.setLayout(self.layout)

    def updateParent(self, parent):
        if TXT:
            # search for a matching root parent widget
            while parent and not (parent.inherits("TouchBaseWidget") or parent.inherits("TouchDialog")):
                parent = parent.parent()

            self.parent = parent

            if parent:
                parent.register(self)
        
            self.setParent(parent)

    def setCentralWidget(self,w):
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
    
    def unregister(self,child):
        if TXT:
            self.parent.unregister(child)

    def register(self,child):
        if TXT:
            self.parent.register(child)

    def close(self):
        if TXT and self.parent:
            self.parent.unregister(self)

        super(TouchDialog, self).close()
        if self.sender().objectName()=="confirmbut": self.confbutclicked=True
        
        # TXT windows are always fullscreen
    def exec_(self):
        if platform.machine() == "armv7l":
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
        TouchDialog.__init__(self,title,parent)
        
        self.buttVert=True
        self.align=2
        self.textSize=3
        self.btnTextSize=3
        self.pixmap=None
        self.pmapalign=1
        self.text=""
        self.text_okay=None
        self.text_deny=None
        self.parent=parent
        
        self.result = ""
        self.confbutclicked=False
        
    def addPixmap(self, pmap: QPixmap):
        self.pixmap=pmap
    
    def setPixmapBelow(self):
        self.pmapalign=2
    
    def buttonsVertical(self,flag=True):
        self.buttVert=flag
    
    def buttonsHorizontal(self, flag=True):
        self.buttVert=not flag
        
    def setText(self,text):
        self.text=text
    
    def setPosButton(self,text):
        self.text_okay=text
    
    def setNegButton(self,text):
        self.text_deny=text
    
    def setTextSize(self,size):
        if (size>0 and size<5): self.textSize=size
        else: self.textSize=3
    
    def setBtnTextSize(self,size):
        if (size>0 and size<5): self.btnTextSize=size
        else: self.btnTextSize=3
    
    def alignTop(self):
        self.align=1
    def alignCenter(self):
        self.align=2
    def alignBottom(self):
        self.align=3
        
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
        
        if self.align>1: self.layout.addStretch()
        
        # the message is:
        
        textfield = QTextEdit(self.text)#QLabel(self.text)
        
        if self.textSize==4:
            textfield.setObjectName("biglabel")
        elif self.textSize==3:
            textfield.setObjectName("smalllabel")
        elif self.textSize==2:
            textfield.setObjectName("smallerlabel")
        elif self.textSize==1:
            textfield.setObjectName("tinylabel")

        textfield.setAlignment(Qt.AlignCenter)
        textfield.setReadOnly(True)
        self.layout.addWidget(textfield)
        
        # the pixmap ist (in case of pmapalign=1
        
        if self.pixmap and self.pmapalign==2:
            ph = QHBoxLayout()
            ph.addStretch()
            p = QLabel()
            p.setPixmap(self.pixmap)
            ph.addWidget(p)
            ph.addStretch()
            self.layout.addLayout(ph)
        
        
        # the buttons are:
        
        if not (self.text_okay==None and self.text_deny==None):
            butbox =QWidget()       
            if self.buttVert: blayou = QVBoxLayout()
            else: blayou = QHBoxLayout()
            
            butbox.setLayout(blayou)
            
            if self.buttVert: blayou.addStretch()
        
        if not self.text_okay==None:
            but_okay = QPushButton(self.text_okay)
            
            if self.btnTextSize==4:
                but_okay.setObjectName("biglabel")
            elif self.btnTextSize==3:
                but_okay.setObjectName("smalllabel")
            elif self.btnTextSize==2:
                but_okay.setObjectName("smallerlabel")
            elif self.btnTextSize==1:
                but_okay.setObjectName("tinylabel")
            
            but_okay.clicked.connect(self.on_select)
        
            blayou.addWidget(but_okay)
        
        if not self.text_deny==None:
            but_deny = QPushButton(self.text_deny)
            
            if self.btnTextSize==4:
                but_deny.setObjectName("biglabel")
            elif self.btnTextSize==3:
                but_deny.setObjectName("smalllabel")
            elif self.btnTextSize==2:
                but_deny.setObjectName("smallerlabel")
            elif self.btnTextSize==1:
                but_deny.setObjectName("tinylabel")
            
            but_deny.clicked.connect(self.on_select)
        
            blayou.addWidget(but_deny)
        
        # finalize layout
        
        if self.align<3: self.layout.addStretch()
        
        if not (self.text_okay==None and self.text_deny==None):
            self.layout.addWidget(butbox)
        
        self.centralWidget.setLayout(self.layout)
        
        # and run...
        
        TouchDialog.exec_(self)
        if self.confbutclicked==True: return True, None
        if self.text_okay==None and self.text_deny==None: return None,None
        elif self.result=="": return False,None
        else: return True,self.result
      
        
# simple on-screen-keyboard to be used on devices without physical
# keyboard attached
class TouchKeyboard(TouchDialog):
    # a pushbutton that additionally shows a second small label
    # in subscript
    class KbdButton(QPushButton):
        SUBSCRIPT_SCALE = 0.5

        def __init__(self, t, s, parent = None):
            if t == s:
                QPushButton.__init__(self, t, parent)
                self.sub = None
            else:
                QPushButton.__init__(self, t + " ", parent)
                self.sub = s

        def setText(self, t, s):
            if t == s:
                QPushButton.setText(self, t)
                self.sub = None
            else:
                QPushButton.setText(self, t + " ")
                self.sub = s

        def paintEvent(self, event):
            QPushButton.paintEvent(self, event)

            if self.sub:
                painter = QPainter()
                painter.begin(self)
                painter.setPen(QColor("#fcce04"))

                # half the normal font size
                font = painter.font()
                if font.pointSize() > 0:
                    font.setPointSize(font.pointSize() * self.SUBSCRIPT_SCALE)
                else:
                    font.setPixelSize(font.pixelSize() * self.SUBSCRIPT_SCALE)
                    
                painter.setFont(font)

                # draw the time at the very right
                painter.drawText(self.contentsRect().adjusted(0,3,-5,-3), Qt.AlignRight, self.sub)
            
                painter.end()

    # a subclassed QLineEdit that grabs focus once it has
    # been drawn for the first time
    class FocusLineEdit(QLineEdit):
        def __init__(self,parent = None):
            QLineEdit.__init__(self, parent)
            self.init = False

        def paintEvent(self, event):
            QLineEdit.paintEvent(self, event)
            if not self.init:
                self.setFocus()  # restore focus
                self.init = True

        def reset(self):
            self.init = False

    text_changed = pyqtSignal(str)

    keys_tab = [ "A-O", "P-Z", "0-9" ]
    keys_upper = [
        ["A","B","C","D","E","F","G","H","I","J","K","L","M","N","O","Aa" ],
        ["P","Q","R","S","T","U","V","W","X","Y","Z",".",","," ","_","Aa" ],
        ["=","!",'"',"§","$","%","&","/","(",")","*","_","'","°",">","Aa" ]
    ]
    keys_lower = [
        ["a","b","c","d","e","f","g","h","i","j","k","l","m","n","o","Aa" ],
        ["p","q","r","s","t","u","v","w","x","y","z",":",";","!","?","Aa" ],
        ["0","1","2","3","4","5","6","7","8","9","+","-","#","^","<","Aa" ]
    ]

    caps = False

    def __init__(self,parent = None):
        TouchDialog.__init__(self, "Input", parent)

        self.addConfirm()
        self.setCancelButton()
        
        edit = QWidget()
        edit.hbox = QHBoxLayout()
        edit.hbox.setContentsMargins(0,0,0,0)

        self.line = self.FocusLineEdit()
        self.line.setProperty("nopopup", True)
        self.line.setAlignment(Qt.AlignCenter)
        edit.hbox.addWidget(self.line)
        but = QPushButton(" ")
        but.setObjectName("osk_erase")
        but.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)
        but.clicked.connect(self.key_erase)
        edit.hbox.addWidget(but)

        edit.setLayout(edit.hbox)
        self.layout.addWidget(edit)

        self.tab = QTabWidget()

        if self.caps: 
            keys = self.keys_upper
            subs = self.keys_lower
        else:         
            keys = self.keys_lower
            subs = self.keys_upper

        for a in range(3):
            page = QWidget()
            page.grid = QGridLayout()
            page.grid.setContentsMargins(0,0,0,0)

            cnt = 0
            for cnt in range(len(keys[a])):
                if keys[a][cnt] == "Aa":
                    but = QPushButton()
                    but.setObjectName("osk_caps")
                    but.clicked.connect(self.caps_changed)
                else:
                    but = self.KbdButton(keys[a][cnt], subs[a][cnt])
                    but.clicked.connect(self.key_pressed)

                but.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding);
                page.grid.addWidget(but,cnt/4,cnt%4)

            page.setLayout(page.grid)
            self.tab.addTab(page, self.keys_tab[a])

        self.tab.tabBar().setExpanding(True);
        self.tab.tabBar().setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding);
        self.layout.addWidget(self.tab)

    def focus(self, str, cpos):
        self.line.setText(str)
        self.line.setCursorPosition(cpos)

    def key_erase(self):
        self.line.backspace()
        self.line.setFocus()  # restore focus

    def key_pressed(self):
        self.line.insert(self.sender().text()[0])
        self.line.setFocus()  # restore focus

        # user pressed the caps button. Exchange all button texts
    def caps_changed(self):
        self.line.setFocus()  # restore focus

        # default is not caps locked
        try:
            self.caps = not self.caps
        except AttributeError:
            self.caps = True

        if self.caps:  
            keys = self.keys_upper
            subs = self.keys_lower
        else:          
            keys = self.keys_lower
            subs = self.keys_upper

        # exchange all characters
        for i in range(self.tab.count()):
            gw = self.tab.widget(i)
            gl = gw.layout()
            for j in range(gl.count()):
                w = gl.itemAt(j).widget()
                if keys[i][j] != "Aa":
                    w.setText(keys[i][j], subs[i][j]);

    def close(self):
        # user has close the input dialog. Sent updated string 
        # to invoking widget
        TouchDialog.close(self)
        self.line.reset()
        if self.sender().objectName()=="confirmbut":
            self.text_changed.emit(self.line.text())

class TouchInputContext(QInputContext):
    def keyboard_present():
        # on the (non-arm) desktop always return False to force 
        # on screen keyboard
        if platform.machine() != "armv7l":
            print("Forcing on screen keyboard on non-arm device")
            return False

        try:
            for i in os.listdir("/dev/input/by-id"):
                if i[-4:] == "-kbd":
                    return True
        except:
            print("No linux USB subsystem accessible")    

        return False

    def __init__(self,parent):
        QInputContext.__init__(self,parent)
        self.keyboard = None

    def reset(self):
        pass

    def filterEvent(self, event):

        if(event.type() == QEvent.RequestSoftwareInputPanel):
            if self.focusWidget().property("nopopup"):
                print("ignoring keyboard widget itself")
                return True

            if not self.keyboard:
                self.keyboard = TouchKeyboard(self.focusWidget())
                self.keyboard.text_changed[str].connect(self.on_text_changed)
            else:
                self.keyboard.updateParent(self.focusWidget())

            text = ""
            cpos = 0
            self.widget = self.focusWidget()
            if self.widget.inherits("QLineEdit"):
                text = self.widget.text()
                cpos = self.widget.cursorPosition() 
            elif self.widget.inherits("QTextEdit"):
                text = self.widget.toPlainText()
                cpos = self.widget.textCursor().position()
            else:
                print("Unsupported widget:", self.widget)

            self.keyboard.focus(text, cpos)

            self.keyboard.show()
            return True

            # the keyboard always overlays the entire sceen.
            # Thus we don't close it via the event but from the
            # panels own close button
        elif(event.type() == QEvent.CloseSoftwareInputPanel):
            return True

        return False

    def on_text_changed(self, str):
        if self.widget.inherits("QLineEdit"):
            self.widget.setText(str)
        elif self.widget.inherits("QTextEdit"):
            self.widget.setText(str)

class TouchApplication(QApplication):
    def __init__(self, args):
        QApplication.__init__(self, args)
        if not TouchInputContext.keyboard_present():
            # disabled while not finished
            self.setInputContext(TouchInputContext(self))
            pass
        else:
            print("Physical keyboard detected")
        TouchSetStyle(self)

