#! /usr/bin/env python3
# -*- coding: utf-8 -*-
#

# assume wpa has been started e.g. by
# sudo wpa_supplicant -B -Dwext -i wlan0 -C/var/run/wpa_supplicant

import sys, os, shlex, time
from subprocess import Popen, call, PIPE
from TxtStyle import *

local = os.path.dirname(os.path.realpath(__file__)) + "/"

IFACE = "wlan0"

connected_ssid = ""

key = ""

encr = [ "OPEN", "WEP", "WPA", "WPA2" ];

keys_tab = [ "A-O", "P-Z", "0-9" ]
keys_upper = [
    ["A","B","C","D","E","F","G","H","I","J","K","L","M","N","O","Aa" ],
    ["P","Q","R","S","T","U","V","W","X","Y","Z",".",","," ","_","Aa" ],
    ["0","1","2","3","4","5","6","7","8","9","+","-","*","/","#","$" ]
]
keys_lower = [
    ["a","b","c","d","e","f","g","h","i","j","k","l","m","n","o","Aa" ],
    ["p","q","r","s","t","u","v","w","x","y","z",":",";","!","?","Aa" ],
    ["0","1","2","3","4","5","6","7","8","9","+","-","*","/","#","$" ]
]

caps = True

def run_program(rcmd):
    """
    Runs a program, and it's paramters (e.g. rcmd="ls -lh /var/www")
    Returns output if successful, or None and logs error if not.
    """

    cmd = shlex.split(rcmd)
    executable = cmd[0]
    executable_options=cmd[1:]    

    print(("run: ", rcmd))

    try:
        proc  = Popen(([executable] + executable_options), stdout=PIPE, stderr=PIPE)
        response = proc.communicate()
        response_stdout, response_stderr = response[0].decode('UTF-8'), response[1].decode('UTF-8')
    except OSError as e:
        if e.errno == errno.ENOENT:
            print(( "Unable to locate '%s' program. Is it in your path?" % executable ))
        else:
            print(( "O/S error occured when trying to run '%s': \"%s\"" % (executable, str(e)) ))
    except ValueError as e:
        print( "Value error occured. Check your parameters." )
    else:
        if proc.wait() != 0:
            print(( "Executable '%s' returned with the error: \"%s\"" %(executable,response_stderr) ))
            return response
        else:
            print(( "Executable '%s' returned successfully." %(executable) ))
            print(( " First line of response was \"%s\"" %(response_stdout.split('\n')[0] )))
            return response_stdout

def get_networks(iface, retry=10):
    """
    Grab a list of wireless networks within range, and return a list of dicts describing them.
    """
    while retry > 0:
        if "OK" in run_program("sudo wpa_cli -i %s scan" % iface):
            networks=[]
            r = run_program("sudo wpa_cli -i %s scan_result" % iface).strip()
            if "bssid" in r and len ( r.split("\n") ) >1 :
                for line in r.split("\n")[1:]:
                    b, fr, s, f = line.split()[:4]
                    ss = " ".join(line.split()[4:]) #Hmm, dirty
                    networks.append( {"bssid":b, "freq":fr, "sig":s, "ssid":ss, "flag":f} )
                return networks
        retry-=1
        print("Couldn't retrieve networks, retrying")
        time.sleep(0.5)
    print("Failed to list networks")

def connect_to_network(_iface, _ssid, _type, _pass=None):
    """
    Associate to a wireless network. Support _type options:
    *WPA[2], WEP, OPEN
    """
    _disconnect_all(_iface)
    time.sleep(1)
    if run_program("sudo wpa_cli -i %s add_network" % _iface) == "0\n":
        if run_program('sudo wpa_cli -i %s set_network 0 ssid \'"%s"\'' % (_iface,_ssid)) == "OK\n":
            if _type == "OPEN":
                run_program("sudo wpa_cli -i %s set_network 0 auth_alg OPEN" % _iface)
                run_program("sudo wpa_cli -i %s set_network 0 key_mgmt NONE" % _iface)
            elif _type == "WPA" or _type == "WPA2":
                run_program('sudo wpa_cli -i %s set_network 0 psk \'"%s"\'' % (_iface,_pass))
            elif _type == "WEP":
                run_program("sudo wpa_cli -i %s set_network 0 wep_key %s" % (_iface,_pass))
            else:
                print("Unsupported type")
            
            run_program("sudo wpa_cli -i %s select_network 0" % _iface)

def save_config(_iface):
    run_program("sudo wpa_cli -i %s save_config" % _iface)

def check4dhcp(_iface):
    pids = [pid for pid in os.listdir('/proc') if pid.isdigit()]
    for pid in pids:
        try:
            cmds = open(os.path.join('/proc', pid, 'cmdline'), 'rt').read().split('\0')
