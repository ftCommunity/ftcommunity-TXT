#! /usr/bin/env python3
# -*- coding: utf-8 -*-
#

import sys, os, shlex, io, time
from subprocess import Popen, call, PIPE, check_output, CalledProcessError
from TouchStyle import *

# only care for the built-in bluetooth adapter
DEV = "hci0"

# a seperate thread runs the tools in the background
class ExecThread(QThread):
    finished = pyqtSignal(bool,object)

    def __init__(self, cmd, silent, wait = 5):
        super(ExecThread,self).__init__()
        self.cmd = cmd
        self.silent = silent
        self.wait = wait
    
    def run(self):
        self.run_program(self.cmd)

    def result(self, ok, str):
        self.finished.emit(ok, str)

    def run_program(self, rcmd):
        """
        Runs a program, and it's paramters (e.g. rcmd="ls -lh /var/www")
        Returns output if successful, or None and logs error if not.
        """
    
        cmd = shlex.split(rcmd)
        executable = cmd[0]
        executable_options=cmd[1:]    

        try:
            if not self.silent:
                proc  = Popen(([executable] + executable_options), stdout=PIPE, stderr=PIPE)
                response = proc.communicate()
                response_stdout, response_stderr = response[0].decode('UTF-8'), response[1].decode('UTF-8')
            else:
                # we must not touch stdout/stderr when running
                # the init script as proc.communicate will wait ...
                proc  = Popen(([executable] + executable_options))
                if self.wait:
                    time.sleep(self.wait)  # artificially wait a little bit
                    # to give script some time to run before hciconfig is
                    # being called etc ....
                response = [ "", "" ]
                response_stdout = ""
                response_stderr = ""
        except OSError as e:
            if e.errno == errno.ENOENT:
                #print( "Unable to locate '%s' program. Is it in your path?" % executable )
                self.result(False, "Program not found")
            else:
                #print( "O/S error occured when trying to run '%s': \"%s\"" % (executable, str(e)) )
                self.result(False, "Exec error")
        except ValueError as e:
            #print( "Value error occured. Check your parameters." )
            self.result(False, "Value Error")
        else:
            if proc.wait() != 0:
                #print( "Executable '%s' returned with the error: \"%s\"" %(executable,response_stderr) )
                self.result(False, response)
            else:
                #print( "Executable '%s' returned successfully." %(executable) )
                #print( " First line of response was \"%s\"" %(response_stdout.split('\n')[0] ))
                self.result(True, response_stdout)

class HciConfig(ExecThread):
    def __init__(self, parm = None):
        self.parm = parm
        cmd = "hciconfig " + DEV
        if parm: cmd += " " + parm
        super(HciConfig,self).__init__(cmd, False)
    
    def result(self, ok, res):
        if not ok:
            # just return error messages
            self.finished.emit(ok, res)
            return

        # parse valid result
        result = { }

        cnt = -1
        lines = io.StringIO(res)
        for l in lines:
            l = l.strip()

            # check if line starts with "hci..."
            if l.startswith("hci"):
                cnt = 0

            if cnt == 1:
                addr = l.split()[2]
                result["bdaddr"] = addr

            # the following 2 ... are request dependent
            if self.parm == None:
                if cnt == 2:
                    if not "flags" in result:
                        result["flags"] = []

                    flags = l.lower().split()
                    for f in [ "up", "running", "pscan", "iscan" ]:
                        if f in flags:
                            result["flags"].append(f)

            if self.parm == "name":
                if cnt == 2:
                    p = l.split()
                    if p[0].lower() == "name:":
                        result["name"] = ' '.join(p[1:]).strip("'").strip('"')

            if cnt >= 0:
                cnt += 1

        self.finished.emit(True, result)

class ServiceEnable(ExecThread):
    def __init__(self, enable):
        cmd = "sudo /etc/init.d/S60bluetooth "
        if enable: cmd += "enable"
        else:      cmd += "disable"        
        super(ServiceEnable,self).__init__(cmd, True)
        
