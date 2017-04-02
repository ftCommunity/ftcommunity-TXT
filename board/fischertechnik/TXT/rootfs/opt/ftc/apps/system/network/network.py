#! /usr/bin/env python3
# -*- coding: utf-8 -*-
#

import sys, os, socket, array, struct, fcntl, string, platform
import shlex, time, copy
from subprocess import Popen, call, PIPE
from TouchStyle import *
from launcher import LauncherPlugin

DEFAULT="wlan0"
INTERFACES = "/etc/network/interfaces"

# For testing on PC: environment may point to buildroot
if 'TOUCHUI_FAKEROOT' in os.environ:
    INTERFACES = os.environ.get('TOUCHUI_FAKEROOT') + INTERFACES

SIOCGIFCONF    = 0x8912
SIOCGIFADDR    = 0x8915
SIOCGIFNETMASK = 0x891b

def _ifinfo(sock, addr, ifname):
    iface = struct.pack('256s', bytes(ifname[:15], "UTF-8"))
    info  = fcntl.ioctl(sock.fileno(), addr, iface)
    return socket.inet_ntoa(info[20:24])

def all_interfaces():
    if platform.machine() == "armv7l": size = 32
    else:                              size = 40
    
    bytes = 8 * size
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    names = array.array('B', b'\x00' * bytes)
    outbytes = struct.unpack('iL', fcntl.ioctl(
        s.fileno(), SIOCGIFCONF,
        struct.pack('iL', bytes, names.buffer_info()[0])
    ))[0]
    namestr = names.tostring()

    # get additional info for all interfaces found
    lst = { }
    for i in range(0, outbytes, size):
        name = namestr[i:i+16].decode('UTF-8').split('\0', 1)[0]
        if name != "" and not name in lst:
            addr = _ifinfo(s, SIOCGIFADDR, name)
            mask = _ifinfo(s, SIOCGIFNETMASK, name)
            lst[name] = (addr, mask)
    return lst

# execute ifconfig up/down, trigger dhcpcd if required
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
    except OSError as e:
        if e.errno == errno.ENOENT:
            print( "Unable to locate '%s' program. Is it in your path?" % executable )
        else:
            print( "O/S error occured when trying to run '%s': \"%s\"" % (executable, str(e)) )
    except ValueError as e:
        print( "Value error occured. Check your parameters." )
    else:
        if proc.wait() != 0:
            print( "Executable '%s' returned with the error: \"%s\"" %(executable,response_stderr) )
            return response
        else:
            print( "Executable '%s' returned successfully." %(executable) )
            print( " First line of response was \"%s\"" %(response_stdout.split('\n')[0] ))
            return response_stdout

def check4dhcp(_iface):
    pids = [pid for pid in os.listdir('/proc') if pid.isdigit()]
    for pid in pids:
        try:
            cmds = open(os.path.join('/proc', pid, 'cmdline'), 'rt').read().split('\0')
            if cmds[0] == "udhcpc" and _iface in cmds:
                return True

        except IOError: # proc has already terminated
            continue
    return False

def run_dhcp(_iface, on):
    pidfilename = "/var/run/udhcpc." + _iface + ".pid"
    cmd = "udhcpc -R -n -p " + pidfilename + " -i " + _iface

    # ask udhcpc to obtain a fresh address if it's already runnung. Start it otherwise
    if check4dhcp(_iface):
        if on:
            # request new lease
            run_program("sudo pkill -SIGUSR1 -f \"" + cmd + "\"")
        else:
            # stop udhcdp
            run_program("sudo pkill -SIGTERM -f \"" + cmd + "\"")
    else:
        if on:
            # start udhcp
            run_program("sudo " + cmd)

def set_config(iface, cfg):
    print("set config for iface", iface)

    # start/stop dhcp according to new config
    dhcp_on = cfg["options"]["method"] == "dhcp"
    run_dhcp(iface, dhcp_on)

    # use ifconfig if no dhcp is configured
    if not dhcp_on:
        # assemble the ifconfig call
        cmd = "ifconfig " + iface

        if "address" in cfg["parms"]:
            cmd += " " + cfg["parms"]["address"]        
        if "netmask" in cfg["parms"]:
            cmd += " netmask " + cfg["parms"]["netmask"]
        if "broadcast" in cfg["parms"]:
            cmd += " broadcast " + cfg["parms"]["broadcast"]
        cmd += " up"

        run_program("sudo " + cmd)
            
        # self.interfaces[iface]["parms"].pop("gateway", None)
        if "gateway" in cfg["parms"]:
            cmd = "route add default gw " + cfg["parms"]["gateway"] + " " + iface
            run_program("sudo " + cmd)
            

