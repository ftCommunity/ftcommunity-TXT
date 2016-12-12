#! /usr/bin/env python3
# -*- coding: utf-8 -*-
#
import sys
import os
import configparser
from TouchStyle import *
from subprocess import Popen, call, PIPE
import socket
import array
import struct
import fcntl
import string
import platform
import shlex
import time
import urllib.request
import json
import ssl
from _thread import start_new_thread
CONFIG_FILE = '/media/sdcard/data/config.conf'
avaible_languages = ['EN', 'DE']
LOCAL_PATH = os.path.dirname(os.path.realpath(__file__))


class Language():

    def __init__(self, path, default_language):
        self.path = path
        self.default_language = default_language

        try:
            config = configparser.RawConfigParser()
            config.read(CONFIG_FILE)
            self.language = config.get('general', 'language')
        except:
            self.language = self.default_language

        try:
            self.global_error = False
            self.translation = configparser.RawConfigParser()
            self.translation.read(self.path)
        except:
            self.global_error = True

    def get_string(self, key):
        if self.global_error == False:
            try:
                return(self.translation.get(self.language, key))
            except:
                pass

            try:
                return(self.translation.get(self.default_language, key))
            except:
                pass
        return('missingno')

translation = Language(os.path.dirname(__file__) + '/translation', 'EN')


class LanguageDialog(TouchDialog):

    def __init__(self, parent):
        TouchDialog.__init__(self, translation.get_string('w_language_name'), parent)
        self.vbox = QVBoxLayout()
        self.vbox.addStretch()
        self.vbox.addWidget(QLabel(translation.get_string('w_language_lang_select')))
        self.lang_select = QComboBox()
        self.lang_select.addItems(avaible_languages)
        self.vbox.addWidget(self.lang_select)
        self.vbox.addStretch()
        self.save_but = QPushButton(translation.get_string('w_language_save'))
        self.save_but.clicked.connect(self.save)
        self.vbox.addWidget(self.save_but)
        self.vbox.addStretch()
        self.centralWidget.setLayout(self.vbox)
        try:
            config = configparser.RawConfigParser()
            config.read(CONFIG_FILE)
            self.lang_select.setCurrentIndex(avaible_languages.index(config.get('general', 'language')))
        except:
            pass

    def save(self):
        print(self.lang_select.currentText())
        config = configparser.ConfigParser()
        cfgfile = open(CONFIG_FILE, 'w')
        config.add_section('general')
        config.set('general', 'language', self.lang_select.currentText())
        config.write(cfgfile)
        cfgfile.close()
        self.close()


class NetinfoDialog(TouchDialog):

    def __init__(self, parent):
        DEFAULT = "wlan0"
        TouchDialog.__init__(self, translation.get_string('w_netinfo_name'), parent)
        self.ifs = self.all_interfaces()
        names = sorted(list(self.ifs.keys()))
        self.vbox = QVBoxLayout()
        self.nets_w = QComboBox()
        self.nets_w.activated[str].connect(self.set_net)
        for i in names:
            self.nets_w.addItem(i)
        self.vbox.addWidget(self.nets_w)
        self.vbox.addStretch()
        self.ip_lbl = QLabel(translation.get_string('w_netinfo_adress'))
        self.ip_lbl.setAlignment(Qt.AlignCenter)
        self.vbox.addWidget(self.ip_lbl)
        self.ip = QLabel("")
        self.ip.setObjectName("smalllabel")
        self.ip.setAlignment(Qt.AlignCenter)
        self.vbox.addWidget(self.ip)
        self.mask_lbl = QLabel(translation.get_string('w_netinfo_netmask'))
        self.mask_lbl.setAlignment(Qt.AlignCenter)
        self.vbox.addWidget(self.mask_lbl)
        self.mask = QLabel("")
        self.mask.setObjectName("smalllabel")
        self.mask.setAlignment(Qt.AlignCenter)
        self.vbox.addWidget(self.mask)
        # select wlan0 if in list
        if DEFAULT in names:
            self.nets_w.setCurrentIndex(names.index(DEFAULT))
            self.set_net(DEFAULT)
        else:
            self.set_net(names[0])
        self.vbox.addStretch()
        self.centralWidget.setLayout(self.vbox)

    def _ifinfo(self, sock, addr, ifname):
        iface = struct.pack('256s', bytes(ifname[:15], "UTF-8"))
        info = fcntl.ioctl(sock.fileno(), addr, iface)
        return socket.inet_ntoa(info[20:24])

    def all_interfaces(self, ):
        SIOCGIFCONF = 0x8912
        SIOCGIFADDR = 0x8915
        SIOCGIFNETMASK = 0x891b
        if platform.machine() == "armv7l":
            size = 32
        else:
            size = 40
        bytes = 8 * size
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        names = array.array('B', b'\x00' * bytes)
        outbytes = struct.unpack('iL', fcntl.ioctl(s.fileno(), SIOCGIFCONF, struct.pack('iL', bytes, names.buffer_info()[0])))[0]
        namestr = names.tostring()
        # get additional info for all interfaces found
        lst = {}
        for i in range(0, outbytes, size):
            name = namestr[i:i + 16].decode('UTF-8').split('\0', 1)[0]
            if name != "" and not name in lst:
                addr = self._ifinfo(s, SIOCGIFADDR, name)
                mask = self._ifinfo(s, SIOCGIFNETMASK, name)
                lst[name] = (addr, mask)
        return lst

    def set_net(self, name):
        interface = self.ifs[name]
        self.ip.setText(interface[0])
        self.mask.setText(interface[1])