#            print "cmds", len(cmds), cmds
            if cmds[0] == "udhcpc" and _iface in cmds:
                print(("PID", pid, "is the dhcp for", _iface))
                return True

        except IOError: # proc has already terminated
            continue
    return False

def run_dhcp(_iface):
    if not check4dhcp(_iface):
        run_program("sudo udhcpc -R -n -p /var/run/udhcpc.wlan0.pid -i %s" % _iface)

def _disconnect_all(_iface):
    """
    Disconnect all wireless networks.
    """
    lines = run_program("sudo wpa_cli -i %s list_networks" % _iface).split("\n")
    if lines:
        for line in lines[1:-1]:
            run_program("sudo wpa_cli -i %s remove_network %s" % (_iface, line.split()[0]))  

def get_associated(_iface):
    """
    Check if we're associated to a network and return its ssid.
    """
    r = run_program("sudo wpa_cli -i %s status" % _iface)
    if "wpa_state=COMPLETED" in r:
        for line in r.split("\n")[1:]:
            if line.split('=')[0] == "ssid":
                return line.split('=')[1]
    return ""

class KeyDialog(TxtDialog):
    def __init__(self,title,str,parent):
        TxtDialog.__init__(self, title, parent)

        self.layout = QVBoxLayout()

        edit = QWidget()
        edit.hbox = QHBoxLayout()
        edit.hbox.setContentsMargins(0,0,0,0)

        self.line = QLineEdit(str)
        #        self.line.setReadOnly(True)
        self.line.setAlignment(Qt.AlignCenter)
        edit.hbox.addWidget(self.line)
        but = QPushButton()
        pix = QPixmap(local + "erase.png")
        icn = QIcon(pix)
        but.setIcon(icn)
        but.setIconSize(pix.size())
        but.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Expanding);
        but.clicked.connect(self.key_erase)
        edit.hbox.addWidget(but)

        edit.setLayout(edit.hbox)
        self.layout.addWidget(edit)

        self.tab = QTabWidget()

        for a in range(3):
            page = QWidget()
            page.grid = QGridLayout()
            page.grid.setContentsMargins(0,0,0,0)

            cnt = 0
            for i in keys_upper[a]:
                if i == "Aa":
                    but = QPushButton()
                    pix = QPixmap(local + "caps.png")
                    icn = QIcon(pix)
                    but.setIcon(icn)
                    but.setIconSize(pix.size())
                    but.clicked.connect(self.caps_changed)
                else:
                    but = QPushButton(i)
                    but.clicked.connect(self.key_pressed)

                but.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding);
                page.grid.addWidget(but,cnt/4,cnt%4)
                cnt+=1

            page.setLayout(page.grid)
            self.tab.addTab(page, keys_tab[a])

        self.tab.tabBar().setExpanding(True);
        self.tab.tabBar().setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding);
        self.layout.addWidget(self.tab)

        self.centralWidget.setLayout(self.layout)        

    def key_erase(self):
        self.line.setText(self.line.text()[:-1]) 

    def key_pressed(self):
        self.line.setText(self.line.text() + self.sender().text())

        # user pressed the caps button. Exchange all button texts
    def caps_changed(self):
        global caps
        caps = not caps
        if caps:  keys = keys_upper
        else:     keys = keys_lower

        # exchange all characters
        for i in range(self.tab.count()):
            gw = self.tab.widget(i)
            gl = gw.layout()
            for j in range(gl.count()):
                w = gl.itemAt(j).widget()
                if keys[i][j] != "Aa":
                    w.setText(keys[i][j]);

    def exec_(self):
        TxtDialog.exec_(self)
        return self.line.text()

# background thread to monitor state of interface
class MonitorThread(QThread):
    def __init__(self):
        QThread.__init__(self)

    def __del__(self):
        self.wait()
 
    def run(self):
        while True:
            time.sleep(5)  # poll every 5 seconds
            status = get_associated(IFACE)
            self.emit( SIGNAL('update_status(QString)'), status )   
        return
    