# deal with /etc/network/interfaces
class Interfaces(QObject):
    error = pyqtSignal(str)

    def __init__(self, parent = None):
        QObject.__init__(self, parent)
        self.parse(INTERFACES)
        self.modified = False

    def write(self):
        if self.modified:
            self.cleanup()

            # write header
            try:
                f = open(INTERFACES, 'w')

                # print file header
                print("# /etc/network/interfaces", file=f)
                print("# generated by", os.path.basename(__file__), file=f)
                print("", file=f)

                # print auto list
                for i in self.ifs_auto:
                    print("auto", i, file=f)
                print("", file=f)

                # print interfaces
                for i in self.interfaces:
                    # print iface line with options
                    print("iface", i ,end="", file=f)
                    options = self.interfaces[i]["options"]
                    for m in [ "inet", "method" ]:
                        print(" "+options[m], end="", file=f)
                    print("", file=f)

                    # print parameter lines
                    parms = self.interfaces[i]["parms"]
                    for p in parms:
                        print("\t"+p+" "+parms[p], file=f)

                    print("", file=f)

                f.close()
            except IOError as e:
                self.error.emit(e.strerror)

    def cleanup(self):
        # clean the interfaces up a little bit
        for iface in self.interfaces:
            # check if modified flag is set. leave untouched otherwise
            if "modified" in self.interfaces[iface] and self.interfaces[iface]["modified"]:
                if self.interfaces[iface]["options"]["method"] == "dhcp":
                    # when dhcp is used no address/netmask/gateway/broadcast
                    # should be set
                    self.interfaces[iface]["parms"].pop("address", None)
                    self.interfaces[iface]["parms"].pop("netmask", None)
                    self.interfaces[iface]["parms"].pop("gateway", None)
                    self.interfaces[iface]["parms"].pop("broadcast", None)
                else:
                    # derive broadcast if address and netmask are given
                    if ( "address" in self.interfaces[iface]["parms"] and 
                         "netmask" in self.interfaces[iface]["parms"] ):
                        bc = [ 0,0,0,0 ]
                        ad = self.interfaces[iface]["parms"]["address"].split('.')
                        nm = self.interfaces[iface]["parms"]["netmask"].split('.')
                        for i in range(4):
                            adv = int(ad[i])
                            nmv = int(nm[i])
                            bc[i] = str((adv & nmv) | (255 & ~nmv))
                        self.interfaces[iface]["parms"]["broadcast"] = ".".join(bc)

    def set(self, name, iface):
        self.interfaces[name] = iface
        self.interfaces[name]["modified"] = True
        self.modified = True

    def parse_indented_line(self, l):
        if self.iface:
            name = l.split()[0]
            parms = l[len(name):].strip()
            self.iface["parms"][name] = parms

    def parse_iface(self, l):
        # iface lo inet loopback
        if len(l) != 3:
            print("unexpected number of iface parameters", len(l))
            self.err = False
            return None
        else:
            iface_options = { }
            iface_options["inet"] = l[1]
            iface_options["method"] = l[2]

            iface = { }
            iface["name"] = l[0]
            iface["options"] = iface_options
            iface["parms"] = { }

            return iface

    def parse_non_indented_line(self, l):
        cmd = l.split()[0].lower()
        if cmd == "auto":
            self.ifs_auto.append(l.split()[1])
        elif cmd == "iface":
            # append any previous interface to list
            if self.iface:
                self.interfaces[self.iface["name"]] = self.iface
            self.iface = self.parse_iface(l.split()[1:])
        else:
            print("unpected entry", cmd)
            self.err = False

    def parse_line(self, l):
        if l[0].isspace():
            self.parse_indented_line(l.strip())
        else:
            self.parse_non_indented_line(l.strip())

    def parse(self, fname):
        self.ifs_auto = [ ]
        self.iface = None
        self.interfaces = { }
        self.err = False

        with open(fname, "r") as f:
            for l in f:
                # remove any comments
                l = l.split('#')[0].rstrip()
                if l != "":
                    self.parse_line(l)

        # append last interface found
        if self.iface:
            self.interfaces[self.iface["name"]] = self.iface

    def ifs(self):
        return self.interfaces

