#! /usr/bin/env python3
# -*- coding: utf-8 -*-

from PyQt4.QtCore import QCoreApplication
from TouchStyle import *
import pty, subprocess, select, atexit

# a seperate thread runs the tools in the background
class ExecThread(QThread):
    finished = pyqtSignal(bool)
    
    def __init__(self, cmd):
        super(ExecThread,self).__init__()
        self.cmd = cmd
        
    def run(self):
        try:
            # use a pty. This enforces unbuffered output and thus
            # allows for fast update
            master_out_fd, slave_out_fd = pty.openpty()
            master_in_fd, self.slave_in_fd = pty.openpty()
            self.proc = subprocess.Popen(self.cmd, stdin=master_in_fd, stdout=slave_out_fd, stderr=slave_out_fd)
        except:
            self.finished.emit(False)
            return

        # listen to process' output
        while self.proc.poll() == None:
            try:
                if select.select([master_out_fd], [], [master_out_fd], .1)[0]:
                    output = os.read(master_out_fd, 100)
                    if output: self.output(str(output, "utf-8"))
            except InterruptedError:
                pass

        os.close(master_out_fd)
        os.close(slave_out_fd)

        os.close(master_in_fd)
        os.close(self.slave_in_fd)

        self.finished.emit(self.proc.wait() == 0)
        
    def stop(self):
        self.proc.terminate()

    def input(self, s):
        os.write(self.slave_in_fd, bytes(s, 'UTF-8'))
        
    def output(self, str):
        pass

class NetReq(ExecThread):
    request = pyqtSignal(list)

    def __init__(self):
        self.rx_buf = ""
        super(NetReq, self).__init__( [ "sudo", "/usr/bin/netreq" ] )

    def stop(self):
        if not self.proc.poll():
            # Send "q" and wait for process to end
            self.input('q')
            self.proc.wait()

    def output(self, str):
        # maintain an output buffer and search for complete strings there
        self.rx_buf += str

        lines = self.rx_buf.split('\n')
        # at least one full line?
        if len(lines) > 1:
            # keep the unterminated last line
            self.rx_buf = lines.pop()
            for l in lines:
                v = l.split()
                if v[0] == "REQ":
                    self.request.emit(v[1:])

class IconBut(QToolButton):
    def __init__(self, icon):
        QToolButton.__init__(self)

        shadow = QGraphicsDropShadowEffect(self)
        shadow.setOffset(QPointF(3,3))
        self.setGraphicsEffect(shadow)

        self.setToolButtonStyle(Qt.ToolButtonTextUnderIcon)
        pix = QPixmap(os.path.join(os.path.dirname(os.path.realpath(__file__)), icon))
        icon = QIcon(pix)
        self.setIcon(icon)
        self.setIconSize(pix.size())

        # hide shadow while icon is pressed
    def mousePressEvent(self, event):
        self.graphicsEffect().setEnabled(False)
        QToolButton.mousePressEvent(self,event)

    def mouseReleaseEvent(self, event):
        self.graphicsEffect().setEnabled(True)
        QToolButton.mouseReleaseEvent(self,event)


# a simple dialog without any decorations (and this without
# the user being able to get rid of it by himself)
class NetReqDialog(QDialog):
    command = pyqtSignal(str)
    
    def __init__(self, req):
        QDialog.__init__(self)
        if platform.machine()[0:3] == "arm":
            size = QApplication.desktop().screenGeometry()
            self.setFixedSize(size.width(), size.height())
        else:
            self.setFixedSize(WIN_WIDTH, WIN_HEIGHT)

        self.setObjectName("centralwidget")

        vbox = QVBoxLayout()
        vbox.addStretch()

        # title
        lbl = QLabel(QCoreApplication.translate("PluginNetReq", "Allow network connection?"))
        lbl.setWordWrap(True)
        lbl.setAlignment(Qt.AlignCenter)
        vbox.addWidget(lbl)
        vbox.addStretch()

        # ip address
        lbl = QLabel(req[1])
        lbl.setObjectName("smalllabel")
        lbl.setAlignment(Qt.AlignCenter)
        vbox.addWidget(lbl)
        vbox.addStretch()

        # mac address
        lbl = QLabel(req[0])
        lbl.setObjectName("tinylabel")
        lbl.setAlignment(Qt.AlignCenter)
        vbox.addWidget(lbl)
        vbox.addStretch()

        # button hbox
        hbox_w = QWidget()
        hbox = QHBoxLayout()
        allowBut = IconBut("allow")
        allowBut.clicked.connect(self.on_allow)
        hbox.addWidget(allowBut)
        denyBut = IconBut("deny")
        denyBut.clicked.connect(self.on_deny)
        hbox.addWidget(denyBut)
        hbox_w.setLayout(hbox)

        vbox.addWidget(hbox_w)
        vbox.addStretch()
        
        self.setLayout(vbox)        

    def on_allow(self):
        self.command.emit('a')
        self.close()

    def on_deny(self):
        self.command.emit('d')
        self.close()

    def exec_(self):
        QDialog.showFullScreen(self)
        QDialog.exec_(self)
    
class NetReqReceiver(QObject):
    def __init__(self):
        super(NetReqReceiver, self).__init__()

        self.netreq_proc = NetReq()
        self.netreq_proc.request.connect(self.on_request)
        self.netreq_proc.start()

        # make sure we get a chance to stop the client
        # on laucnher exit
        atexit.register(self.on_atexit)
    
    def on_request(self, req):
        dialog = NetReqDialog(req)
        dialog.command.connect(self.on_command)
        dialog.exec_()

    def on_command(self, cmd):
        self.netreq_proc.input(cmd)
        
    def on_atexit(self):
        self.netreq_proc.stop()

def name():
    return QCoreApplication.translate("PluginNetReq", "NetReq")

def icon():
    # create icon from png: convert x.png -monochrome x.xpm
    icon_data = [ "16 16 2 1 ", "  c None", ". c white",
                  "                ",
                  "      ....      ",
                  "      ....      ",
                  "      ..        ",
                  "      ..        ",
                  "      ..        ",
                  "      ..        ",
                  "      ..        ",
                  "     ....       ",
                  "    ......      ",
                  "   ..    ..     ",
                  "   ..    ..     ",
                  "   ..    ..     ",
                  "    ......      ",
                  "     ....        ",
                  "                " ]    
    
    # device present but no link: draw darkgrey
    # icon_data[2] = ". c #606060"
    #return None
    return icon_data

def status():
    return QCoreApplication.translate("PluginNetReq", "")

netreqreceiver = NetReqReceiver()