class FtcGuiApplication(TxtApplication):
    def __init__(self, args):
        global networks
        global connected_ssid
        global key

        TxtApplication.__init__(self, args)
        self.w = TxtWindow("Wifi")

        self.vbox = QVBoxLayout()

        networks = []
        networks_dup = get_networks(IFACE)
        if networks_dup:
            # remove duplicate ssids
            networks = []
            if len(networks_dup) > 1:
                for i in range(len(networks_dup)-1):
                    has_dup = False
                    for j in range(i+1,len(networks_dup)):
                        if networks_dup[i]['ssid'] == networks_dup[j]['ssid']:
                            has_dup = True
                    if not has_dup:
                        if networks_dup[i]['ssid'] != "\\x00":
                            networks.append(networks_dup[i])

                if networks_dup[-1]['ssid'] != "\\x00":
                    networks.append(networks_dup[-1])

            # only one ssid returned: This sure has no duplicate
            elif len(networks_dup) > 0:
                networks.append(networks_dup[0])
        
        self.ssids_w = QComboBox()
        if networks:
            for network in networks:
                self.ssids_w.addItem(network['ssid'])
        self.ssids_w.activated[str].connect(self.set_default_encryption)
        self.ssids_w.setCurrentIndex(-1)
        self.vbox.addWidget(self.ssids_w)

        self.vbox.addStretch()

        self.vbox.addWidget(QLabel("Encryption:"))
        self.encr_w = QComboBox()
        self.encr_w.addItems(encr)
        self.vbox.addWidget(self.encr_w)

        self.vbox.addStretch()

        self.edit_hbox_w = QWidget()
        self.edit_hbox = QHBoxLayout()
        self.key = QLineEdit(key)
        self.key.setPlaceholderText("key")
        self.key.editingFinished.connect(self.do_edit_done)
        self.edit_hbox.addWidget(self.key)
        self.edit_but = QPushButton()
        pix = QPixmap(local + "edit.png")
        icn = QIcon(pix)
        self.edit_but.setIcon(icn)
        self.edit_but.setIconSize(pix.size())
        self.edit_but.clicked.connect(self.do_key)
        self.edit_hbox.addWidget(self.edit_but)
        self.edit_hbox_w.setLayout(self.edit_hbox)
        self.vbox.addWidget(self.edit_hbox_w)

        # the connect button is by default disabled until
        # the user enters a key
        self.connect = QPushButton("Connect")
        self.connect.clicked.connect(self.do_connect)
        self.connect.setDisabled(True)
        self.vbox.addWidget(self.connect)

        # check if a network is already connected
        connected_ssid = get_associated(IFACE)
        if connected_ssid != "":
            print(("Already associated with", connected_ssid))
            for i in range(len(networks)):
                if networks[i]['ssid'] == connected_ssid:
                    self.ssids_w.setCurrentIndex(i)

        # update gui depending on selected ssid
        if networks and self.ssids_w.currentText() != "":
            self.set_default_encryption(self.ssids_w.currentText())

        self.w.centralWidget.setLayout(self.vbox)
        self.w.show() 

        # start thread to monitor wlan0 state and connect it to
        # slot to receive events
        self.monitorThread = MonitorThread()
        self.w.connect( self.monitorThread, SIGNAL("update_status(QString)"), self.on_update_status )
        self.monitorThread.start()

        self.exec_()        

    def on_update_status(self, ssid):
        global connected_ssid
        print(("New ssid:", ssid))
        if connected_ssid != ssid:
            connected_ssid = ssid
            self.update_connect_button(self.ssids_w.currentText())
            if ssid != "":
                save_config(IFACE)
                run_dhcp(IFACE)

    def set_key(self, k):
        global key
        key = k

        # enable connect button if key was entered
        if k != "":
            # but only if the current network isn't already connected
            self.connect.setDisabled(connected_ssid == self.ssids_w.currentText())
        else:
            self.connect.setDisabled(True)

        self.key.setText(k)

        # user entered a key using a keyboard
    def do_edit_done(self):
        self.set_key(self.sender().text())

        # user hit the "key edit button"
    def do_key(self):
        global key
        dialog = KeyDialog("Key",key,self.w)
        self.set_key( dialog.exec_() )
 
    def do_connect(self):
        global networks
        ssid = self.ssids_w.currentText()
        enc_type = self.encr_w.currentText()
        enc_key = self.key.text()
        print(("Connecting to", ssid, "with", enc_type, enc_key))
        connect_to_network(IFACE, ssid, enc_type, enc_key)

    def set_default_encryption(self,net):
        global networks
        print(("Setting default encryption for", net))
        # search for network is list
        for i in networks: 
            if i['ssid'] == net:
                if "WPA2" in i['flag']:
                    self.encr_w.setCurrentIndex(3)
                elif "WPA" in i['flag']:
                    self.encr_w.setCurrentIndex(2)
                elif "WEP" in i['flag']:
                    self.encr_w.setCurrentIndex(1)
                else:
                    self.encr_w.setCurrentIndex(0)
        self.update_connect_button(net)

    def update_connect_button(self,net):
        global key
        if net == connected_ssid:
            self.connect.setText("connected")
            self.connect.setDisabled(True)
        else:
            self.connect.setText("Connect")
            self.connect.setDisabled(key == "")

if __name__ == "__main__":
    FtcGuiApplication(sys.argv)
