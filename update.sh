#!/bin/sh
#Updates the local files and compiles the firmware
cd ~/ftcommunity-TXT
make fischertechnik_TXT_defconfig
BR2_JLEVEL=$(($(nproc)+1)) make
