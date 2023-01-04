#! /usr/bin/env python3
# -*- coding: utf-8 -*-
#

# assume wpa has been started e.g. by
# sudo wpa_supplicant -B -Dwext -i wlan0 -C/var/run/wpa_supplicant

import sys, os, shlex, time
from TouchStyle import *
from TouchAuxiliary import run_program
from launcher import LauncherPlugin

try:
    if TouchStyle_version<1.3: TouchStyle_version=0
except:
    TouchStyle_version=0.0

local = os.path.dirname(os.path.realpath(__file__)) + "/"

IFACE = "wlan0"

encr = [ "OPEN", "WEP", "WPA", "WPA2" ];

COUNTRIES = {
    "Germany": "DE",
    "United States": "US",
    "Britain (UK)": "GB",
    "Netherlands": "NL",
    "France": "FR"
}
    
def scan_networks(iface, retry=2):
    run_program("sudo wpa_cli -i %s scan_interval 5" % iface)
    for attempt in range(retry+1):
        if "OK" in run_program("sudo wpa_cli -i %s scan" % iface):
            return True
    return False

def get_networks(iface, retry=2):
    """
    Grab a list of wireless networks within range, and return a list of dicts describing them.
    """
    for attempt in range(retry+1):
        networks=[]
        r = run_program("sudo wpa_cli -i %s scan_result" % iface).strip()
        if "bssid" in r and len ( r.split("\n") ) >1 :
            for line in r.split("\n")[1:]:
                b, fr, s, f = line.split()[:4]
                ss = " ".join(line.split()[4:]) #Hmm, dirty
                networks.append( {"bssid":b, "freq":fr, "sig":s, "ssid":ss, "flag":f} )
            return networks
 
#       print("SCAN did not return ok, trying setting the country to DE ...")
#       run_program("sudo wpa_cli -i %s set country DE" % iface)
#       run_program("sudo wpa_cli -i %s save_config" % iface)
#       run_program("sudo rfkill unblock wifi")

        time.sleep(0.5)

    return None

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
            
            run_program("sudo wpa_cli -i %s select_network 0" % _iface)

def save_config(_iface):
    run_program("sudo wpa_cli -i %s save_config" % _iface)

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

def set_country(_iface, country):
    run_program("sudo wpa_cli -i %s set country %s" % (_iface, country))
    run_program("sudo wpa_cli -i %s save_config" % _iface)

def run_dhcp(_iface):
    # ask udhcpc to obtain a fresh address if it's already runnung. Start it otherwise
    if check4dhcp(_iface):
        run_program("sudo killall -SIGUSR1 udhcpc")
    else:
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

# background thread to monitor state of interface
class MonitorThread(QThread):

    update_status = pyqtSignal(str)
    network_added = pyqtSignal(object)
    ssid_removed = pyqtSignal(str)
    
    def __init__(self):
        QThread.__init__(self)
        self.ssids = set()
        self.associated_ssid = ""

    def __del__(self):
        self.stop()

    def run(self):
        self.timer = QTimer()
        self.timer.timeout.connect(self.on_timer_tick)

        scan_networks(IFACE)
        self.timer.start(2000) # Poll every 2 seconds
        
        self.exec_()

    @pyqtSlot()
    def on_timer_tick(self):
        ssid = get_associated(IFACE)
        if ssid != self.associated_ssid:
            self.update_status.emit(ssid)
            self.associated_ssid = ssid

        networks = get_networks(IFACE)
        if networks:
            print(networks)
            current_ssids = {s["ssid"] for s in networks}
            new_ssids = current_ssids.difference(self.ssids)
            missing_ssids = self.ssids.difference(current_ssids)

            for ssid in new_ssids:
                network = next(x for x in networks if x["ssid"] == ssid)
                self.network_added.emit(network)
            for ssid in missing_ssids:
                self.ssid_removed.emit(ssid)
            self.ssids = current_ssids
            
    def stop(self):
        print("Stopping network monitor thread...")
        #self.timer.stop()
        self.quit()
        self.wait()
        print("... network monitor thread stopped")

class WlanWindow(TouchWindow):
    def __init__(self, app, str):
        super().__init__(str)
        self.monitorThread = MonitorThread()
        self.monitorThread.update_status.connect(app.on_update_status)
        self.monitorThread.network_added.connect(app.new_network)
        self.monitorThread.ssid_removed.connect(app.ssid_removed)

    def show(self):
        super().show()
        # start thread to monitor wlan0 state and connect it to
        # slot to receive events
        self.monitorThread.start()

    def close(self):
        self.monitorThread.stop()
        super().close()

