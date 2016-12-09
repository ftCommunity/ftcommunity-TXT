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
from _thread import start_new_thread
import ssl
from PyQt4 import QtCore
global w
CONFIG_FILE = '/media/sdcard/data/config.conf'
LOCAL_PATH = os.path.dirname(os.path.realpath(__file__))
INET_PROBE_SERVERS = ['ftcommunity.de', 'github.com', 'google.com']


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
                return(self.string_transform(self.translation.get(self.language, key)))
            except:
                pass

            try:
                return(self.string_transform(self.translation.get(self.default_language, key)))
            except:
                pass
        return('missingno')

    def string_transform(self, string):
        transform = [
            ('&Auml;', 'Ä'), ('&auml;', 'ä'),
            ('&Ouml;', 'Ö'), ('&ouml;', 'ö'),
            ('&Uuml;', 'Ü'), ('&uuml;', 'ü')
        ]
        for t in transform:
            string = string.replace(t[0], t[1])
        return(string)

translation = Language(LOCAL_PATH + '/translation', 'EN')


class LanguageDialog(TouchDialog):

    def __init__(self, parent):
        self.avaible_languages = ['EN', 'DE']
        TouchDialog.__init__(self, translation.get_string('w_language_name'), parent)
        self.vbox = QVBoxLayout()
        self.vbox.addStretch()
        self.vbox.addWidget(QLabel(translation.get_string('w_language_lang_select')))
        self.lang_select = QComboBox()
        self.lang_select.addItems(self.avaible_languages)
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
            self.lang_select.setCurrentIndex(self.avaible_languages.index(config.get('general', 'language')))
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


class NetworkDialog(TouchDialog):

    def __init__(self, parent):
        DEFAULT = "wlan0"
        TouchDialog.__init__(self, translation.get_string('w_network_name'), parent)
        self.ifs = self.all_interfaces()
        names = sorted(list(self.ifs.keys()))
        self.vbox = QVBoxLayout()
        self.inet = QLabel(translation.get_string('w_network_probing'))
        self.inet.setStyleSheet('color: #ffff00')
        self.inet.setAlignment(Qt.AlignCenter)
        self.vbox.addWidget(self.inet)
        self.nets_w = QComboBox()
        self.nets_w.activated[str].connect(self.set_net)
        for i in names:
            self.nets_w.addItem(i)
        self.vbox.addWidget(self.nets_w)
        self.password = QPushButton(translation.get_string('w_network_password'))
        self.password.clicked.connect(self.auth_settings)
        self.password.setDisabled(True)
        self.vbox.addWidget(self.password)
        self.vbox.addStretch()
        self.ip_lbl = QLabel(translation.get_string('w_network_adress'))
        self.ip_lbl.setAlignment(Qt.AlignCenter)
        self.vbox.addWidget(self.ip_lbl)
        self.ip = QLabel("")
        self.ip.setObjectName("smalllabel")
        self.ip.setAlignment(Qt.AlignCenter)
        self.vbox.addWidget(self.ip)
        self.mask_lbl = QLabel(translation.get_string('w_network_netmask'))
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
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.inet_probe)
        self.timer.start(5000)

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
        if 'wlan' in name:
            self.password.setDisabled(False)
        else:
            self.password.setDisabled(True)

    def auth_settings(self):
        dialog = WLanDialog(self)
        dialog.exec_()

    def inet_probe(self):
        for server in INET_PROBE_SERVERS:
            print(server)
            try:
                host = socket.gethostbyname(server)
                s = socket.create_connection((host, 80), 2)
                self.inet.setText(translation.get_string('w_network_up'))
                self.inet.setStyleSheet('color: #00ff00')
                return
            except:
                pass
            self.inet.setText(translation.get_string('w_network_down'))
            self.inet.setStyleSheet('color: #ff0000')
            return


class WLanDialog(TouchDialog):

    def __init__(self, parent):
        encr = ["OPEN", "WEP", "WPA", "WPA2"]
        TouchDialog.__init__(self, translation.get_string('w_wlan_name'), parent)
        self.key = ""
        self.w = TouchWindow("Wifi")
        self.vbox = QVBoxLayout()
        self.vbox.setContentsMargins(2, 2, 2, 2)
        self.vbox.addWidget(QLabel(translation.get_string('w_wlan_network')))
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
        self.key_edit.setPlaceholderText(translation.get_string('w_wlan_prekey'))
        self.vbox.addWidget(self.key_edit)
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
        self.w.connect(self, SIGNAL("update_status(QString)"), self.on_update_status)
        self.timer0 = QTimer(self)
        self.timer0.timeout.connect(self.Monitoring)
        self.timer0.start(5000)
        self.timer1 = QTimer(self)
        self.timer1.timeout.connect(self.connect_edit_key_field_service)
        self.timer1.start(100)

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

    def Monitoring(self):
        status = self.get_associated("wlan0")
        self.emit(SIGNAL('update_status(QString)'), status)

    def on_update_status(self, ssid):
        print("New ssid:", ssid)
        if self.connected_ssid != ssid:
            self.connected_ssid = ssid
            self.update_connect_button(self.ssids_w.currentText())
            if ssid != "":
                save_config("wlan0")
                run_dhcp("wlan0")

    def connect_edit_key_field_service(self):
        self.key = self.key_edit.text()
        if self.key != "":
            if self.connected_ssid == self.ssids_w.currentText():
                self.connect.setDisabled(True)
            else:
                self.connect.setDisabled(False)
        else:
            if self.connected_ssid == self.ssids_w.currentText():
                self.connect.setDisabled(True)
            else:
                if self.encr_w.currentText() == 'OPEN':
                    self.connect.setDisabled(False)
                else:
                    self.connect.setDisabled(True)
        if self.encr_w.currentText() == 'OPEN':
            self.key_edit.setDisabled(True)
        else:
            self.key_edit.setDisabled(False)
        if self.ssids_w.currentText() == self.connected_ssid:
            self.connect.setText(translation.get_string('w_wlan_connected'))
        else:
            self.connect.setText(translation.get_string('w_wlan_connect'))

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


