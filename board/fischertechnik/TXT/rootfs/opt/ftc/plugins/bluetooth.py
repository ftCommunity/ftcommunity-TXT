#! /usr/bin/env python3
# -*- coding: utf-8 -*-

from PyQt4.QtCore import QCoreApplication
import fcntl, socket

def name():
    return QCoreApplication.translate("PluginBluetooth", "Bluetooth")

def hci0_up():
    # AF_BLUETOOTH = 31, BTPROTO_HCI = 1
    try:
        s = socket.socket(31, socket.SOCK_RAW, 1)
        di = bytearray(92)   # hci0
        fcntl.ioctl(s.fileno(), 0x800448d3, di)
        return (di[16] & 1) != 0
    except:
        return None

def icon():
    icon_data = [ "16 16 2 1 ", "  c None", ". c white",
                  "                ",
                  "        .       ",
                  "        ..      ",
                  "        . .     ",
                  "     .  .  .    ",
                  "      . . .     ",
                  "       ...      ",
                  "        .       ",
                  "       ...      ",
                  "      . . .     ",
                  "     .  .  .    ",
                  "        . .     ",
                  "        ..      ",
                  "        .       ",
                  "                ",
                  "                " ]
    
    state = hci0_up()
    if state == True:
        # device up: draw white
        icon_data[2] = ". c white"
        return icon_data

    elif state == False:
        # device present but no link: draw darkgrey
        icon_data[2] = ". c #606060"
        return icon_data

    else:
        return None

def status():
    state = hci0_up()
    if state == True:
        return QCoreApplication.translate("PluginBluetooth", "Enabled")
    elif state == False:
        return QCoreApplication.translate("PluginBluetooth", "Disabled")
    else:
        return QCoreApplication.translate("PluginBluetooth", "Not available")