# a rotating "i am busy" widget to be shown while busy
class BusyAnimation(QWidget):
    expired = pyqtSignal()

    def __init__(self, parent=None):
        super(BusyAnimation, self).__init__(parent)

        self.resize(64, 64)
        self.move(QPoint(parent.width()/2-32, parent.height()/2-32))

        self.step = 0

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
        painter.drawEllipse(0, 0, img.width()-1, img.height()-1)
        painter.end()

        return img

    def animate(self):
        self.step += 45
        self.repaint()

    def close(self):
        self.atimer.stop()
        super(BusyAnimation, self).close()

    def paintEvent(self, event):
        radius = min(self.width(), self.height())/2 - 16
        painter = QPainter()
        painter.begin(self)

        painter.setRenderHint(QPainter.Antialiasing)

        painter.translate(self.width()/2, self.height()/2)
        painter.rotate(45)
        painter.rotate(self.step)
        painter.drawImage(0,radius, self.bright)
        for i in range(7):
            painter.rotate(45)
            painter.drawImage(0,radius, self.dark)

        painter.end()
        
class EntryWidget(QWidget):
    def __init__(self, title, parent = None):
        QWidget.__init__(self, parent)

        layout = QVBoxLayout()
        layout.setSpacing(0)
        layout.setContentsMargins(0,0,0,0)
        self.title = QLabel(title)
        layout.addWidget(self.title)        
        self.value = QLabel("")
        self.value.setObjectName("smalllabel")
        layout.addWidget(self.value)
        self.setLayout(layout)

    def setText(self, str):
        self.value.setText(str)

