---
nav-title: Prerequisites
nav-pos: 1
---

# Prerequisites

You need a few things to be able to build the Community-Firmware

## Needed:
1.  A Linux-System with at least 20 GB free hard disk space (*as well as a fast CPU and a fast internet connection*)

    (***The following how-to is based on Ubuntu, but should work on other distributions as well***).

2. A microSD-card on which the ftcommunity-TXT-firmware can be installed. Any SD(HC) microSD-Card should work! 

	(*Cards with other technical specifications (eg. microSD-XC) have not been tested*). 
	To  be safe it is recommended to use a microSD(HC)-Card with 32GB or less.

    As the ftcommunity-TXT-firmware itself only uses as little as 200MB of cardspace, even a 2GB-card is more than sufficient.

3. A ssh-client to connect to the TXT:
	-  on Windows [PuTTY](http://www.chiark.greenend.org.uk/~sgtatham/putty/download.htm)
	-  on iOS eg. “Serverauditor” could be used
4. A network connection to the TXT:
    * USB-based network connection: IP 192.168.7.2
    * WLAN connection: IP 192.168.8.2
        * WLAN might need to be switched on first: “Settings” -> “Network” -> WLAN Setup
        * in this mode, the TXT serves as an access point
        * the network SSID is the name of the TXT displayed on the main screen
        * the WPA-Key can be found in the menu “Settings” -> “Network” -> WLAN Setup
    * BT-based network connection IP 192.168.9.2
        * BT needs to be switched on first: “Settings” -> “Network”
