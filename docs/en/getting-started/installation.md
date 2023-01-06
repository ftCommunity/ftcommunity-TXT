---
nav-title: Installation
nav-pos: 1
---
# Prerequisites: 
* A microSD card (microSD or microSDHC, i.e. up to 32GB; please be aware that microSDXC will not work). Size really doesn't matter; the system needs less than 100MB, so even a card with 512 MB would suffice)
* A means to extract files from a ZIP-archive to the microSD-card

# Installation
1. Upgrade the standard firmware to the version 4.2.4 or later (recommended version is the most recent version provided by Fischertechnik, currently 4.4.4). The standard firmware upgrade is handled by RoboPro, you will find the current version of RoboPro (which contains the latest TXT firmware) 
[here at the official Fischertechnik site](https://www.fischertechnik.de/-/media/fischertechnik/fite/service/downloads/robotics/robo-pro/documents/update-robopro.ashx)

2. Enable booting from MicroSD-card (in Fischertechnik terminology: "Activation Bootloader"). For standard firmware version 4.4.3 or later, navigate to _Settings / Security_ in the TXT GUI and activate the _Boot SD_ switch. For standard firmware 4.2.4, please follow the [instructions provided by Fischertechnik](https://www.fischertechnik.de/-/media/fischertechnik/fite/service/downloads/robotics/txt-controller/documents/activation_bootloaders_english.ashx)

3. On your computer: Download the latest version of the ftcommunity-TXT-firmware here (at the very bottom of the page):
[https://github.com/ftCommunity/ftcommunity-TXT/releases/latest](https://github.com/ftCommunity/ftcommunity-TXT/releases/latest). At the time of writing this was "ftcommunity-txt-0.9.5.zip". Use a zip program to unpack the zip file. Copy all three files contained therein to the microSD-card (which should be formatted with FAT32. If you don't know what that means and your card has 16GB or less: don't worry, you're set already)

4. Insert the microSD in the TXT and power it up. After a short time the yellow loading indicator should show up as well as the text "community edition" at the bottom half of the screen.

  ![Bootupscreen](https://raw.githubusercontent.com/ftCommunity/ftcommunity-TXT/master/board/fischertechnik/TXT/rootfs/etc/ftc-logo.png)

The first startup will take a while, because the SD card needs to be initialized first. Subsequently, the boot process will be faster.

# Update

To update a SD card to the newest CFW version, you extract it from your TXT and insert it into the SD slot of your computer. Now replace the following three files with the current version (extract from the zipfile):

    uImage
    am335x-kno_txt.dtb
    rootfs.img
    
All apps and data, which are currently stored on the SD card will be preserved.