class FtcGuiApplication(TouchApplication):
    def __init__(self, args):
        TouchApplication.__init__(self, args)

        translator = QTranslator()
        path = os.path.dirname(os.path.realpath(__file__))
        translator.load(QLocale.system(), os.path.join(path, "bluetooth_"))
        self.installTranslator(translator)
        
        # create the empty main window
        self.w = TouchWindow(QCoreApplication.translate("FtcGuiApplication","Bluetooth"))

        menu = self.w.addMenu()
        self.menu_btrc = menu.addAction(QCoreApplication.translate("FtcGuiApplication","BT Control Set"))
        self.menu_btrc.triggered.connect(self.start_bt_remote_server)

        self.stack = QStackedWidget(self.w)
        self.main_w = QWidget()
        
        self.vbox = QVBoxLayout()
        self.vbox.setSpacing(0)

        self.vbox.addStretch()

        self.ena = QCheckBox(QCoreApplication.translate("FtcGuiApplication","enabled"))
        self.ena.setDisabled(True)
        self.vbox.addWidget(self.ena)

        self.vbox.addStretch()

        self.bdaddr = EntryWidget(QCoreApplication.translate("FtcGuiApplication","BT Address:"))
        self.vbox.addWidget(self.bdaddr)

        self.vbox.addStretch()

        self.name = EntryWidget(QCoreApplication.translate("FtcGuiApplication","Name:"))
        self.vbox.addWidget(self.name)
        
        self.vbox.addStretch()

        self.main_w.setLayout(self.vbox)
        self.stack.addWidget(self.main_w)

        # when the bt remote server is active only a simple text is being shown
        self.btrc_w = QWidget()

        self.btrc_vbox = QVBoxLayout()
        self.btrc_vbox.setSpacing(0)

        self.btrc_vbox.addStretch()

        label = QLabel(QCoreApplication.translate("BTRC", "The BT Control Set server is running."))
        label.setObjectName("smalllabel")
        label.setWordWrap(True)
        label.setAlignment(Qt.AlignCenter)
        self.btrc_vbox.addWidget(label)        
        self.btrc_vbox.addStretch()

        label = QLabel(QCoreApplication.translate("BTRC", "You can connect with the blue transmitter from the BT Control Set or with a smart phone running the BlueTooth Control app."))
        label.setObjectName("tinylabel")
        label.setWordWrap(True)
        label.setAlignment(Qt.AlignCenter)
        self.btrc_vbox.addWidget(label)        
        self.btrc_vbox.addStretch()

        label = QLabel(QCoreApplication.translate("BTRC", "Reboot your TXT to return to normal bluetooth operation."))
        label.setObjectName("tinylabel")
        label.setWordWrap(True)
        label.setAlignment(Qt.AlignCenter)
        self.btrc_vbox.addWidget(label)        
        self.btrc_vbox.addStretch()

        self.btrc_w.setLayout(self.btrc_vbox)
        self.stack.addWidget(self.btrc_w)

        self.w.setCentralWidget(self.stack)

        # check if the bt_remote_server is already running and switch gui
        # if that's the case
        self.check_for_ft_bt_remote_server()

        # get generic info first, then get name
        self.service_is_running = False  # assume no bluetooth is running
        self.hciconfig(None, self.get_name)

        self.w.show()
        self.exec_()        

    def service_enable(self, on):
        self.w.centralWidget.setGraphicsEffect(QGraphicsBlurEffect(self))
        self.w.titlebar.setGraphicsEffect(QGraphicsBlurEffect(self))
        self.busy = BusyAnimation(self.w)
        self.busy.show()
        self.ena.setDisabled(True)
        self.thread = ServiceEnable(on)
        self.thread.finished.connect(self.on_service_enable_result)
        self.thread.start()

    def on_service_enable_result(self):
        self.busy.close()
        self.w.centralWidget.setGraphicsEffect(None)
        self.w.titlebar.setGraphicsEffect(None)

        self.ena.setDisabled(False)
        
        # if service has been enabled check for the name
        if self.ena.isChecked():
            self.get_name()
        
    def on_enable_toggle(self, on):
        if self.service_is_running != on:
            self.service_is_running = on
            self.service_enable(on)

    def get_name(self):
        self.hciconfig("name")

    def hciconfig(self, parm = None, callback = None):
        self.callback = callback
        self.thread = HciConfig(parm)
        self.thread.finished.connect(self.on_hciconfig_result)
        self.thread.start()

    def on_hciconfig_result(self, ok, result):
        if not ok:
            # if hciconfig fails then the service isn't running and
            # we need to enable the check box
            self.ena.setDisabled(False)
            self.ena.toggled.connect(self.on_enable_toggle)
            return

        if "flags" in result:
            # bluetooth service is running
            self.service_is_running = "up" in result["flags"]
            self.ena.setChecked("up" in result["flags"])
            self.ena.setDisabled(False)
            self.ena.toggled.connect(self.on_enable_toggle)

        if "bdaddr" in result:
            self.bdaddr.setText(result["bdaddr"])

        if "name" in result:
            self.name.setText(result["name"])

        while self.thread.isRunning(): pass
        self.thread = None

        # read name after the flags have been read
        if self.callback:
            self.callback()

    def start_bt_remote_server(self):
        call("sudo /usr/bin/ft_bt_remote_start.sh &", shell=True)
        # disable local gui to give server some time to start
        self.ena.setDisabled(True)
        self.w.centralWidget.setGraphicsEffect(QGraphicsBlurEffect(self))
        self.w.titlebar.setGraphicsEffect(QGraphicsBlurEffect(self))
        self.busy = BusyAnimation(self.w)
        self.busy.show()
        
        self.start_timer = QTimer(self)
        self.start_timer.timeout.connect(self.on_bt_remote_server_startup)
        self.start_timer.setSingleShot(True)
        self.start_timer.start(3000)
        
    def on_bt_remote_server_startup(self):
        self.busy.close()
        self.busy = None
        self.w.centralWidget.setGraphicsEffect(None)
        self.w.titlebar.setGraphicsEffect(None)
        self.start_timer = None
        
        self.check_for_ft_bt_remote_server()

    def check_for_ft_bt_remote_server(self):
        try:
            check_output(["pidof", "ft_bt_remote_server"])
            # process exists, prevent user from starting a second one
            self.menu_btrc.setEnabled(False)
            self.stack.setCurrentWidget(self.btrc_w)
            
        except CalledProcessError:
            pass
    
if __name__ == "__main__":
    FtcGuiApplication(sys.argv)
