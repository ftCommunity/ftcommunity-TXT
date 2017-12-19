---
nav-title: Building
nav-pos: 3
---

Usually you don't need to build the firmware yourself. Instead you probably just want to download pre-built [releases](https://github.com/ftCommunity/ftcommunity-TXT/releases).

## Setting up a build system

### Basic Linux/VirtualBox setup
You now need some sort of Linux system to run the build process. 

I used Ubuntu Desktop x64, Version 15.10 (http://www.ubuntu.com/download/desktop); installed in a VirtualBox (https://www.virtualbox.org/wiki/Downloads) running on Windows 10 Pro x64 as Host.  
The steps below have been tested under these conditions.

When creating a new virtual machine, be sure go assign sufficient virtual hard disk space (8GB certainly isn’t enough – I used 32GB HD-space, 3072 MB memory.

### Installing the tools required to build
All further steps are performed on the Linux system running within VirtualBox.

The build process requires mercurial, to get the source files for the firmware, git is required.

Open a terminal (on Ubuntu: right-click on desktop and select “Open terminal”) and install the missing packages:

``````````sudo apt-get install git``````````  
``````````sudo apt-get install mercurial``````````  
*(Note: These are the commands for Ubuntu and other distributions using apt as package management tool. Your distribution might use different tools to install missing packages.)*

## Building the ftcommunity-TXT-firmware from the sources
For all further steps it is assumed that we start out in the user’s home directory ~:  
``````````cd ~``````````  
*Note: So your local copy of the git repository will be located in the directory ~/ftcommunity-TXT (= /home/[INDIVIDUAL_USERNAME]/ftcommunity-TXT).*

Fetch the source code of the ftcommunity-TXT firmware from the git repository:  
``````````git clone https://github.com/ftCommunity/ftcommunity-TXT.git``````````

This creates a new directory named ftcommunity-TXT in the current (=home) directory.   
Change to this directory:  
``````````cd ftcommunity-TXT``````````

Now prepare the build process:  
``````````make fischertechnik_TXT_defconfig``````````  
(this should take only minute or so) 

Now start the actual build process  
``````````make  ``````````
(on first run this will take several hours, depending on CPU and download speed)

Attention: Internet access is required permanently during the build process as further files (several gigabytes) have to be downloaded.  
If you intend to do an offline build and just want to download all sources previously selected via ``make fischertechnik_TXT_defconfig`` then use  
``make source  ``  
before the actual ``make  ``  

### Side remark – Speeding up the build process
To speed up the process, you can run the build process by starting the actual build process with  
``````````BR2_JLEVEL=$(($(nproc)+1)) make``````````  
instead of the plain “make”.

### Side remark – Missing i2c-tools
On my first attempt the build process failed because i2c-tools-3.1.2.tar.bz2 could not be obtained. If this happens, the build process stops. You can then try to download the file manually:  
``````````cd ~/ftcommunity-TXT/dl``````````  
``````````wget http://sources.buildroot.net/i2c-tools-3.1.2.tar.bz2``````````

Then start the build process anew – it will pick up where it left off:  
``````````cd ~/ftcommunity-TXT``````````  
``````````make  ``````````

### Side remark - further details about building embedded systems based on Buildroot (such as the TXT firmware):
https://buildroot.org/downloads/manual/manual.html#_general_buildroot_usage