class WLanDialog(TouchDialog):

    def __init__(self, parent):
        encr = ["OPEN", "WEP", "WPA", "WPA2"]
        TouchDialog.__init__(self, translation.get_string('w_wlan_name'), parent)
        self.key = ""
        self.w = TouchWindow("Wifi")
        self.vbox = QVBoxLayout()
        self.vbox.setContentsMargins(2, 2, 2, 2)
        self.networks = []
        networks_dup = self.get_networks("wlan0")
        if networks_dup:
            self.networks = []
            if len(networks_dup) > 1:
                for i in range(len(networks_dup) - 1):
                    has_dup = False
                    for j in range(i + 1, len(networks_dup)):
                        if networks_dup[i]['ssid'] == networks_dup[j]['ssid']:
                            has_dup = True
                    if not has_dup:
                        if networks_dup[i]['ssid'] != "\\x00":
                            self.networks.append(networks_dup[i])
                if networks_dup[-1]['ssid'] != "\\x00":
                    self.networks.append(networks_dup[-1])
            elif len(networks_dup) > 0:
                self.networks.append(networks_dup[0])
        self.ssids_w = QComboBox()
        if self.networks:
            for network in self.networks:
                self.ssids_w.addItem(network['ssid'])
        self.ssids_w.activated[str].connect(self.set_default_encryption)
        self.ssids_w.setCurrentIndex(-1)
        self.vbox.addWidget(self.ssids_w)
        self.vbox.addStretch()
        self.vbox.addWidget(QLabel(translation.get_string('w_wlan_encryption')))
        self.encr_w = QComboBox()
        self.encr_w.addItems(encr)
        self.vbox.addWidget(self.encr_w)
        self.edit_hbox_w = QWidget()
        self.edit_hbox = QHBoxLayout()
        self.edit_hbox.setContentsMargins(0, 0, 0, 0)
        self.key_edit = QLineEdit(self.key)
        self.key_edit.setPlaceholderText("key")
        self.key_edit.editingFinished.connect(self.do_edit_done)
        self.edit_hbox.addWidget(self.key_edit)
        self.edit_but = QPushButton()
        pix = QPixmap(os.path.join(LOCAL_PATH, "wlan/edit.png"))
        self.edit_but.setIcon(QIcon(pix))
        self.edit_but.setIconSize(pix.size())
        self.edit_but.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)
        self.edit_but.clicked.connect(self.do_key)
        self.edit_hbox.addWidget(self.edit_but)
        self.edit_hbox_w.setLayout(self.edit_hbox)
        self.vbox.addWidget(self.edit_hbox_w)
        self.connect = QPushButton("Connect")
        self.connect.clicked.connect(self.do_connect)
        self.connect.setDisabled(True)
        self.vbox.addWidget(self.connect)
        self.connected_ssid = self.get_associated("wlan0")
        if self.connected_ssid != "":
            print("Already associated with", self.connected_ssid)
            for i in range(len(self.networks)):
                if self.networks[i]['ssid'] == self.connected_ssid:
                    self.ssids_w.setCurrentIndex(i)
        if self.networks and self.ssids_w.currentText() != "":
            self.set_default_encryption(self.ssids_w.currentText())
        self.centralWidget.setLayout(self.vbox)
        self.monitorThread = self.MonitorThread()
        self.w.connect(self.monitorThread, SIGNAL("update_status(QString)"), self.on_update_status)
        self.monitorThread.start()

    def run_program(self, rcmd):
        """
        Runs a program, and it's paramters (e.g. rcmd="ls -lh /var/www")
        Returns output if successful, or None and logs error if not.
        """

        cmd = shlex.split(rcmd)
        executable = cmd[0]
        executable_options = cmd[1:]

        print("run: ", rcmd)

        try:
            proc = Popen(([executable] + executable_options), stdout=PIPE, stderr=PIPE)
            response = proc.communicate()
            response_stdout, response_stderr = response[0].decode('UTF-8'), response[1].decode('UTF-8')
        except OSError as e:
            if e.errno == errno.ENOENT:
                print("Unable to locate '%s' program. Is it in your path?" % executable)
            else:
                print("O/S error occured when trying to run '%s': \"%s\"" % (executable, str(e)))
        except ValueError as e:
            print("Value error occured. Check your parameters.")
        else:
            if proc.wait() != 0:
                print("Executable '%s' returned with the error: \"%s\"" % (executable, response_stderr))
                return response
            else:
                print("Executable '%s' returned successfully." % (executable))
                print(" First line of response was \"%s\"" % (response_stdout.split('\n')[0]))
                return response_stdout

    def get_networks(self, iface, retry=10):
        """
        Grab a list of wireless networks within range, and return a list of dicts describing them.
        """
        while retry > 0:
            if "OK" in self.run_program("sudo wpa_cli -i %s scan" % iface):
                networks = []
                r = self.run_program("sudo wpa_cli -i %s scan_result" % iface).strip()
                if "bssid" in r and len(r.split("\n")) > 1:
                    for line in r.split("\n")[1:]:
                        b, fr, s, f = line.split()[:4]
                        ss = " ".join(line.split()[4:])  # Hmm, dirty
                        networks.append({"bssid": b, "freq": fr, "sig": s, "ssid": ss, "flag": f})
                    return networks
            retry -= 1
            print("Couldn't retrieve networks, retrying")
            time.sleep(0.5)
        print("Failed to list networks")

    def connect_to_network(self, _iface, _ssid, _type, _pass=None):
        """
        Associate to a wireless network. Support _type options:
        *WPA[2], WEP, OPEN
        """
        self._disconnect_all(_iface)
        time.sleep(1)
        if self.run_program("sudo wpa_cli -i %s add_network" % _iface) == "0\n":
            if self.run_program('sudo wpa_cli -i %s set_network 0 ssid \'"%s"\'' % (_iface, _ssid)) == "OK\n":
                if _type == "OPEN":
                    self.run_program("sudo wpa_cli -i %s set_network 0 auth_alg OPEN" % _iface)
                    self.run_program("sudo wpa_cli -i %s set_network 0 key_mgmt NONE" % _iface)
                elif _type == "WPA" or _type == "WPA2":
                    self.run_program('sudo wpa_cli -i %s set_network 0 psk \'"%s"\'' % (_iface, _pass))
                elif _type == "WEP":
                    self.run_program("sudo wpa_cli -i %s set_network 0 wep_key %s" % (_iface, _pass))
                else:
                    print("Unsupported type")

                self.run_program("sudo wpa_cli -i %s select_network 0" % _iface)

    def save_config(_iface):
        self.run_program("sudo wpa_cli -i %s save_config" % _iface)

    def check4dhcp(_iface):
        pids = [pid for pid in os.listdir('/proc') if pid.isdigit()]
        for pid in pids:
            try:
                cmds = open(os.path.join('/proc', pid, 'cmdline'), 'rt').read().split('\0')
                if cmds[0] == "udhcpc" and _iface in cmds:
                    print("PID", pid, "is the dhcp for", _iface)
                    return True

            except IOError:  # proc has already terminated
                continue
        return False

    def run_dhcp(_iface):
        if not check4dhcp(_iface):
            self.run_program("sudo udhcpc -R -n -p /var/run/udhcpc.wlan0.pid -i %s" % _iface)

    def _disconnect_all(self, _iface):
        """
        Disconnect all wireless networks.
        """
        lines = self.run_program("sudo wpa_cli -i %s list_networks" % _iface).split("\n")
        if lines:
            for line in lines[1:-1]:
                self.run_program("sudo wpa_cli -i %s remove_network %s" % (_iface, line.split()[0]))

    def get_associated(self, _iface):
        """
        Check if we're associated to a network and return its ssid.
        """
        r = self.run_program("sudo wpa_cli -i %s status" % _iface)
        if "wpa_state=COMPLETED" in r:
            for line in r.split("\n")[1:]:
                if line.split('=')[0] == "ssid":
                    return line.split('=')[1]
        return ""

    class KeyDialog(TouchDialog):

        def __init__(self, title, str, parent):
            TouchDialog.__init__(self, title, parent)
            keys_tab = ["A-O", "P-Z", "0-9"]
            self.keys_upper = [
                ["A", "B", "C", "D", "E", "F", "G", "H", "I", "J", "K", "L", "M", "N", "O", "Aa"],
                ["P", "Q", "R", "S", "T", "U", "V", "W", "X", "Y", "Z", ".", ",", " ", "_", "Aa"],
                ["0", "1", "2", "3", "4", "5", "6", "7", "8", "9", "+", "-", "*", "/", "#", "$"]
            ]
            self.keys_lower = [
                ["a", "b", "c", "d", "e", "f", "g", "h", "i", "j", "k", "l", "m", "n", "o", "Aa"],
                ["p", "q", "r", "s", "t", "u", "v", "w", "x", "y", "z", ":", ";", "!", "?", "Aa"],
                ["0", "1", "2", "3", "4", "5", "6", "7", "8", "9", "+", "-", "*", "/", "#", "$"]
            ]
            self.caps = True
            self.layout = QVBoxLayout()

            edit = QWidget()
            edit.hbox = QHBoxLayout()
            edit.hbox.setContentsMargins(0, 0, 0, 0)

            self.line = QLineEdit(str)
            self.line.setAlignment(Qt.AlignCenter)
            edit.hbox.addWidget(self.line)
            but = QPushButton()
            pix = QPixmap(os.path.join(LOCAL_PATH, "wlan/erase.png"))
            icn = QIcon(pix)
            but.setIcon(icn)
            but.setIconSize(pix.size())
            but.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)
            but.clicked.connect(self.key_erase)
            edit.hbox.addWidget(but)

            edit.setLayout(edit.hbox)
            self.layout.addWidget(edit)

            self.tab = QTabWidget()

            for a in range(3):
                page = QWidget()
                page.grid = QGridLayout()
                page.grid.setContentsMargins(0, 0, 0, 0)

                cnt = 0
                for i in self.keys_lower[a]:
                    if i == "Aa":
                        but = QPushButton()
                        pix = QPixmap(os.path.join(LOCAL_PATH, "wlan/caps.png"))
                        icn = QIcon(pix)
                        but.setIcon(icn)
                        but.setIconSize(pix.size())
                        but.clicked.connect(self.caps_changed)
                    else:
                        but = QPushButton(i)
                        but.clicked.connect(self.key_pressed)

                    but.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
                    page.grid.addWidget(but, cnt / 4, cnt % 4)
                    cnt += 1

                page.setLayout(page.grid)
                self.tab.addTab(page, keys_tab[a])

            self.tab.tabBar().setExpanding(True)
            self.tab.tabBar().setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
            self.layout.addWidget(self.tab)

            self.centralWidget.setLayout(self.layout)

        def key_erase(self):
            self.line.setText(self.line.text()[:-1])

        def key_pressed(self):
            self.line.setText(self.line.text() + self.sender().text())

            # user pressed the caps button. Exchange all button texts
        def caps_changed(self):
            # default is not caps locked
            try:
                self.caps = not self.caps
            except AttributeError:
                self.caps = True

            if self.caps:
                keys = keys_upper
            else:
                keys = keys_lower

            # exchange all characters
            for i in range(self.tab.count()):
                gw = self.tab.widget(i)
                gl = gw.layout()
                for j in range(gl.count()):
                    w = gl.itemAt(j).widget()
                    if keys[i][j] != "Aa":
                        w.setText(keys[i][j])

        def exec_(self):
            TouchDialog.exec_(self)
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
                status = self.get_associated("wlan0")
                self.emit(SIGNAL('update_status(QString)'), status)
            return

        def get_associated(self, _iface):
            """
            Check if we're associated to a network and return its ssid.
            """
            r = self.run_program("sudo wpa_cli -i %s status" % _iface)
            if "wpa_state=COMPLETED" in r:
                for line in r.split("\n")[1:]:
                    if line.split('=')[0] == "ssid":
                        return line.split('=')[1]
            return ""

        def run_program(self, rcmd):
            """
            Runs a program, and it's paramters (e.g. rcmd="ls -lh /var/www")
            Returns output if successful, or None and logs error if not.
            """

            cmd = shlex.split(rcmd)
            executable = cmd[0]
            executable_options = cmd[1:]

            print("run: ", rcmd)

            try:
                proc = Popen(([executable] + executable_options), stdout=PIPE, stderr=PIPE)
                response = proc.communicate()
                response_stdout, response_stderr = response[0].decode('UTF-8'), response[1].decode('UTF-8')
            except OSError as e:
                if e.errno == errno.ENOENT:
                    print("Unable to locate '%s' program. Is it in your path?" % executable)
                else:
                    print("O/S error occured when trying to run '%s': \"%s\"" % (executable, str(e)))
            except ValueError as e:
                print("Value error occured. Check your parameters.")
            else:
                if proc.wait() != 0:
                    print("Executable '%s' returned with the error: \"%s\"" % (executable, response_stderr))
                    return response
                else:
                    print("Executable '%s' returned successfully." % (executable))
                    print(" First line of response was \"%s\"" % (response_stdout.split('\n')[0]))
                    return response_stdout

    def on_update_status(self, ssid):
        print("New ssid:", ssid)
        if self.connected_ssid != ssid:
            self.connected_ssid = ssid
            self.update_connect_button(self.ssids_w.currentText())
            if ssid != "":
                save_config("wlan0")
                run_dhcp("wlan0")

    def set_key(self, k):
        self.key = k

        # enable connect button if key was entered
        if k != "":
            # but only if the current network isn't already connected
            self.connect.setDisabled(self.connected_ssid == self.ssids_w.currentText())
        else:
            self.connect.setDisabled(True)

        self.key_edit.setText(k)

        # user entered a key using a keyboard
    def do_edit_done(self):
        self.set_key(self.sender().text())

        # user hit the "key edit button"
    def do_key(self):
        dialog = self.KeyDialog("Key", self.key, self.w)
        self.set_key(dialog.exec_())

    def do_connect(self):
        ssid = self.ssids_w.currentText()
        enc_type = self.encr_w.currentText()
        enc_key = self.key_edit.text()
        print("Connecting to", ssid, "with", enc_type, enc_key)
        self.connect_to_network("wlan0", ssid, enc_type, enc_key)

    def set_default_encryption(self, net):
        print("Setting default encryption for", net)
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

    def update_connect_button(self, net):
        if net == self.connected_ssid:
            self.connect.setText("connected")
            self.connect.setDisabled(True)
        else:
            self.connect.setText("Connect")
            self.connect.setDisabled(self.key == "")


