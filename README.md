# This is the community edition of the standard firmware for the FT-TXT.

The ftcommunity firmware aims to provide enhancements that are not (or not yet) in the standard firmware, and at the same time to be fully compatible with the latest standard firmware.

# What is this and why would i want this?

The Fischertechnik TXT controller is a Linux driven computerized brick for the Fischertechnik construction toy.

![TXT](https://raw.githubusercontent.com/wiki/ftCommunity/ftcommunity-TXT/txt_cw.jpg)

The Fischertechnik TXT comes pre-installed with a Linux based firmware. This firmware is slightly outdated
(the base system consist of parts which are all at least two years old) and doesn't make full use of the
hardware capabilities of the TXT. At the time of writing the original TXT firmware doesn't even allow to use
the built-in WLAN capabilities to connect to your home WiFi.

The community firmware aims to change this. It replaces the entire system with much newer components including 
an updated Linux kernel and updates for all system components. Furthermore it provides a fresh user interface
and focusses on connectivity in general. It connect to your home WiFi as well as e.g. via USB to your Lego WeDo
bricks and much more.

There are still limitations which are due to the fact that some vendor
specific closed source core components have not yet been replaced by
open components. Especially compatibility to the original RoboPro
software used to program and control the TXT from a PC is limited. The
firmware community aims to restore full compatibility as well as
moving beyond the RoboPro capabilities by providing support for additional 
programming environments like e.g. [Snap! or Scratch](https://en.wikipedia.org/wiki/Scratch_%28programming_language%29)

# Usage

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

You need an empty micro SD card for the ftcommunity firmware. Create two partitions on the SD card. The first partition should be about 20-40 MB in size and must be formatted as `FAT`, the second partition can use the rest of the available space on the SD card and must be formatted as `ext4`.

The following commands will do this on a linux system where the SD card slot is named `
/dev/mmcblk0`. *Make sure this is really the empty SD card, the following commands will destroy all data on `/dev/mmcblk0`*:

```
parted /dev/mmcblk0 mklabel msdos
parted -a optimal /dev/mmcblk0 mkpart primary fat32 1MB 33MB
parted -a optimal /dev/mmcblk0 mkpart primary ext2 34MB 100%
parted /dev/mmcblk0 set 1 boot on
mkfs.vfat -n BOOT /dev/mmcblk0p1
mkfs.ext4 -L ROOT /dev/mmcblk0p2
```

Now, copy the files `output/images/uImage` and `output/images/am335x-kno_txt.dtb` to the first partition of the SD card:
```
mount /dev/mmcblk0p1 /mnt
cp output/images/uImage output/images/am335x-kno_txt.dtb /mnt/
umount /mnt
```

Finally, unpack `output/images/rootfs.tar` to the second partition on the SD card:
```
mount /dev/mmcblk0p2 /mnt
tar xvf output/images/rootfs.tar -C /mnt/
umount /mnt
```

Note: On most linux systems, you will need to run all of these commands as root.

## Reconfigure the TXT to allow booting from SD Card

Before you can run the ftcommunity firmware, you will need to reconfigure the TXT to allow starting a firmware from the SD card. This needs only to be done once.

To reconfigure the TXT, start the TXT with the original Fischertechnik firmware and log into the TXT as root (see [here](http://www.fischertechnik.de/PortalData/1/Resources/downloads/documents/TXT_Security_Information.pdf) for instructions).

As root, execute this command:
```
fw_setenv bootcmd "run sdboot;run nandboot"
```

**Hinweis: Bitte überprüfen Sie das Kommando genauestens. Fehler im 'bootcmd' wird verhindern, dass der TXT booten kann. In diesem Fall muss die Korrektur über die [serielle Konsole](https://github.com/ftCommunity/ftcommunity-TXT/wiki/Serial-Console) mit Hilfe eines speziellen Adapters vorgenommen werden.**

**Note: Compare this command carefully and do not run it if it doesn't exactly match the line shown here. Changing 'bootcmd' with defective settings will brick your TXT and you will need to set up [serial console access](https://github.com/ftCommunity/ftcommunity-TXT/wiki/Serial-Console) to the TXT to fix the boot loader configuration and make the TXT usable again.**

## Run the ftcommunity firmware

Switch off the TXT, insert the SD card with the ftcommunity firmware in the SD card slot and restart the TXT. If you see the note "community edition" on the bootup splash screen, the ftcommunity firmware is running.

The ftcommunity firmware enables ssh login via USB by default, network settings for USB are the same as with the original firmware: The TXT has address 192.168.7.2, the host computer has address 192.168.7.1. On most systems, the host computer address should be set up automatically when you connect the USB cable.

You can log in to the TXT either via [serial console](https://github.com/ftCommunity/ftcommunity-TXT/wiki/Serial-Console) or using ssh. 

In both cases, the user name is "ftc". By default, the *ftc* user can log in without a password. It is strongly recommended to set a password for the *ftc* user when you first log in.

After setting a password, the *ftc* user may use `sudo` to execute commands as root.

## Switch back to original firmware

Shut down the TXT and remove the SD card with the ftcommunity firmware. On the next start, the TXT will boot the original Fischertechnik firmware.
