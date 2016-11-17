#! /usr/bin/env python3
# -*- coding: utf-8 -*-
# plugin checking for RTC interrupts. Keep quiet if there were none

import os

IRQ_SRC = "tps65910-rtc"

name = "RTC"

# check for the number of rtc interrupts
# the interesting line in /proc/interrupts looks like this
# 197:          1  tps65910   6 Edge      tps65910-rtc

def rtc_interrupts():
    try:
        for line in open("/proc/interrupts",'r'):
            parts = line.strip().split()
            if len(parts) >= 6 and parts[5] == IRQ_SRC:
                return int(parts[1])
    except:
        pass

    return 0

def icon():
    # create icon from png: convert x.png -monochrome x.xpm
    icon_data = [ "16 16 2 1 ", "  c None", "# c white",
                  "  ###      ###  ",
                  " #####    ##### ",
                  " ##   ####   ## ",
                  " #  ########  # ",
                  "   ###    ###   ",
                  "  ##   ##   ##  ",
                  "  ##   ##   ##  ",
                  " ##    ##    ## ",
                  " ##    ####  ## ",
                  " ##    ####  ## ",
                  " ##          ## ",
                  "  ##        ##  ",
                  "  ##        ##  ",
                  "   ###    ###   ",
                  "    ########    ",
                  "   #  ####  #   " ]
    
    if rtc_interrupts() > 0:
        return icon_data
    else:
        return None

def status():
    if rtc_interrupts() > 0:
        return str(rtc_interrupts())+" events"
    else:
        return None
