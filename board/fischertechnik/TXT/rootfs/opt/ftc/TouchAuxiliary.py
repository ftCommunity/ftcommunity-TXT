#! /usr/bin/env python3
# -*- coding: utf-8 -*-
#
import sys, time, os, shlex
import numpy
try:
    import cv2
except:
    print("no opencv")

from subprocess import *
from TouchStyle import *
from threading import Timer
from touch_keyboard import TouchKeyboard

try:
    if TouchStyle_version<1.2:
        print("aux: TouchStyle >= v1.2 not found!")        
except:
    print("aux: TouchStyle_version not found!")
    TouchStyle_version=0


class TouchAuxMessageBox(TouchMessageBox): pass

class TouchAuxMultibutton(TouchDialog):
    """ 
        Opens up a window containing a list of items and returns the item selected by the user
        
        ******** function call **********
        msg = TouchAuxMultibutton(title:str, parent:class)
         ... some of the methods to configure
        (succes:bool, result:str) = msg.exec_()
        
        with title:str       Title of the input window
        
        ******** methods *************
        
        msg.setText(text:str)           Optional text above the button list
        msg.setButtons(items:str[])     Array of str, contains the button text ["Button one","Button two",...]
                                        Empty intermediate cells will be interpreted as a separator bar
        msg.setColumnSplit(count:int)   sets the maximum number of buttons for the first column (in landscape oriented screens)
        msg.leftAlignButtons()          Align the button Text to the left instead of center
        msg.setTextSize(size:int)       Sets the font size for the message text (1..4, 1 is smallest, default is 3)
        msg.setBtnTextSize(size:int)    Sets the font size for the button text (1..4, 1 is smallest, default is 3)
        
        ******** Return values **********
        success:bool         True for user confirmed selection, False for user aborted selection
        result:str           selected item in case of success==True or None in case of success=False
    """
    
    def __init__(self,title:str,parent=None):
        TouchDialog.__init__(self,title,parent)  
                
       
        self.result=None
        self.text=""
        self.items=["Okay"]
        self.textSize=3
        self.btnTextSize=3
        self.csplit=4
        self.leftAlign=False
        
    def setText(self,text):
        self.text=text
        
    def setButtons(self,items):
        self.items=items
           
    def setColumnSplit(self, count):
        self.csplit=count
        
    def leftAlignButtons(self):
        self.leftAlign=True
    
    def setTextSize(self,size):
        if (size>0 and size<5): self.textSize=size
        else: self.textSize=3
    
    def setBtnTextSize(self,size):
        if (size>0 and size<5): self.btnTextSize=size
        else: self.btnTextSize=3    
    
    def on_button(self):
        self.result=self.sender().text()
        self.close()
        
    def exec_(self):
        self.layout=QVBoxLayout()
        
        # orientation
        w=self.width()
        h=self.height()
        
        split=False
        if w>h: split=True  #querformat
        
        # the message
        if self.text:
            mh=QHBoxLayout()
            msg=QLabel(self.text)
            if self.textSize==4:
                msg.setObjectName("biglabel")
            elif self.textSize==3:
                msg.setObjectName("smalllabel")
            elif self.textSize==2:
                msg.setObjectName("smallerlabel")
            elif self.textSize==1:
                msg.setObjectName("tinylabel")
            msg.setWordWrap(True)
            msg.setAlignment(Qt.AlignCenter)
            mh.addWidget(msg)
            self.layout.addLayout(mh)
        
        self.layout.addStretch()
        
        if split:
            box=QHBoxLayout()
            box1=QVBoxLayout()
            box2=QVBoxLayout()
        
        c=0
        
        for b in self.items:
            k=QPushButton(b)
            if self.btnTextSize==4:
                k.setObjectName("biglabel")
            elif self.btnTextSize==3:
                k.setObjectName("smalllabel")
            elif self.btnTextSize==2:
                k.setObjectName("smallerlabel")
            elif self.btnTextSize==1:
                k.setObjectName("tinylabel")
            if self.leftAlign:
                k.setStyleSheet("Text-align:left")
            
            if b!="": k.clicked.connect(self.on_button)
            else:
                k.setEnabled(False)
                k.setDisabled(True)
                k.setMaximumHeight(6)
                
            if c<self.csplit and split:
                box1.addWidget(k)
            elif c>=self.csplit and split:
                box2.addWidget(k)
            else:
                self.layout.addWidget(k)
            c+=1
        
        if split:
            box1.addStretch()
            box2.addStretch()
            box.addLayout(box1)
            box.addLayout(box2)
            self.layout.addLayout(box)
        
        if TouchStyle_version >=1.3:
           self.setCancelButton()
        
        self.centralWidget.setLayout(self.layout) 
        TouchDialog.exec_(self)
        if self.result!=None: return True,self.result
        return False,None
      