# QPushButton with a slightly smaller font
class SmallButton(QPushButton):
    def __init__(self, str, parent = None):
        QPushButton.__init__(self, str, parent)
        style = "QPushButton { font: 24px; }"
        self.setStyleSheet(style)

class SmallLabel(QLabel):
    def __init__(self, str, parent = None):
        QLabel.__init__(self, str, parent)
        self.setObjectName("smalllabel")
        self.setAlignment(Qt.AlignCenter)

class SmallHighlightLabel(SmallLabel):
    clicked = pyqtSignal(int)

    def __init__(self, index, value, on, parent = None):
        if value[index] != None: s = str(value[index])
        else:                    s = "___"

        SmallLabel.__init__(self, s, parent)
        self.index = index
        self.highlight(on)

    def mousePressEvent(self, event):
        self.clicked.emit(self.index)

    def set(self, s):
        if s != None: self.setText(str(s))
        else:         self.setText("___")

    def highlight(self, on):
        if on:
            self.setStyleSheet("QLabel { background-color : #fcce04; color : white; }")
        else:
            self.setStyleSheet(None)

# a simple dialog to edit an ip address
class IpEdit(TouchDialog):
    address = pyqtSignal(str)

    def __init__(self, str, value, parent = None):
        TouchDialog.__init__(self, str, parent)
        self.addConfirm()
        self.setCancelButton()

        self.value =  [ ]
        self.state = False
        self.index = 0

        # check if this really is something like an ip
        # address
        if value and len(value.split('.')) == 4:
            parts = value.split('.')
            for i in range(4):
                self.value.append(int(parts[i]))
        else:
            for i in range(4):
                self.value.append(None)

        vbox = QVBoxLayout()
        vbox.setContentsMargins(0,0,0,0)

        vbox.addStretch()

        # a hbox containing the parts of the ip address
        hbox_w = QWidget()
        hbox = QHBoxLayout()
        hbox.setContentsMargins(0,0,0,0)
        hbox.setSpacing(0)
        hbox.addStretch()

        self.ip = [ ]
        self.ip.append(SmallHighlightLabel(0, self.value, True, self))
        self.ip[0].clicked.connect(self.ip_clicked)
        hbox.addWidget(self.ip[0])
        hbox.addWidget(SmallLabel("."))
        self.ip.append(SmallHighlightLabel(1, self.value, False, self))
        self.ip[1].clicked.connect(self.ip_clicked)
        hbox.addWidget(self.ip[1])
        hbox.addWidget(SmallLabel("."))
        self.ip.append(SmallHighlightLabel(2, self.value, False, self))
        self.ip[2].clicked.connect(self.ip_clicked)
        hbox.addWidget(self.ip[2])
        hbox.addWidget(SmallLabel("."))
        self.ip.append(SmallHighlightLabel(3, self.value, False, self))
        self.ip[3].clicked.connect(self.ip_clicked)
        hbox.addWidget(self.ip[3])
        hbox_w.setLayout(hbox)
        
        hbox.addStretch()
        vbox.addWidget(hbox_w)

        vbox.addStretch()

        # add number grid
        buttons = [ "0", "1", "2", "3", 
                    "4", "5", "6", "7", 
                    "8", "9", "<", "." ]
        grid_w = QWidget()
        grid = QGridLayout()
        cnt = 0
        for i in buttons:
            btn = QPushButton(i)
            btn.clicked.connect(self.btn_clicked)
            grid.addWidget(btn, cnt/4, cnt%4) 
            cnt += 1

        grid_w.setLayout(grid)
        vbox.addWidget(grid_w)
        vbox.addStretch()

        self.centralWidget.setLayout(vbox)
        self.show() 

    def close(self):
        TouchDialog.close(self)

        if self.sender().objectName()=="confirmbut":
            # check of value is a complete ip
            if ( self.value[0] != None and self.value[1] != None and 
                 self.value[2] != None and self.value[3] != None):
                self.address.emit(str(self.value[0])+"."+str(self.value[1])+"."+
                                  str(self.value[2])+"."+str(self.value[3]))
            else:
                self.address.emit(None)

    def btn_clicked(self):
        val = self.sender().text()

        if val == ".":
            if self.index < 3:
                self.ip_clicked(self.index + 1)
        elif val == "<":
            if self.value[self.index]:
                self.value[self.index] = int(self.value[self.index] / 10)
            elif self.value[self.index] == 0:
                self.value[self.index] = None

            self.ip[self.index].set(self.value[self.index])
        else:
            # process edit state
            if not self.state:
                self.value[self.index] = int(val)
                self.ip[self.index].setText(str(self.value[self.index]))
                self.state = True
            else:
                val = self.value[self.index] * 10 + int(val)
                if val < 256:
                    self.value[self.index] = val
                    self.ip[self.index].set(self.value[self.index])
                    if val > 25 and self.index < 3:
                        self.ip_clicked(self.index + 1)

    def ip_clicked(self, index):
        self.state = False
        self.index = index
        for i in range(4):
            self.ip[i].highlight(i == index)


