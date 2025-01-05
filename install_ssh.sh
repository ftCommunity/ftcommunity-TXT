#!/bin/bash
set -e

[[ $# == 1 ]] || { echo "$0 hostname"; exit 1; }

txt=$1

files="am335x-kno_txt.dtb uImage rootfs.img"
boot=/media/sdcard/boot

read -s -p "Password for root@$txt?" p
echo

cd output/images/

echo "Preparing"
export SSHPASS=$p
sshpass -e ssh root@$txt mkdir -p $boot/new $boot/old

echo "Copying"
sshpass -e rsync -tv --progress $files root@$txt:$boot/new

echo "Activating"
sshpass -e ssh root@$txt "cd $boot && mv $files old && mv new/* ."
echo "Success, rebooting"
sshpass -e ssh root@$txt reboot