class UpdateCheckDialog(TouchDialog):

    def __init__(self, parent):
        TouchDialog.__init__(self, translation.get_string('w_update_name'), parent)
        self.vbox = QVBoxLayout()
        self.vbox.addStretch()
        self.status = QLabel('<html>' + translation.get_string('w_update_search_search') + '<br><img src="' + LOCAL_PATH + '/update/search.png"></html>')
        self.status.setAlignment(Qt.AlignCenter)
        self.vbox.addWidget(self.status)
        self.vbox.addStretch()
        self.but_update = QPushButton(translation.get_string('w_update_search_button'))
        self.but_update.clicked.connect(self.do_update)
        self.but_update.setDisabled(True)
        self.vbox.addWidget(self.but_update)
        self.vbox.addStretch()
        self.centralWidget.setLayout(self.vbox)
        start_new_thread(self.checkupdate, ())

    def do_update(self):
        dialog = UpdateInitiateDialog(self)
        dialog.exec_()
        self.but_update.setDisabled(True)

    def get_release_version(self):
        try:
            ctx = ssl.create_default_context()
            ctx.check_hostname = False
            ctx.verify_mode = ssl.CERT_NONE
            raw_data = urllib.request.urlopen('https://api.github.com/repos/ftCommunity/ftcommunity-TXT/releases/latest', context=ctx).read().decode()
            latest_release = json.loads(raw_data)
            release_version = latest_release['tag_name'].replace('v', '')
            return release_version
        except:
            None

    def get_current_version(self):
        try:
            current_version = os.popen('cat /etc/fw-ver.txt').read().strip().split('-')[0]
            return current_version
        except:
            return None

    def checkupdate(self):
        _rel_ver = self.get_release_version()
        _cur_ver = self.get_current_version()
        if _rel_ver == None or _cur_ver == None:
            self.but_update.setDisabled(True)
            self.status.setText('<html>' + translation.get_string('w_update_search_error') + '<br><img src="' + LOCAL_PATH + '/update/error.png"></html>')
            return
        if _rel_ver == _cur_ver:
            self.but_update.setDisabled(True)
            self.status.setText(translation.get_string('w_update_search_utd'))
        else:
            self.but_update.setDisabled(False)
            self.status.setText('<html>' + translation.get_string('w_update_search_update') + _rel_ver + '<br><img src="' + LOCAL_PATH + '/update/avaiable.png"></html>')