class TouchAuxFTCamPhotoRequester(TouchDialog):
    """
        opens up a requester window to make a photo snapshot
        
        *********** function call ******************
        
        req = TouchAuxFTCamPhotoRequester(self, title:str, width:int, height:int, button:str, parent=None)
        img:QPixmap = req.exec_()
        
        title:str       title of the requester window
        width:int       width setpoint for the image 
        height:int      height setpoint for the image
        button:str      text for the "photo" button
        parent          parent class, optional, defaults to "none"
    """
        
    def __init__(self, title:str, width:int, height:int, button:str, parent=None):
        TouchDialog.__init__(self,title,parent)
        
        self.img=None
        
        #container
        
        vbox=QVBoxLayout()
        
        self.cw=TouchAuxCamWidget(width,10)
        self.cw.setPhotoSize(width,height)
        vbox.addWidget(self.cw)
        
        hb=QHBoxLayout()
        zout=QPushButton(" - ")
        zout.clicked.connect(self.on_zoom_out)
        hb.addWidget(zout)
        zin=QPushButton(" + ")
        zin.clicked.connect(self.on_zoom_in)
        #hb.addStretch()
        hb.addWidget(zin)
        
        vbox.addLayout(hb)
        
        vbox.addStretch()
        
        znap=QPushButton()
        znap.setText(button)
        znap.clicked.connect(self.on_photo)
        vbox.addWidget(znap)
        
        self.centralWidget.setLayout(vbox)
        self.titlebar.close.clicked.connect(self.cw.closeCam)
    
    def on_zoom_in(self):
        self.cw.setZoom(True)
    
    def on_zoom_out(self):
        self.cw.setZoom(False)
    
    def on_photo(self):
        self.img=self.cw.getPhoto() 
        self.cw.closeCam()
        self.close()
        
    def exec_(self):
        TouchDialog.exec_(self)
        return self.img
      
def TouchAuxFTCamIsPresent():
    CAM_DEV = os.environ.get('FTC_CAM')
    if CAM_DEV == None:
        CAM_DEV = 0
    else:
        CAM_DEV=int(CAM_DEV)
     
    # initialize camera
    try:
        cap = cv2.VideoCapture(CAM_DEV)       
        if not cap.isOpened(): return False
        else:                  return True
    except: return False
  