class AppButton(QToolButton):

    def __init__(self):
        QToolButton.__init__(self)

        shadow = QGraphicsDropShadowEffect(self)
        shadow.setOffset(QPointF(3, 3))
        self.setGraphicsEffect(shadow)

        self.setToolButtonStyle(Qt.ToolButtonTextUnderIcon)
        self.setObjectName("launcher-icon")

        # hide shadow while icon is pressed
    def mousePressEvent(self, event):
        self.graphicsEffect().setEnabled(False)
        QToolButton.mousePressEvent(self, event)

    def mouseReleaseEvent(self, event):
        self.graphicsEffect().setEnabled(True)
        QToolButton.mouseReleaseEvent(self, event)


class IconGrid(QStackedWidget):

    def __init__(self, apps):
        QStackedWidget.__init__(self)
        self.TILE_STYLE = """
        QPushButton {width: 100px; font-size: 13px; color:white; border-radius: 0; border-style: none; height: 75px}
        QPushButton:pressed {background-color: #123456}
        """
        self.TILE_LABEL = """
        QLabel {text-align: center; font-size: 15px; color:white}
        """
        self.apps = apps
        self.installEventFilter(self)

    def eventFilter(self, obj, event):
        if event.type() == event.Resize:
            self.columns = int(self.width() / 80)
            self.rows = int(self.height() / 80)
            self.createPages()
        return False

    def createPages(self):
        # remove all pages that might already be there
        while self.count():
            w = self.widget(self.count() - 1)
            self.removeWidget(w)
            w.deleteLater()

        icons_per_page = self.columns * self.rows
        page = None
        icons_total = 0
        # create pages to hold every app
        for name, data in sorted(self.apps.items()):
            # create a new page if necessary
            if not page:
                index = 0
                # create grid widget for page
                page = QWidget()
                grid = QGridLayout()
                grid.setSpacing(0)
                grid.setContentsMargins(0, 0, 0, 0)
                page.setLayout(grid)

                # if this isn't the first page, then add a "prev" arrow
                if self.count():
                    but = self.createIcon(os.path.join(LOCAL_PATH, "prev.png"), self.do_prev, 'Previous')
                    grid.addWidget(but, 0, 0, Qt.AlignCenter)
                    index = 1

            executable = data[0]

            # use icon file if one is mentioned in the manifest
            iconname = LOCAL_PATH + '/' + data[1]

            # create a launch button for this app
            but = self.createIcon(iconname, self.do_launch, name, executable)
            grid.addWidget(but, index / self.columns, index % self.columns, Qt.AlignCenter)

            # check if this is the second last icon on page
            # and if there are at least two more icons to be added. Then we need a
            # "next page" arrow
            if index == icons_per_page - 2:
                if icons_total < len(self.apps) - 2:
                    index = icons_per_page - 1
                    but = self.createIcon(os.path.join(LOCAL_PATH, "next.png"), self.do_next, 'Next')
                    grid.addWidget(but, index / self.columns, index % self.columns, Qt.AlignCenter)

            # advance position counters
            index += 1
            if index == icons_per_page:
                self.addWidget(page)
                page = None

        # fill last page with empty icons
        while index < icons_per_page:
            self.addWidget(page)
            empty = self.createIcon()
            grid.addWidget(empty, index / self.columns, index % self.columns, Qt.AlignCenter)
            index += 1
        icons_total += 1

    # handler of the "next" button
    def do_next(self):
        print('NEXT')
        self.setCurrentIndex(self.currentIndex() + 1)

    # handler of the "prev" button
    def do_prev(self):
        print('PREV')
        self.setCurrentIndex(self.currentIndex() - 1)

    # create an icon with label
    def createIcon(self, iconfile=None, on_click=None, appname=None, executable=None):
        if appname == None:
            button = AppButton()
            button.setText(appname)
            button.setProperty("executable", executable)
            return button
        buttonbox = QVBoxLayout()
        iconlabel = QLabel()
        pixmap = QPixmap(iconfile)
        iconlabel.setPixmap(pixmap)
        iconlabel.setAlignment(Qt.AlignCenter)
        txt = QLabel(appname)
        txt.setStyleSheet(self.TILE_LABEL)
        txt.setAlignment(Qt.AlignCenter)
        buttonbox.addWidget(iconlabel)
        buttonbox.addWidget(txt)
        button = QPushButton()
        button.setStyleSheet(self.TILE_STYLE)
        button.setLayout(buttonbox)
        if on_click:
            button.clicked.connect(on_click)
        button.setProperty("executable", executable)
        return button

    def do_launch(self, clicked):
        exec = self.sender().property("executable")
        dialog = exec(w)
        dialog.exec_()


class FtcGuiApplication(TouchApplication):

    def __init__(self, args):
        TouchApplication.__init__(self, args)
        global w
        self.w = TouchWindow(translation.get_string('app_name'))
        self.icons = IconGrid({
            translation.get_string('menu_language'): [LanguageDialog, 'icons/language.png'],
            translation.get_string('menu_network'): [NetworkDialog, 'icons/network.png'],
            translation.get_string('menu_update'): [UpdateCheckDialog, 'icons/update.png']})
        self.vbox = QVBoxLayout()
        self.vbox.addWidget(self.icons)
        self.w.centralWidget.setLayout(self.vbox)
        self.w.show()
        w = self.w
        self.exec_()


if __name__ == "__main__":
    FtcGuiApplication(sys.argv)