class FtcGuiPlugin(LauncherPlugin):
    def __init__(self, application):
        LauncherPlugin.__init__(self, application)

        translator = QTranslator()
        path = os.path.dirname(os.path.realpath(__file__))
        translator.load(self.locale(), os.path.join(path, "wlan_"))
        self.installTranslator(translator)

        self.mainWindow = WlanWindow(self, QCoreApplication.translate("Main", "WLAN"))

        menu = self.mainWindow.addMenu()
        submenu = menu.addMenu(QCoreApplication.translate("Main","Set Country"))
        for i in COUNTRIES:
            entry = submenu.addAction(i)
            entry.setData( COUNTRIES[i] )
            entry.triggered.connect(self.on_set_country)

        self.vbox = QVBoxLayout()

        self.networks = []
        self.connected_ssid = ""
        self.encr_key = ""
        
        self.ssids_w = QComboBox()
        self.ssids_w.activated[str].connect(self.set_default_encryption)
        self.ssids_w.setCurrentIndex(-1)
        self.vbox.addWidget(self.ssids_w)

        self.vbox.addStretch()

        self.vbox.addWidget(QLabel(QCoreApplication.translate("Main", "Encryption:")))
        self.encr_w = QComboBox()
        self.encr_w.addItems(encr)
        self.vbox.addWidget(self.encr_w)

        self.vbox.addStretch()

        self.vbox.addWidget(QLabel(QCoreApplication.translate("Main", "Key:")))
        self.key = QLineEdit(self.encr_key)
        self.key.setPlaceholderText(QCoreApplication.translate("placeholder", "key"))
        self.key.textChanged.connect(self.do_edit_done)
        self.vbox.addWidget(self.key)

        # the connect button is by default disabled until
        # the user enters a key
        self.connect = QPushButton(QCoreApplication.translate("Main", "Connect"))
        self.connect.clicked.connect(self.do_connect)
        self.connect.setDisabled(True)
        self.vbox.addWidget(self.connect)

        self.mainWindow.centralWidget.setLayout(self.vbox)

        # make sure key edit has focus
        self.key.setFocus()
        self.mainWindow.show()


    @pyqtSlot(object)
    def new_network(self, network):
        print("found network %s" % network)
        self.ssids_w.addItem(network["ssid"])
        self.update_connect_button(self.ssids_w.currentText())
        self.networks.append(network)

    @pyqtSlot(str)
    def ssid_removed(self, ssid):
        print("lost ssid %s" % ssid)
        idx = self.ssids_w.findText(ssid)
        if idx != -1:
            self.ssids_w.removeItem(idx)
        self.networks = [s for s in self.networks if s["ssid"] != ssid]
        self.update_connect_button(self.ssids_w.currentText())

    @pyqtSlot(bool)
    def on_set_country(self, x):
        set_country(IFACE, self.sender().data())

    @pyqtSlot(str)
    def on_update_status(self, ssid):
        # select in list
        if self.connected_ssid != "":
            for i in range(len(self.networks)):
                if self.networks[i]['ssid'] == self.connected_ssid:
                    self.ssids_w.setCurrentIndex(i)
                    self.set_default_encryption(self.ssids_w.currentText())

        # manage changes
        if self.connected_ssid != ssid:
            self.connected_ssid = ssid
            self.update_connect_button(self.ssids_w.currentText())
            if ssid != "":
                save_config(IFACE)
                run_dhcp(IFACE)

    def set_key(self, k):
        self.encr_key = k
        self.key.setText(k)
        
        self.update_connect_button(self.ssids_w.currentText())

        # user entered a key using a keyboard
    def do_edit_done(self):
        self.set_key(self.sender().text())
        self.key.setFocus()

    def do_connect(self):
        ssid = self.ssids_w.currentText()
        enc_type = self.encr_w.currentText()
        enc_key = self.key.text()
        connect_to_network(IFACE, ssid, enc_type, enc_key)

    def set_default_encryption(self,net):
        # search for network is list
        for i in self.networks: 
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

    def update_connect_button(self, ssid):

        already_connected = self.connected_ssid == self.ssids_w.currentText()
        key_unavailable = self.encr_key == ""
        
        self.connect.setDisabled(already_connected or key_unavailable)
        if already_connected:
            self.connect.setText(QCoreApplication.translate("Main", "connected"))
        else:
            self.connect.setText(QCoreApplication.translate("Main", "Connect"))

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

