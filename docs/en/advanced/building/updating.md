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


## Copy files from your computer
Remove the SD-Card from the TXT, place it in a Card-Reader in your computer and replace the following three files with the latest version:
- uImage
- am335x-kno_txt.dtb
- rootfs.img

## Update without removing the SD-Card

From a linux system (or with any other SSH-client), on the console with the working directory being the ftcommunity-TXT-repository (in the examples used in the wiki: ~/ftcommunity-TXT); and provided 192.168.7.2 is the IP of your TXT:

```ssh root@192.168.7.2 mv /media/sdcard/root.img /media/sdcard/root.old```  
```scp output/images/uImage output/images/am335x-kno_txt.dtb output/images/rootfs.img root@192.168.7.2:/media/sdcard/boot```  

Now, reboot the TXT. Be sure to shut it down by pressing the blue power button until "Shutting down..." is shown in the display. Release the button when you see the text, otherwise it will be turned off the hard way a few seconds later.