# a widget for displaying and entering an ipv4 address
class IpWidget(QWidget):
    iface_changed = pyqtSignal(object)

    def __init__(self, title, iface, value_name, parent = None):
        QWidget.__init__(self, parent)
        
        self.value = None
        self.iface = iface
        self.value_name = value_name
        if value_name in iface["parms"]:
            self.value = iface["parms"][value_name]

        vbox = QVBoxLayout()
        vbox.setContentsMargins(0,0,0,0)
        vbox.setSpacing(00)

        self.lbl = SmallLabel(title)
        vbox.addWidget(self.lbl)

        if self.value:
            self.ip_but = SmallButton(self.value)
        else:
            self.ip_but = SmallButton("___.___.___.___")

        self.ip_but.clicked.connect(self.on_click)
        vbox.addWidget(self.ip_but)
        self.setLayout(vbox)

    def on_click(self):
        dialog = IpEdit(self.lbl.text(), self.value, self)
        dialog.address.connect(self.on_new_address)
        dialog.exec_()

    def on_new_address(self, str):
        if str:
            # use a valid new address
            self.value = str
            self.ip_but.setText(str)
            self.iface["parms"][self.value_name] = str
        else:
            # forget about address as it's not valid
            self.value = None
            self.ip_but.setText("___.___.___.___")
            self.iface["parms"].pop(self.value_name, None)

        # notify edit dialog about updated address
        self.iface_changed.emit(self.iface)
    
class EditDialog(TouchDialog):
    iface_changed = pyqtSignal(object)

    def __init__(self,ifname, iface, parent):
        TouchDialog.__init__(self, ifname, parent)
        self.addConfirm()
        self.setCancelButton()

        self.iface_has_been_changed = False
        self.iface = copy.deepcopy(iface)

        self.vbox = QVBoxLayout()

        dhcp = QCheckBox(QCoreApplication.translate("Main", "automatic"))
        dhcp.setChecked(self.iface["options"]["method"] == "dhcp")
        dhcp.toggled.connect(self.on_dhcp_toggle)
        self.vbox.addWidget(dhcp)

        self.vbox.addStretch()

        self.ip = IpWidget(QCoreApplication.translate("Main", "Address"), self.iface, "address", self)
        self.ip.iface_changed.connect(self.on_iface_changed)
        self.vbox.addWidget(self.ip)

        self.vbox.addStretch()

        self.nm = IpWidget(QCoreApplication.translate("Main", "Netmask"), self.iface, "netmask", self)
        self.nm.iface_changed.connect(self.on_iface_changed)
        self.vbox.addWidget(self.nm)

        self.vbox.addStretch()

        self.gw = IpWidget(QCoreApplication.translate("Main", "Gateway"), self.iface, "gateway", self)
        self.gw.iface_changed.connect(self.on_iface_changed)
        self.vbox.addWidget(self.gw)

        self.on_dhcp_toggle(dhcp.isChecked())

        self.centralWidget.setLayout(self.vbox)
        self.show() 

    def on_iface_changed(self, iface):
        self.iface_has_been_changed = True
        self.iface = iface

    def on_dhcp_toggle(self, on):
        if on:
            self.iface["options"]["method"] = "dhcp"
        else:
            self.iface["options"]["method"] = "static"

        self.ip.setDisabled(on)
        self.nm.setDisabled(on)
        self.gw.setDisabled(on)
        self.iface_has_been_changed = True

    def close(self):
        if self.iface_has_been_changed:
            if self.sender().objectName()=="confirmbut":
                self.iface_changed.emit(self.iface)

        TouchDialog.close(self)