class UpdateInitiateDialog(TouchDialog):

    def __init__(self, parent):
        TouchDialog.__init__(self, translation.get_string('w_update_name'), parent)
        self.vbox = QVBoxLayout()
        self.vbox.addStretch()
        self.main_widget = QLabel(translation.get_string('w_update_initiate_prestart'))
        self.main_widget.setObjectName('smalllabel')
        self.main_widget.setWordWrap(True)
        self.vbox.addWidget(self.main_widget)
        self.vbox.addStretch()
        self.start_but = QPushButton(translation.get_string('w_update_process_start'))
        self.start_but.clicked.connect(self.do_update)
        self.vbox.addWidget(self.start_but)
        self.vbox.addStretch()
        self.centralWidget.setLayout(self.vbox)

    def do_update(self):
        dialog = UpdateProcessDialog(self)
        dialog.exec_()
        self.close()


class UpdateProcessDialog(TouchDialog):

    def __init__(self, parent):
        TouchDialog.__init__(self, translation.get_string('w_update_name'), parent)
        self.vbox = QVBoxLayout()
        self.vbox.addStretch()
        self.text = translation.get_string('w_update_process_0')
        self.html_widget = QLabel(self.text)
        self.vbox.addWidget(self.html_widget)
        self.vbox.addStretch()
        self.centralWidget.setLayout(self.vbox)
        timer = QTimer(self)
        timer.timeout.connect(self.update_text)
        timer.start(500)
        start_new_thread(self.process, ())

    def update_text(self):
        self.html_widget.setText(self.text)

    def process(self):
        time.sleep(3)
        self.text = translation.get_string('w_update_process_1')
        self.get_dl_url()
        print('Download URL: ' + str(self.dl_url) + ' with size: ' + str(self.dl_size))
        if self.dl_url == None:
            self.text = '<html>EROOR<br>DOWNLOAD<img src="' + LOCAL_PATH + '/update/error.png"></html>'
            time.sleep(5)
            os._exit(0)
            raise
        self.text = translation.get_string('w_update_process_2')
        os.system('rm /tmp/update.zip')
        os.system('wget ' + self.dl_url + ' -O /tmp/update.zip --no-check-certificate')
        self.text = translation.get_string('w_update_process_3')
        try:
            if self.dl_size == os.path.getsize('/tmp/update.zip'):
                pass
            else:
                self.text = '<html>EROOR<br>DOWNLOAD<img src="' + LOCAL_PATH + '/update/error.png"></html>'
                time.sleep(5)
                os._exit(0)
                raise
        except:
            self.text = '<html>EROOR<br>DOWNLOAD<img src="' + LOCAL_PATH + '/update/error.png"></html>'
            time.sleep(5)
            os._exit(0)
            raise
        self.text = translation.get_string('w_update_process_4')
        time.sleep(3)
        self.text = translation.get_string('w_update_process_5')
        os.system('sudo mkdir /media/sdcard/update_rollback/')
        self.text = translation.get_string('w_update_process_6')
        os.system('sudo mv /media/sdcard/am335x-kno_txt.dtb /media/sdcard/rootfs.img /media/sdcard/uImage /media/sdcard/update_rollback/')
        self.text = translation.get_string('w_update_process_7')
        time.sleep(3)
        self.text = translation.get_string('w_update_process_8')
        os.system('sudo unzip /tmp/update.zip -d /media/sdcard/')
        self.text = translation.get_string('w_update_process_9')
        time.sleep(5)
        self.text = translation.get_string('w_update_process_10')
        time.sleep(5)
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            self.sock.connect(("localhost", 9000))
            self.sock.sendall(bytes("msg Shutting down...\n", "UTF-8"))
        except:
            pass
        os.system('sudo poweroff')

    def get_dl_url(self):
        try:
            ctx = ssl.create_default_context()
            ctx.check_hostname = False
            ctx.verify_mode = ssl.CERT_NONE
            raw_data = urllib.request.urlopen('https://api.github.com/repos/ftCommunity/ftcommunity-TXT/releases/latest', context=ctx).read().decode()
            latest_release = json.loads(raw_data)
            assets = latest_release['assets']
            assets_count = 0
            content_type = ''
            while content_type != 'application/zip':
                if assets_count - 1 > len(assets):
                    print("No valid download link found! Contact the developer!")
                    self.dl_url = None
                    self.dl_size = None
                    return
                file_info = assets[assets_count]
                content_type = file_info['content_type']
                self.dl_url = file_info['browser_download_url']
                self.dl_size = file_info['size']
                assets_count += 1
            return
        except:
            self.dl_url = None
            self.dl_size = None
            return


