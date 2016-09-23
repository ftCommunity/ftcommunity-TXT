#! /usr/bin/env python3
# -*- coding: utf-8 -*-
# plugin checking for presence of physical keyboard

import os

name = "Keyboard"

def keyboard_present():
    try:
        for i in os.listdir("/dev/input/by-id"):
            if i[-4:] == "-kbd":
                return True
    except:
        pass

    return False

def icon():
    # create icon from png: convert x.png -monochrome x.xpm
    icon_data = [ "16 16 2 1 ", "  c None", ". c white",
                  "                ",
                  "                ",
                  "                ",
                  "                ",
                  "                ",
                  " . . . . . . .. ",
                  "              . ",
                  " .. . . . . . . ",
                  "                ",
                  " ... . . . . .. ",
                  "                ",
                  "  .. ...... ..  ",
                  "                ",
                  "                ",
                  "                ",
                  "                " ]
    
    if keyboard_present():
        return icon_data
    else:
        return None

def status():
    if keyboard_present():
        return "Available"
    else:
        return "Not available"