class NetworkWindow(TouchWindow):
    def __init__(self):
        TouchWindow.__init__(self, QCoreApplication.translate("Main", "Network"))
        
        self.interfaces_file = Interfaces()    # get interfaces from config file
        self.ifs = all_interfaces()            # get interfaces from system

        # add unconfigured interfaces missing from the system and set ip/netmask to "---"
        for i in self.interfaces_file.ifs():
            if not i in self.ifs:
                self.ifs[i] = ("---", "---")

        names = sorted(list(self.ifs.keys()))

        self.vbox = QVBoxLayout()

        self.nets_w = QComboBox()
        self.nets_w.activated[str].connect(self.set_net)
        for i in names:
            self.nets_w.addItem(i)

        self.vbox.addWidget(self.nets_w)

        self.vbox.addStretch()

        self.ip_lbl = QLabel(QCoreApplication.translate("Main", "Address")+":")
        self.ip_lbl.setAlignment(Qt.AlignCenter)
        self.vbox.addWidget(self.ip_lbl)

        self.ip = QLabel("")
        self.ip.setObjectName("smalllabel")
        self.ip.setAlignment(Qt.AlignCenter)
        self.vbox.addWidget(self.ip)
   
        self.mask_lbl = QLabel(QCoreApplication.translate("Main", "Netmask")+":")
        self.mask_lbl.setAlignment(Qt.AlignCenter)
        self.vbox.addWidget(self.mask_lbl)

        self.mask = QLabel("")
        self.mask.setObjectName("smalllabel")
        self.mask.setAlignment(Qt.AlignCenter)
        self.vbox.addWidget(self.mask)

        self.vbox.addStretch()

        self.edit_btn = QPushButton(QCoreApplication.translate("Main", "Edit..."))
        self.edit_btn.setDisabled(True)
        self.edit_btn.clicked.connect(self.on_edit)
        self.vbox.addWidget(self.edit_btn)
        
        self.centralWidget.setLayout(self.vbox)

        # select wlan0 if in list
        if DEFAULT in names:
            self.nets_w.setCurrentIndex(names.index(DEFAULT))
            self.set_net(DEFAULT)
        else:
            self.set_net(names[0])
   
    def on_edit(self):
        name = self.nets_w.currentText()
        if name in self.interfaces_file.ifs():
            dialog = EditDialog(name, self.interfaces_file.ifs()[name], self)
            dialog.iface_changed.connect(self.on_iface_changed)
            dialog.exec_()
 
    def on_iface_changed(self, iface):
        name = self.nets_w.currentText()
        self.interfaces_file.set(name, iface)

    def set_net(self,name):
        interface = self.ifs[name]
        self.ip.setText(interface[0])
        self.mask.setText(interface[1])

        # has this device an entry in the config file? Only then allow to edit
        # it. Also don't edit the loopback device
        if name in self.interfaces_file.ifs() and name != "lo":
            self.edit_btn.setEnabled(True)
        else:
            self.edit_btn.setDisabled(True)

    def update_interfaces(self):
        # update interfaces according to their new configuration
        for iface in self.interfaces_file.ifs():
            # check if modified flag is set. leave untouched otherwise
            if "modified" in self.interfaces_file.ifs()[iface] and self.interfaces_file.ifs()[iface]["modified"]:
                set_config(iface, self.interfaces_file.ifs()[iface])

    def close(self):
        self.interfaces_file.error.connect(self.file_error)
        self.interfaces_file.write()
        self.update_interfaces()
        TouchWindow.close(self)

    def file_error(self, str):
        dialog = TouchDialog(QCoreApplication.translate("Main", "Error"), self)
        
        vbox = QVBoxLayout()
        vbox.addStretch()
        err = QLabel(QCoreApplication.translate("Main", "File Error"))
        err.setAlignment(Qt.AlignCenter)
        vbox.addWidget(err)
        lbl = QLabel(str)
        lbl.setObjectName("smalllabel")
        lbl.setWordWrap(True)
        lbl.setAlignment(Qt.AlignCenter)
        
        vbox.addWidget(lbl)
        vbox.addStretch()
        dialog.centralWidget.setLayout(vbox)
        dialog.exec_()

class FtcGuiPlugin(LauncherPlugin):
    def __init__(self, application):
        LauncherPlugin.__init__(self, application)

        translator = QTranslator()
        path = os.path.dirname(os.path.realpath(__file__))
        translator.load(QLocale.system(), os.path.join(path, "network_"))
        self.installTranslator(translator)

        self.w = NetworkWindow()
        self.w.show() 

if __name__ == "__main__":
    class FtcGuiApplication(TouchApplication):
        def __init__(self, args):
            super().__init__(args)
            module = FtcGuiPlugin(self)
            self.exec_()
    FtcGuiApplication(sys.argv)
else:
    def createPlugin(launcher):
        return FtcGuiPlugin(launcher)

