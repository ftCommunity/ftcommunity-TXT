#!/usr/bin/python
import os
import sys
import time
import getpass

user = getpass.getuser()
print 'Welcome to ft-community-TXT-Frimware-Generation and Update-Kit'
print 'Be sure your internet connection is workin'
print 'Current User: ' + user
if user != "root":
	print 'Not logged in as root'
	print 'Script ended'
	print 'Try again as root'
	sys.exit()
else:
	print 'You are logged in as root'
	print 'Script will be continued'

x = "N"
while x == "N":
	print 'Current medias'
	os.system("lsblk")
	print 'Please enter path to SD-card without numbers at the end. exp.: /dev/sdb:'
	sd_card = raw_input("Path to SD: ")
	print 'Path to SD-card: ' + sd_card
	print 'Is this right? [J/N]'
	x = raw_input("[J/N]: ")

print 'Be sure that al prtitions of SD-card are unmounted. Unmount them by typing: umount [mount-point]'
print 'Are all partitions unmounted?'
os.system("lsblk")
x = raw_input("[J/N]: ")
if x == "N":
	sys.exit()

print 'Installing packages!'
os.system("apt-get -y install git mercurial")
print 'Update repository!'
os.system("git pull")
print 'Compile OS!'
os.system("wget -P dl http://sources.buildroot.net/i2c-tools-3.1.2.tar.bz2")
os.system("make fischertechnik_TXT_defconfig")
os.system("BR2_JLEVEL=$(($(nproc)+1)) make")

print 'Buildroot finished!'
print 'Formatting SD-card!'
print 'Answer all questions with Y'

os.system("parted " + sd_card + " mklabel msdos")
os.system("parted -a optimal " + sd_card + " mkpart primary fat32 1MB 33MB")
os.system("parted -a optimal " + sd_card + " mkpart primary ext2 34MB 100%")
os.system("parted " + sd_card + " set 1 boot on")
os.system("mkfs.vfat -n BOOT " + sd_card + "1")
os.system("mkfs.ext4 -L ROOT " + sd_card + "2")

print 'Formatting completed!'
#creating mountpoint
os.system("mkdir mnt")

os.system("mount " + sd_card + "1 mnt")
os.system("cp output/images/uImage output/images/am335x-kno_txt.dtb mnt/")
os.system("umount mnt")

os.system("mount " + sd_card + "2 mnt")
os.system("tar xvf output/images/rootfs.tar -C mnt/")
os.system("umount mnt")

print 'Everything is finished. Plug-out the SD-card, put it into the TXT and be happy!'