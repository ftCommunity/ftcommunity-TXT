#! /usr/bin/env python3
# -*- coding: utf-8 -*-

from PyQt4.QtCore import QCoreApplication
from TouchStyle import *
import pty, subprocess, select, atexit, socket, struct

# name of the file used to permanently store permissions
# The file contains a list of allowed and denied mac addresses

FILE="/etc/netreq_permissions"

class PermissionsFile(QObject):
    def __init__(self):
        super(PermissionsFile,self).__init__()

        self.file_ok = True
        self.allowed = []
        self.denied = []

        # file must be writable
        if not os.access(FILE, os.W_OK):
            self.file_ok = False
            return
    
        # try to open the file
        try:
            with open(FILE, "r") as f:
                for l in f:
                    # ignore anything after '#'
                    i = l.split('#')[0].split()
                    if len(i) == 2:
                        if i[0][0].lower() == 'a':
                            self.allowed.append( i[1] )
                        if i[0][0].lower() == 'd':
                            self.denied.append( i[1] )
        except:
            self.file_ok = False

    def is_available(self):
        return self.file_ok

    def append(self, perm, dev):
        for i in self.allowed:
            if i == dev:
                return
            
        for i in self.denied:
            if i == dev:
                return
        
        with open(FILE, "a") as f:
            print(perm, dev, file=f)

        if perm == 'a':
            self.allowed.append( dev )
        if perm == 'd':
            self.denied.append( dev )

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

        self.req = req
        self.pfile = PermissionsFile()
            
        self.setObjectName("centralwidget")

        vbox = QVBoxLayout()
        vbox.addStretch()

        # title
        lbl = QLabel(QCoreApplication.translate("PluginNetReq", "Allow network connection?"))
        lbl.setWordWrap(True)
        lbl.setAlignment(Qt.AlignCenter)
        vbox.addWidget(lbl)
        vbox.addStretch()

        # button hbox
        hbox_w = QWidget()
        hbox = QHBoxLayout()
        hbox.setContentsMargins(0,0,0,0)
        allowBut = IconBut("allow")
        allowBut.clicked.connect(self.on_allow)
        hbox.addStretch()
        hbox.addWidget(allowBut)
        hbox.addStretch()
        hbox.addStretch()
        denyBut = IconBut("deny")
        denyBut.clicked.connect(self.on_deny)
        hbox.addWidget(denyBut)
        hbox.addStretch()
        hbox_w.setLayout(hbox)
        vbox.addWidget(hbox_w)

        # mac address
        lbl = QLabel(req[0])
        lbl.setObjectName("smalllabel")
        lbl.setAlignment(Qt.AlignCenter)
        vbox.addWidget(lbl)

        # try to lookup a name
        name = None
        try:
            name = socket.gethostbyaddr(req[1])[0].split('.')[0]
        except:
            # ignore any errors
            name = req[1]

        # ip address
        lbl = QLabel(name)
        lbl.setObjectName("tinylabel")
        lbl.setAlignment(Qt.AlignCenter)
        vbox.addWidget(lbl)
        vbox.addStretch()

        # if the permissions file is available then let
        # the user choose to save the setting
        self.check_save = False
        if self.pfile.is_available():
            hbox_w = QWidget()
            hbox = QHBoxLayout()
            hbox.setContentsMargins(0,0,0,0)
            self.check_save = QCheckBox(QCoreApplication.translate("PluginNetReq", "save"))
            hbox.addStretch()
            hbox.addWidget(self.check_save)
            hbox.addStretch()
            hbox_w.setLayout(hbox)
            vbox.addWidget(hbox_w)

        vbox.addStretch()        
          
        self.setLayout(vbox)        

    def on_allow(self):
        self.command.emit('a')
        if self.check_save and self.check_save.isChecked():
            self.pfile.append('a', self.req[0])
            
        self.close()

    def on_deny(self):
        self.command.emit('d')
        if self.check_save and self.check_save.isChecked():
            self.pfile.append('d', self.req[0])

        self.close()

    def exec_(self):
        QDialog.showFullScreen(self)
        QDialog.exec_(self)
    
class NetReqReceiver(QObject):
    def __init__(self):
        super(NetReqReceiver, self).__init__()

        # figure out the default gateways IP address
        # as we'd reject any connection from there
        self.default = self.get_default_gateway_linux()

        self.netreq_proc = NetReq()
        self.netreq_proc.request.connect(self.on_request)
        self.netreq_proc.start()

        # make sure we get a chance to stop the client
        # on laucnher exit
        atexit.register(self.on_atexit)

    def on_request(self, req):
        if req[1] == self.default:
            self.command.emit('d')
            return

        dialog = NetReqDialog(req)
        dialog.command.connect(self.on_command)
        dialog.exec_()

    def on_command(self, cmd):
        self.netreq_proc.input(cmd)
        
    def on_atexit(self):
        self.netreq_proc.stop()

    def get_default_gateway_linux(self):
        with open("/proc/net/route") as fh:
            for line in fh:
                fields = line.strip().split()
                if fields[1] != '00000000' or not int(fields[3], 16) & 2:
                    continue

                return socket.inet_ntoa(struct.pack("<L", int(fields[2], 16)))
        
def name():
    return QCoreApplication.translate("PluginNetReq", "NetReq")

def icon():
    return None

def status():
    return None

netreqreceiver = NetReqReceiver()

