---
nav-title: Preparing the TXT
nav-pos: 2
---

## Update to latest official firmware for TXT-Controller 
The first step should be to update the official firmware to the latest version. The easiest way to achieve this is updating ROBOPro to its latest version and using the built-in firmware update method.

The latest Version of ROBOPro is available on the fischertechnik website under “Downloads” -> “Robotics (Software und mehr)” -> Section "ROBO Pro Software" (http://www.fischertechnik.de/home/downloads/Computing.aspx).

The latest version available on October 14, 2016 was Version 4.2.4. 

Direct download (ca. 222 MB) via http://www.fischertechnik.de/ResourceImage.aspx?raid=10274

## Enable booting from micro SD card

### Using ROBOPro 4.2.4 or later
As of ROBOPro 4.2.4, booting from SD card can be enabled by following the instructions from Fischertechnik in 
* http://www.fischertechnik.de/en/PortalData/1/Resources/downloads/documents/Activation_Bootloaders_english.pdf (English)
* http://www.fischertechnik.de/PortalData/1/Resources/downloads/documents/Freischaltung_des_Bootloaders_deutsch.pdf (German). 

Summary:

* Establish a network connection to the Connect to the TXT via SSH (see [[Prerequisites]] for IP-Addresses)
    * Login name: ROBOPro
    * Password: ROBOPro

* Execute the following command:  

    ``````````
    sudo /usr/sbin/boot_sd_nand
    ``````````

### For older versions of ROBOPro
If you are using an older version of ROBOPro, booting from SD card has to be enabled manually as the root user on the TXT.
#### Get TXT’s root password
Background: The root password for the embedded Linux on the TXT controller is set randomly at manufacture. To make the changes enabling booting the community firmware from microSD, root access to the TXT is required – thus we need the password. 

The password can be displayed by the TXT on its info-screen; but only after root-password display was enabled:

* Establish a network connection to the Connect to the TXT via SSH (see [[Prerequisites]] for IP-Addresses)
    * Login name: ROBOPro
    * Password: ROBOPro

* Execute the following command:  
    ``````````
    echo "showroot=1" > .TxtAccess.ini
    ``````````

* Reboot the TXT

Now you can read the root password in “Settings” -> “Info” (bottom Entry in the Info menu is now “Root password”.

Further details about enabling/ disabling root password display can be found on the fischertechnik website under “Downloads” -> “Robotics (Software und mehr)” -> Section "TXT" -> “[PDF] TXT Controller Root-Zugang“ (direct link: http://www.fischertechnik.de/ResourceImage.aspx?raid=8402)

#### Modify Boot-Options on TXT


Before you can run the ftcommunity firmware, you will need to reconfigure the TXT to allow starting a firmware from the SD card. This needs to be done only once.

**Attention: This is the only step where the TXT could be damaged, so be sure to execute the commands exactly as shown.**

* Log on to the TXT via SSH (see above under “Get TXT’s root password”)
  * Username: root
  * Password: The TXT root password obtained above
* Then, execute the following four command (beginning with fw_setenv and including the " at the end):

```
fw_setenv bootcmd "run sdboot;run nandboot"
```

Note: Compare the line carefully and do not execute this command until it matches exactly the line above. Changing 'bootcmd' with defective settings will brick your TXT and you will need to set up serial console access to the TXT to fix the boot loader configuration and make the TXT usable again.
