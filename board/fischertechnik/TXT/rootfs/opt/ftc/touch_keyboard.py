from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

from TouchStyle import TouchDialog

class TouchHandler(QObject):
    def __init__(self, parent):
        QObject.__init__(self, parent)


    def eventFilter(self, widget, event):

            if widget.inherits("FocusLineEdit"):
                return False
            
            if widget.inherits("QLineEdit"):
                
                if event.type() == QEvent.MouseButtonPress:# TouchBegin
                    text = widget.text()
                    validator = widget.validator()
                    if validator:
                        # simple heuristics as checking for QIntValidator does not seem to work
                        numbers_only = validator.validate("asd", 0)[0] != QValidator.Acceptable and \
                                       validator.validate("123", 0)[0] == QValidator.Acceptable
                    else:
                        numbers_only = False
                    
                    keyboard = TouchKeyboard(widget, numbers_only)

                    keyboard.set_text(text)
                    keyboard.exec_()
                    widget.setText(keyboard.text())
                        

            return False

        
class TouchKeyboard(TouchDialog):
    # a pushbutton that additionally shows a second small label
    # in subscript
    class KbdButton(QPushButton):
        SUBSCRIPT_FRAC = 2

        def __init__(self, t, s=None, parent=None):
            if s is None:
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
                    font.setPointSize(font.pointSize() // self.SUBSCRIPT_FRAC)
                else:
                    font.setPixelSize(font.pixelSize() // self.SUBSCRIPT_FRAC)
                    
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
        ["=","!",'"',"§","$","%","&","/","(",")","*","~","'","°",">","Aa" ]
    ]
    keys_lower = [
        ["a","b","c","d","e","f","g","h","i","j","k","l","m","n","o","Aa" ],
        ["p","q","r","s","t","u","v","w","x","y","z",":",";","!","?","Aa" ],
        ["0","1","2","3","4","5","6","7","8","9","+","-","#","^","<","Aa" ]
    ]
    keys_numeric = [ "1","2","3","4","5","6","7","8","9", "0" ]

    def __init__(self, parent = None, only_numbers = False):
        super().__init__(None, parent)

        self.caps = False

        self.layout = QVBoxLayout(self.centralWidget)

        w = self.width()
        h = self.height()

        self.line = self.FocusLineEdit()
        self.line.setProperty("nopopup", True)
        self.line.setAlignment(Qt.AlignCenter)
        self.line.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        self.layout.addWidget(self.line)
        
        edit = QWidget()
        edit.hbox = QHBoxLayout()
        edit.hbox.setContentsMargins(0, 0, 0, 0)

        but = QPushButton(" ")
        but.setObjectName("osk_erase")
        but.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Preferred)
        but.clicked.connect(self.key_erase)
        edit.hbox.addWidget(but)

        but = QPushButton(" ")
        but.setObjectName("keyboard_return")
        but.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Preferred)
        but.clicked.connect(self.close)
        edit.hbox.addWidget(but)
        
        edit.setLayout(edit.hbox)
        self.layout.addWidget(edit)

        if only_numbers:
            keys = self.keys_numeric

            page = QWidget()
            page.grid = QGridLayout()
            page.grid.setContentsMargins(0, 0, 0, 0)

            for cnt in range(len(keys)):
                but = self.KbdButton(keys[cnt])
                but.clicked.connect(self.key_pressed)

                but.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
                if w < h:
                    page.grid.addWidget(but, cnt // 3, cnt % 3)
                else:
                    page.grid.addWidget(but, cnt // 4, cnt % 4)

            page.setLayout(page.grid)

            self.layout.addWidget(page)
            
        else:
            if self.caps: 
                keys = self.keys_upper
                subs = self.keys_lower
            else:         
                keys = self.keys_lower
                subs = self.keys_upper

            self.tab = QTabWidget()
            for a in range(len(keys)):
                page = QWidget()
                page.grid = QGridLayout()
                page.grid.setContentsMargins(0, 0, 0, 0)

                for cnt in range(len(keys[a])):
                    if keys[a][cnt] == "Aa":
                        but = QPushButton(" ")
                        but.setObjectName("osk_caps")
                        but.clicked.connect(self.caps_changed)
                    else:
                        but = self.KbdButton(keys[a][cnt], subs[a][cnt])
                        but.clicked.connect(self.key_pressed)

                    but.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
                    if w < h:
                        page.grid.addWidget(but, cnt // 4, cnt % 4)
                    else:
                        page.grid.addWidget(but, cnt // 8, cnt % 8)

                page.setLayout(page.grid)
                self.tab.addTab(page, self.keys_tab[a])

            self.tab.tabBar().setExpanding(True)
            self.tab.tabBar().setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
            self.layout.addWidget(self.tab)
    
    def set_text(self, str):
        self.line.setText(str)
        self.line.setCursorPosition(len(str))

    def key_erase(self):
        self.line.backspace()
        self.line.setFocus()  # restore focus

    def key_pressed(self):
        self.line.insert(self.sender().text()[0])
        self.line.setFocus()  # restore focus

    # user pressed the caps button. Exchange all button texts
    def caps_changed(self):
        self.line.setFocus()  # restore focus

        self.caps = not self.caps
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
                    w.setText(keys[i][j], subs[i][j])

    def close(self):
        QDialog.close(self)

    def text(self):
        return self.line.text()
