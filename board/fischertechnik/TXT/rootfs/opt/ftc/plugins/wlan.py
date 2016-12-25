#! /usr/bin/env python3
# -*- coding: utf-8 -*-

from PyQt4.QtCore import QCoreApplication
import fcntl, socket, struct

def name():
    return QCoreApplication.translate("PluginWlan", "WLAN")

DEV = "wlan0"
SYS_PATH = "/sys/class/net/"+DEV+"/"
FILE_OPERSTATE = SYS_PATH+"operstate"

def get_operstate():
    try:
        return open(FILE_OPERSTATE,'r').read().strip()
    except:
        return None

def _ifinfo(sock, addr, ifname):
    iface = struct.pack('256s', bytes(ifname[:15], "UTF-8"))
    info  = fcntl.ioctl(sock.fileno(), addr, iface)
    return socket.inet_ntoa(info[20:24])

def get_ip():
    try:
        SIOCGIFADDR = 0x8915
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        return _ifinfo(s, SIOCGIFADDR, DEV)
    except:
        return None

def icon():
    icon_data = [ "16 16 2 1 ", "  c None", ". c white",
                  "                ",
                  "                ",
                  "     ......     ",
                  "   ..........   ",
                  "  ...      ...  ",
                  " ..          .. ",
                  " .    ....    . ",
                  "    ........    ",
                  "   ...    ...   ",
                  "   .        .   ",
                  "       ..       ",
                  "      ....      ",
                  "      ....      ",
                  "       ..       ",
                  "                ",
                  "                " ]
    
    operstate = get_operstate()
    if operstate:
        if operstate == "up":
            # device up: draw white
            icon_data[2] = ". c white"
            return icon_data

        elif operstate == "dormant" or operstate == "down":
            # device present but no link: draw darkgrey
            icon_data[2] = ". c #606060"
            return icon_data

        else:
            # device present but unknown operstate
            icon_data[2] = ". c red"
            return icon_data
        
    else:
        return None

def status():
    operstate = get_operstate()
    if operstate:
        if operstate == "up":
            ip = get_ip()
            if ip:
                return QCoreApplication.translate("PluginWlan", "Up, ") + ip
            else:
                return QCoreApplication.translate("PluginWlan", "Up, no IP address")

        else:
            return operstate
    else:
        return QCoreApplication.translate("PluginWlan", "Not available")
