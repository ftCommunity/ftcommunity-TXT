#!/bin/sh
echo "Setting environment for SD card boot"
fw_setenv loadsduimg "fatload mmc 0 0x80200000 uImage"
fw_setenv loadsddtb "fatload mmc 0 0x80F00000 am335x-kno_txt.dtb"
fw_setenv setsdargs "setenv bootargs fbtft_device.name=txt_ili9341 fbtft_device.fps=10 console=ttyO0,115200 root=/dev/mmcblk0p2 rw rootwait quiet"
fw_setenv bootboth "run reset_wl18xx; mtdparts default; nand read 0x80200000 NAND.uImage; nand read 0x80F00000 NAND.dtb; setenv bootargs fbtft_device.name=txt_ili9341 fbtft_device.fps=10 console=ttyO0,115200 ubi.mtd=10 root=ubi0:rootfs rootfstype=ubifs rootwait quiet; run loadsduimg loadsddtb setsdargs; fdt addr 0x80F00000; run opp; bootm 0x80200000 - 0x80F00000"

echo "Verifying environment!"
if [ "`fw_printenv loadsduimg`" != "loadsduimg=fatload mmc 0 0x80200000 uImage" ]; then
    echo "Verification of loadsduimg failed!"
    exit 1
fi

if [ "`fw_printenv loadsddtb`" != "loadsddtb=fatload mmc 0 0x80F00000 am335x-kno_txt.dtb" ]; then
    echo "Verification of loadsddtb failed!"
    exit 1
fi

if [ "`fw_printenv setsdargs`" != "setsdargs=setenv bootargs fbtft_device.name=txt_ili9341 fbtft_device.fps=10 console=ttyO0,115200 root=/dev/mmcblk0p2 rw rootwait quiet" ]; then
    echo "Verification of setsdargs failed!"
    exit 1
fi

if [ "`fw_printenv bootboth`" != "bootboth=run reset_wl18xx; mtdparts default; nand read 0x80200000 NAND.uImage; nand read 0x80F00000 NAND.dtb; setenv bootargs fbtft_device.name=txt_ili9341 fbtft_device.fps=10 console=ttyO0,115200 ubi.mtd=10 root=ubi0:rootfs rootfstype=ubifs rootwait quiet; run loadsduimg loadsddtb setsdargs; fdt addr 0x80F00000; run opp; bootm 0x80200000 - 0x80F00000" ]; then
    echo "Verification of bootboth failed!"
    exit 1
fi

echo "Environment looks good. Enabling SD boot"
fw_setenv bootcmd "run bootboth"