class TouchAuxCamWidget(QWidget):
    def __init__(self,cwidth:int=320, fps:int=10, parent=None):

        super(TouchAuxCamWidget, self).__init__(parent)
        
        self.zoom=False
        
        self.cwidth=cwidth
        
        self.pwidth=cwidth
        self.pheight=cwidth*3/4
        
        CAM_DEV = os.environ.get('FTC_CAM')
        if CAM_DEV == None:
            CAM_DEV = 0
        else:
            CAM_DEV=int(CAM_DEV)

        # initialize camera
        self.cap = cv2.VideoCapture(CAM_DEV)
        if self.cap.isOpened():
            self.cap.set(3,cwidth)
            self.cap.set(4,cwidth*3/4)
            self.cap.set(5,fps)
        
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update)
        self.timer.start(1000/fps)

        qsp = QSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)
        qsp.setHeightForWidth(True)
        self.setSizePolicy(qsp)

    def setZoom(self,zoom:bool):
        self.zoom=zoom

    def sizeHint(self):
        try:
            return QSize(self.cwidth,self.cwidth*3/4)
        except:
            return QSize(320,240)

    def heightForWidth(self,w):
        return w*3/4
    
    def closeCam(self):
        self.cap.release()    
    
    def grab(self):
        self.frame = self.cap.read()[1]

        # expand/shrink to widget size
        if self.zoom:
            wsize = (self.size().width()*2, self.size().height()*2)
            rect=QRect(self.size().width()/2,self.size().height()/2,self.size().width(), self.size().height())
        else:
            wsize = (self.size().width(), self.size().height())
            rect=QRect(0,0,self.size().width(), self.size().height())
        
        self.cvImage = cv2.resize(self.frame, wsize)

        height, width, byteValue = self.cvImage.shape
        bytes_per_line = byteValue * width

        cv2.cvtColor(self.cvImage, cv2.COLOR_BGR2RGB, self.cvImage)
        self.mQImage = QImage(self.cvImage, width, height,
                              bytes_per_line, QImage.Format_RGB888).copy(rect)
    
    def setPhotoSize(self,width,height):
        self.pwidth=width
        self.pheight=height
        
    def getPhoto(self):
        frame = self.cap.read()[1]
        
        wsize=(self.pwidth,self.pheight)
        self.frame = cv2.resize(self.frame, wsize)
        
        height, width, byteValue = frame.shape
        bytes_per_line = byteValue * width

        cv2.cvtColor(frame, cv2.COLOR_BGR2RGB, frame)
        return QImage(frame, width, height,
                      bytes_per_line, QImage.Format_RGB888)

        
    def paintEvent(self, QPaintEvent):
        painter = QPainter()
        painter.begin(self)

        if not self.cap.isOpened():
            painter.drawText(QRect(QPoint(0,0), self.size()),
                             Qt.AlignCenter, 
                             "No camera")
        else:
            self.grab()
            painter.drawImage(0,0,self.mQImage)
            
        painter.end()

class TouchAuxListRequester(TouchDialog):
    """ 
        Opens up a window containing a list of items and returns the item selected by the user
        
        ******** function call **********
        (succes:bool, result:str) = TouchAuxListRequester(title:str, items:str[], inititem:str, button:str, parent:class)
        
        ******** parameters *************
        
        title:str       Title of the input window
        items:str[]     Array of string contains the list of items to be displayed
        inititem:str    Initially selected item, will also be returned in case of cancellation 
        button:str      Text label for the confirm button, only considered for TouchStyle_version<1.3, otherwise confirm and cancel buttons will be part of the window title
        parent:class    Parent class
        
        ******** Return values **********
        success:bool         True for user confirmed selection, False for user aborted selection
        result:str           selected item in case of success==True or inititem in case of success==False
    """
    def __init__(self,title:str,message:str,items,inititem,button:str,parent=None):
        TouchDialog.__init__(self,title,parent)  
                
        self.result=""
        self.button=button
        self.confbutclicked=False
        self.inititem=inititem
        
        self.layout=QVBoxLayout()
        
        # the message
        if message:
            mh=QHBoxLayout()
            msg=QLabel(message)
            msg.setObjectName("smalllabel")
            msg.setWordWrap(True)
            msg.setAlignment(Qt.AlignCenter)
            mh.addWidget(msg)
            self.layout.addLayout(mh)
            
        # the list
        self.itemlist = QListWidget()
        self.itemlist.setVerticalScrollMode(QAbstractItemView.ScrollPerPixel)
        QScroller.grabGesture(self.itemlist.viewport(), QScroller.LeftMouseButtonGesture);
        self.itemlist.setObjectName("smalllabel")
        self.itemlist.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.itemlist.addItems(items)
        self.itemlist.currentItemChanged.connect(self.on_itemchanged)

        self.layout.addWidget(self.itemlist)
               
        # the label
        midbox = QHBoxLayout()
  
        self.actitem = QLineEdit()
        self.actitem.setReadOnly(True)
        self.actitem.setObjectName("smalllabel")
        self.actitem.setStyleSheet("color: #fcce04")
        self.actitem.setAlignment(Qt.AlignLeft)

        midbox.addWidget(self.actitem)
             
        self.layout.addLayout(midbox)
        self.itemlist.setCurrentRow(items.index(inititem))
        
        
        # the button
        but_okay = QPushButton(button)
        but_okay.setObjectName("smalllabel")
        but_okay.clicked.connect(self.on_select)
        
        if TouchStyle_version >=1.3:
           cbc=self.addConfirm()
           cbc.clicked.connect(self.on_cbc)
           self.setCancelButton()
        else:    
            self.layout.addWidget(but_okay)
        
        self.centralWidget.setLayout(self.layout)    
        
        
    def on_itemchanged(self):
        self.actitem.setText(self.itemlist.currentItem().text())
                
    def on_select(self):
        self.result = self.sender().text()
        self.close()
    
    def on_cbc(self):
        self.confbutclicked=True
    
    def exec_(self):
        TouchDialog.exec_(self)
        if self.confbutclicked==True: return True, self.itemlist.currentItem().text()
        if self.result==self.button: return True, self.itemlist.currentItem().text()
        return False, self.inititem
      

