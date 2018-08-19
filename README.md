# Community edition of the standard firmware for the FT-TXT.

## Quick start

Please use the [installation quide](http://cfw.ftcommunity.de/ftcommunity-TXT/en/getting-started/installation.html) or the [Deutsche Kurzanleitung (installation guide in german)](http://cfw.ftcommunity.de/ftcommunity-TXT/de/getting-started/installation.html) for a quick start. More infos can be found on the [web site](http://cfw.ftcommunity.de/)

## What is this and why would I want this?

The [Fischertechnik TXT controller](https://www.fischertechnik.de/en/products/playing/robotics/522429-robotics-txt-controller) is a Linux driven computerized brick for the Fischertechnik construction toy.

![TXT](https://raw.githubusercontent.com/wiki/ftCommunity/ftcommunity-TXT/txt_cw.jpg)

The Fischertechnik TXT comes pre-installed with a Linux based firmware. This firmware is slightly outdated
(the base system consist of parts which are all at least two years old) and doesn't make full use of the
hardware capabilities of the TXT.

The community firmware aims to change this. It replaces the entire system with much newer components including 
an updated Linux kernel and updates for all system components. Furthermore it provides a fresh user interface
and focusses on connectivity in general. It can connect to your home WiFi, to other Fischertechnik Components, to custom made controllers like [ftDuino](https://github.com/harbaum/ftduino), to foreign parts like e.g. Lego WeDo
bricks, and much more.

The community firmware doesn't replace the built-in original firmware. Instead it is installed on a regular micro-SD card
and provides a means to leave the original untouched which being used. Simply pull out the SD card containing the
community firmware to bring your TXT back into factory state.

## (German) Forum 

Most discussions around the community firmware take place in the [FTCommunity forum](http://forum.ftcommunity.de/viewforum.php?f=8). This is a german forum but english contributions are welcome.

# Installation and Usage

See [the getting started guide](https://cfw.ftcommunity.de/ftcommunity-TXT/en/getting-started/) for instructions on how to install and use the community firmware.

# Build the firmware from source
In the toplevel directory, type

```
make
```

This will build the entire root file system and the kernel and place the resulting files in the `buildroot/output/images` directory.

After the build has finished, copy the files `buildroot/output/images/uImage`, `buildroot/output/images/am335x-kno_txt.dtb` and `buildroot/output/images/rootfs.img` to an empty, FAT32 formatted SD card.

# Switch back to original firmware

Shut down the TXT and remove the SD card with the ftcommunity firmware. On the next start, the TXT will boot the original Fischertechnik firmware.
