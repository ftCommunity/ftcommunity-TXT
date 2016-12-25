#! /usr/bin/env python3
# -*- coding: utf-8 -*-
# ethernet link monitoring plugin

from PyQt4.QtCore import QCoreApplication
import fcntl, socket, struct

def name():
    return QCoreApplication.translate("PluginEth", "Ethernet")

DEV = "eth0"
SYS_PATH = "/sys/class/net/"+DEV+"/"
FILE_CARRIER = SYS_PATH+"carrier"

def get_carrier():
    try:
        return int(open(FILE_CARRIER,'r').read().strip())
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
    # create icon from png: convert x.png -monochrome x.xpm
    icon_data = [ "16 16 2 1 ", "  c None", ". c white",
                  "                ",
                  "      ....      ",
                  "      ....      ",
                  " .............. ",
                  " .............. ",
                  " ..          .. ",
                  " ..          .. ",
                  " ..          .. ",
                  " ..          .. ",
                  " ..          .. ",
                  " .............. ",
                  " .............. ",
                  " .. .. .. .. .. ",
                  " .. .. .. .. .. ",
                  "                ",
                  "                " ]    
    
    carrier = get_carrier()
    if carrier != None:
        if carrier == 1:
            icon_data[2] = ". c white"
            return icon_data
        else:
            # device present but no link: draw darkgrey
            icon_data[2] = ". c #606060"
            return icon_data
    else:
        return None

def status():
    carrier = get_carrier()

    if carrier != None:
        if carrier == 1:
            ip = get_ip()
            if ip:
                return QCoreApplication.translate("PluginEth", "Up, ") + ip
            else:
                return QCoreApplication.translate("PluginEth", "Up, no IP address")
        else:
            return QCoreApplication.translate("PluginEth", "No link")
    else:
        return QCoreApplication.translate("PluginEth", "Not available")