class TouchAuxRequestInteger(TouchDialog):
    """ 
        Opens up a window to get a integer number input
        
        ******** function call **********
        (succes:bool, result:int) = TouchAuxListRequester(title:str, message:str, initvalue:int, maxval:int, minval:int, button:str, parent:class)
        
        ******** parameters *************
        
        title:str       Title of the input window
        message:str     text message to be displayed
        initvalue:int   Init value for the input dial
        maxval:int      Upper limit for the input number
        minval:int      Lower limit for the inout number
        button:str      Text label for the confirm button, only considered for TouchStyle_version<1.3, otherwise confirm and cancel buttons will be part of the window title
        parent:class    Parent class
        
        ******** Return values **********
        success         True for user confirmed selection, False for user aborted selection
        result          Input value in case of success==True or initvalue in case of success==False
    """
    def __init__(self,title:str,message:str,initvalue:int,minval:int,maxval:int,button:str,parent=None):
        TouchDialog.__init__(self,title,parent)  
        
        
        self.result=""
        self.button=button
        self.initvalue=initvalue
        
        self.layout=QVBoxLayout()
        
        # the message
        if message:
            mh=QHBoxLayout()
            msg=QLabel(message)
            msg.setObjectName("smalllabel")
            msg.setWordWrap(True)
            msg.setAlignment(Qt.AlignCenter)
            mh.addWidget(msg)
            self.layout.addLayout(mh)
            
        # the dial 
        self.dial=QDial()
        self.dial.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.dial.setNotchesVisible(True)
        self.dial.setRange(minval,maxval)
        self.dial.setValue(initvalue)
        self.dial.valueChanged.connect(self.show_value)
        #db.addWidget(self.dial)
        self.layout.addWidget(self.dial)
              
        # buttons and label
        midbox = QHBoxLayout()
  
        self.bckbutt = QPushButton(" < ")
        self.bckbutt.clicked.connect(self.bckbutt_clicked)
        midbox.addWidget(self.bckbutt)
        
        midbox.addStretch()
        self.actval = QLabel()
        self.actval.setAlignment(Qt.AlignCenter)
        self.actval.setText(str(self.dial.value()))
        midbox.addWidget(self.actval)
        midbox.addStretch()
        
        self.fwdbutt = QPushButton(" > ")
        self.fwdbutt.clicked.connect(self.fwdbutt_clicked)
        midbox.addWidget(self.fwdbutt)
                
        self.layout.addLayout(midbox)
           
        
        # the button
        but_okay = QPushButton(button)
        but_okay.setObjectName("smalllabel")
        but_okay.clicked.connect(self.on_select)
        
        if TouchStyle_version >=1.3:
            confirm=self.addConfirm()
            confirm.clicked.connect(self.on_select)
            self.setCancelButton()
        else:    
            self.layout.addWidget(but_okay)
        
        self.centralWidget.setLayout(self.layout)    
        
        
    def bckbutt_clicked(self):
        self.dial.setValue(max(self.dial.minimum(),self.dial.value()-1))
    
    def fwdbutt_clicked(self):
        self.dial.setValue(min(self.dial.value()+1,self.dial.maximum()))

    def show_value(self):
        self.actval.setText(str(self.dial.value()))
                
    def on_select(self):
        self.result = self.sender().text()
        if self.result=="": self.result=self.button        
        self.close()
    
    def exec_(self):
        TouchDialog.exec_(self)

        if self.result==self.button: return True, self.dial.value()
        return False, self.initvalue
      
      

