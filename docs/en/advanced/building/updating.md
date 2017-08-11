---
nav-title: Updating
nav-pos: 4
---
# Fetch latest changes and make a new build
To fetch changes from the main git repository of ftcommunity-TXT, you have to update your local copy of the repository and then rebuilt the firmware package. (This will be a lot quicker than the initial build, as only the changes will be downloaded and only changed parts will be recompiled).
## Updating the local clone of the git-repository
Change to the directory with the local copy of the repository, then download and integrate the changes:  
``````````cd ~/ftcommunity-TXT`````````` (or wherever else it might be located; this is the path if you followed this wiki from start.)  
``````````git pull``````````
## Re-building the ftcommunity-TXT-firmware
``````````make fischertechnik_TXT_defconfig  ``````````  
``````````make  ``````````

*Note: If the system doesn't work try running
``````````make clean  ``````````  
before continuing with   
``````````make fischertechnik_TXT_defconfig  ``````````  
``````````make  ``````````  
Be aware that in this case the entire system will be rebuilt - which takes a while (for orientaion: ~4hrs on my 2nd generation Intel Core i5 mobile with 2.5 GHz using Ubuntu in a VirtualBox environment)

# Transfering the build output to the SD-Card    
... without removing the card from the TXT by replacing the system while it's running!(yup, that's possible in this case...) 

Important: Start up the TXT-community-firmware.

For the Update-Paths on Linux you need to set a root password first. See here [[TXT password policy|TXT-password-policy#enabeling-the-root-user]] how to do that.

## For the Simple Layout (=plain FAT32-formatted SD-Card)

### Using Windows
Remove the SD-Card from the TXT, place it in a Card-Reader accessible from windows and replace the following three files with the latest version:
- uImage
- am335x-kno_txt.dtb
- rootfs.img

### Using Linux 
(and without removing the SD-Card - of course you can use the windows way on Linux as well)

From a linux system, on the console with the working directory being the ftcommunity-TXT-repository (in the examples used in the wiki: ~/ftcommunity-TXT); and provided 192.168.7.2 is the IP of your TXT:

```ssh root@192.168.7.2 mv /media/sdcard/root.img /media/sdcard/root.old```  
```scp output/images/uImage output/images/am335x-kno_txt.dtb output/images/rootfs.img root@192.168.7.2:/media/sdcard```  

Now, reboot the TXT. Be sure to shut it down by pressing the blue power button until "Shutting down..." is shown in the display. Release the button when you see the text, otherwise it will be turned off the hard way a few seconds later.

## For the Advanced Layout (=partitioned SD-Card)
***
### Note for updating to builds created in 2017
For all manual builds after December 26, 2016, the "Advanced Layout" as described below is no longer in use. If you want to upgrade your current "Advanced Layout", please see https://forum.ftcommunity.de/viewtopic.php?f=33&t=3903 for details (German only, unfortunately).

It might however be easier to just start from scratch by reformatting your SD-Card to use only one FAT32-partition and installing the ftcommunity-TXT-firmware (from your own build) as described here under Simple Layout: [[Configuring-the-microSD-card#simple-layout-of-sd-card]].

The Wiki will be updated only after a new release is published.
***

Adapt the IP (192.168.7.2) to the IP of your TXT  

1. On the TXT  
    *eg. by logging on to the TXT via ssh from another termial on your build system:*  
    ```ssh root@192.168.7.2```  
    1. Create a mount point (needs to be done only once)  
        ```mkdir /boot```  
    1. Mount the boot-partition of the SD-Card:  
        ```mount -t vfat /dev/mmcblk0p1 /boot```  

1. From a terminal on your build-system:   
    Change to the directory with the local copy of the repository on your Linux build system.
    ```cd ~/ftcommunity-TXT``` (or wherever else it might be located; this is the path if you followed this tutorial)  
    Copy am335x-kno_txt.dtb and uImage to the boot-partition just mounted:  
    ```scp output/images/uImage output/images/am335x-kno_txt.dtb root@192.168.7.2:/boot```  

1. On the TXT  
    Unmount the boot-partition:  
    ```umount /boot```  
    ```exit``` (to log out)  

1. From a terminal on your build-system:  
    ```cat output/images/rootfs.tar | ssh root@192.168.7.2 tar xvf - -C /```  
    (as of today (May 2nd, 2016) this step will overwrite the files containing the passwords for the user accounts. So the password for the user 'ftc' will be blank again and 'root' will be disabled - you have to set the passwords again).

1. Now, reboot the TXT. Be sure to shut it down by pressing the blue power button until "Shutting down..." is shown in the display. Release the button when you see the text, otherwise it will be turned off the hard way a few seconds later.

