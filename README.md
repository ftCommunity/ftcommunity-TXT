# Community edition of the standard firmware for the FT-TXT.

## Quick start

Please use the [installation quide](http://cfw.ftcommunity.de/ftcommunity-TXT/en/getting-started/installation.html) or the [Deutsche Kurzanleitung (installation guide in german)](http://cfw.ftcommunity.de/ftcommunity-TXT/de/getting-started/installation.html) for a quick start. More infos can be found on the [web site](http://cfw.ftcommunity.de/)

## What is this and why would i want this?

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

Most discussions around the community firmware take place in the [FTCommunity forum)](http://forum.ftcommunity.de/viewforum.php?f=8). This is a german forum but english contributions are welcome.

# Usage

Two simple steps are needed to run the community firmware on your TXT:

 1. A correctly prepared micro SD card
 2. Configure the TXT to boot from SD card

Both steps are simple and risk-free as removing the SD card will always give you the original firmware back. 

# Step 1: Preparing the SD card

You'll need a micro SD card. A size of 2 or 4 GB is recommended.

## Use pre-built images

Pre-built images for a hassle free quick start have been [released](https://github.com/ftCommunity/ftcommunity-TXT/releases).

For beginners it's recommended to use the pre-built releases.

For the latest bleading-edge versions you might want to build the firmware yourself as explained below.

## Build the firmware

Load the configuration for the TXT by typing:

```
make fischertechnik_TXT_defconfig
```

Afterwards a single

```
make
```

will build the entire root file system and the kernel and place the resulting files in the `output/images` directory.

## Prepare SD Card
You need an empty micro SD card for the ftcommunity firmware.

Make sure that the SD card contains only ond partition, and that this is formatted as FAT32 (most fresh SD cards should already have this layout). Then copy the files `output/images/uImage`, `output/images/am335x-kno_txt.dtb` and `output/images/rootfs.img` to the SD card.

# Step 2: Configure the TXT to boot from SD card

Make sure you are running at least version [4.2.4 of the official firmware](http://www.fischertechnik.de/home/downloads/Computing.aspx). You then only need to follow the [instructions provided by Fischertechnik](http://www.fischertechnik.de/ResourceImage.aspx?raid=10278).

More details and a brief set of instructions can be found in our [web site](https://cfw.ftcommunity.de/ftcommunity-TXT/en/getting-started/).

# Run the ftcommunity firmware

Switch off the TXT, insert the SD card with the ftcommunity firmware in the SD card slot and restart the TXT. If you see the note "community edition" on the bootup splash screen, the ftcommunity firmware is running.

The ftcommunity firmware enables ssh login via USB by default, network settings for USB are the same as with the original firmware: The TXT has address 192.168.7.2, the host computer has address 192.168.7.1. On most systems, the host computer address should be set up automatically when you connect the USB cable.

You can log in to the TXT either via [serial console](https://github.com/ftCommunity/ftcommunity-TXT/wiki/Serial-Console) or using ssh. 

In both cases, the user name is "ftc". By default, the *ftc* user can log in without a password. It is strongly recommended to set a password for the *ftc* user when you first log in.

The *ftc* user may use `sudo` to execute commands as root.

# Switch back to original firmware

Shut down the TXT and remove the SD card with the ftcommunity firmware. On the next start, the TXT will boot the original Fischertechnik firmware.