class TouchAuxRequestText(TouchDialog):
    """
        Opens up a Text input requester window
        
        ********* function call *********
        
        (success:bool, result:str) = TouchAuxRequestText(title:str, message:str, inittext:str, button:str, parent:class=None)
        
        title:str               Title of the message window
        message:str             Optional message to be shown
        inittext:str            Initial text for the input line
        button:str              text for the confirm button, only considered for TouchStyle_version<1.3
        
        
    """

    def __init__(self,title:str,message:str,inittext:str,button:str,parent=None):
        TouchDialog.__init__(self,title,parent)  
        
        
        self.result=""
        self.button=button
        self.confbutclicked=False
        self.inittext=inittext
        
        self.layout=QVBoxLayout()
        self.layout.addStretch()
        
        # the message
        msg=QLabel(message)
        msg.setWordWrap(True)
        msg.setObjectName("smalllabel")
        msg.setAlignment(Qt.AlignCenter)
        self.layout.addWidget(msg)
        self.layout.addStretch()
        
        # the text line
        self.txline=QLineEdit()
        #self.txline.setReadOnly(True)
        self.txline.setText(inittext)
        self.txline.setAlignment(Qt.AlignCenter)
        #self.txline.mousePressEvent = self.gettext
        self.layout.addWidget(self.txline)
        #self.layout.addStretch()
        
        # the button
        but_okay = QPushButton(button)
        but_okay.setObjectName("smalllabel")
        but_okay.clicked.connect(self.on_select)
        
        if TouchStyle_version >=1.3:
            cbc=self.addConfirm()
            cbc.clicked.connect(self.on_cbc)
            self.setCancelButton()
        else:    
            self.layout.addStretch()
            self.layout.addWidget(but_okay)
        
        self.centralWidget.setLayout(self.layout)    
    
    #def gettext(self,msg):
        #kbd=TouchAuxKeyboard("Input",self.txline.text(),None)
        #self.txline.setText(kbd.exec_())
    
    def on_cbc(self):
       self.confbutclicked=True
       
    def on_select(self):
        self.result = self.sender().text()
        self.close()
     
    def exec_(self):
        TouchDialog.exec_(self)
        
        if self.confbutclicked==True: return True, self.txline.text()
        if self.result==self.button: return True, self.txline.text()
        return False, self.inittext

def run_program(rcmd):
    """
    Runs a program, and it's paramters (e.g. rcmd="ls -lh /var/www")
    Returns output if successful, or None and logs error if not.
    """

    cmd = shlex.split(rcmd)
    executable = cmd[0]
    executable_options=cmd[1:]    

    try:
        proc  = Popen(([executable] + executable_options), stdout=PIPE, stderr=PIPE)
        response = proc.communicate()
        response_stdout, response_stderr = response[0].decode('UTF-8'), response[1].decode('UTF-8')
    except FileNotFoundError:
        print( "Unable to locate '%s' program. Is it in your path?" % executable )
        return ""
    except OSError as e:
        print( "O/S error occured when trying to run '%s': \"%s\"" % (executable, str(e)) )
        return ""
    except ValueError as e:
        print( "Value error occured. Check your parameters." )
        return ""
    else:
        if proc.wait() != 0:
            print( "Executable '%s' returned with the error: \"%s\"" %(executable,response_stderr) )
            return response
        else:
            print( "Executable '%s' returned successfully." %(executable) )
            print( " First line of response was \"%s\"" %(response_stdout.split('\n')[0] ))
            return response_stdout
          
class TouchAuxPicButton(QAbstractButton):
    """
        Provides an image button for PyQT Layouts
         
        button = TouchAuxPicButton(pixmap:QPixmap, parent:class=None)
        
        
    """
    def __init__(self, pixmap, parent=None):
        super(TouchAuxPicButton, self).__init__(parent)
        self.pixmap = pixmap

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.drawPixmap(event.rect(), self.pixmap)

    def sizeHint(self):
        return self.pixmap.size()
    
    def changePixmap(self,np:QPixmap):
       self.pixmap=np

class TouchAuxKeyboard(TouchKeyboard):
    def __init__(self, title, strg, parent):
        TouchKeyboard.__init__(self, parent)
        
        self.line.setText(strg)
        
        try:
            dummy = float(strg.split(";")[0])
            self.tab.setCurrentIndex(2)
        except:
            pass
        
    def exec_(self):
        TouchKeyboard.exec_(self)
        return self.text()
        

if __name__ == "__main__":
    print("This is a python3 module containing stuff for ft TXT programming based on the TouchStyle UI\n")

