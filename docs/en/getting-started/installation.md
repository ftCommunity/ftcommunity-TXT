---
nav-title: Installation
nav-pos: 1
---
# Prerequisites: 
* A microSD-Card (microSD or microSDHC, i.e. up to 32GB; please be aware that microSDXC will not work). Size really doesn't matter; the system needs less than 100MB, so even a card with 512 MB would suffice)
* A means to extract files from a ZIP-archive to the microSD-card

# Installation
1. Upgrade the standard firmware to the latest Version 4.2.4
You can find the update to RoboPro 4.2.4 (which will also update the TXT) 
[here at the official Fischertechnik site](https://www.fischertechnik.de/-/media/fischertechnik/fite/service/downloads/robotics/robo-pro/documents/02-demoversion-robopro-english.ashx)

2. Enable booting from MicroSD-card (in Fischertechnik terminology: "Activation Bootloader"). Please follow the official guide which is also available [at the official Fischertechnik site](https://www.fischertechnik.de/-/media/fischertechnik/fite/service/downloads/robotics/txt-controller/documents/activation_bootloaders_english.ashx)

3. Download the latest version of the ftcommunity-TXT-firmware here (at the very bottom of the page):
[https://github.com/ftCommunity/ftcommunity-TXT/releases/latest](https://github.com/ftCommunity/ftcommunity-TXT/releases/latest). At the time of writing this was "ftcommunity-txt-0.9.4.zip". Copy all three files contained therein to the microSD-card (which should be formatted with FAT32. If you don't know what that means and your card has 16GB or less: don't worry, you're set already)

4. Insert the microSD in the TXT and power it up. After a short time the yellow loading indicator should show up as well as the text "community edition" at the bottom half of the screen.

  ![Bootupscreen](https://raw.githubusercontent.com/ftCommunity/ftcommunity-TXT/master/board/fischertechnik/TXT/rootfs/etc/ftc-logo.png)

The first startup will take a while, because the SD-Card needs to be initialized first. Subsequently, the boot process will be a little faster). 