class FtcGuiApplication(TouchApplication):

    def __init__(self, args):
        TouchApplication.__init__(self, args)
        self.w = TouchWindow(translation.get_string('app_name'))
        menu = self.w.addMenu()
        menu_lang = menu.addAction(translation.get_string('menu_language'))
        menu_lang.triggered.connect(self.menu_language_click)
        menu.addSeparator()
        menu_netinfo = menu.addAction(translation.get_string('menu_netinfo'))
        menu_netinfo.triggered.connect(self.menu_netinfo_click)
        menu_wlan = menu.addAction(translation.get_string('menu_wlan'))
        menu_wlan.triggered.connect(self.menu_wlan_click)
        menu.addSeparator()
        menu_update = menu.addAction(translation.get_string('menu_update'))
        menu_update.triggered.connect(self.menu_update_click)
        self.vbox = QVBoxLayout()
        self.vbox.addStretch()
        self.txt = QLabel(translation.get_string('home_text'))
        self.txt.setObjectName("smalllabel")
        self.txt.setWordWrap(True)
        self.txt.setAlignment(Qt.AlignCenter)
        self.vbox.addWidget(self.txt)
        self.vbox.addStretch()
        self.w.centralWidget.setLayout(self.vbox)
        self.w.show()
        self.exec_()

    def menu_language_click(self):
        dialog = LanguageDialog(self.w)
        dialog.exec_()

    def menu_netinfo_click(self):
        dialog = NetinfoDialog(self.w)
        dialog.exec_()

    def menu_wlan_click(self):
        dialog = WLanDialog(self.w)
        dialog.exec_()

    def menu_update_click(self):
        dialog = UpdateCheckDialog(self.w)
        dialog.exec_()

if __name__ == "__main__":
    FtcGuiApplication(sys.argv)
