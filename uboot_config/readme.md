# TXT uboot config update script

This script changes the UBoot setup of a Fischertechnik TXT to let it boot from SD card.

<font color="red">This script changes some vital settings of the device. A failure may result in the device becoming unusable and requiring professional service. You have been warned!!!</font>

## Prerequisites

You need to have root access to your TXT and a working network connection. Only TXT running original firmware 4.2.3.0 has been tested with this script. Please be extra careful when running it on a different version.

## Usage with a command line SSH client (e.g. from a Linux PC)

You need to copy this script onto your TXT, e.g. into the /tmp directory. When using a command line ssh client on e.g. a Linux PC with the TXT being connected via USB the follwing line will do this:

```
scp uboot_env_enable_sd_boot.sh root@192.168.7.2:/tmp
```

Afterwards the script has to be executed. This can also be done with the ssh command line client:

```
$ ssh root@192.168.7.2 /tmp/uboot_env_enable_sd_boot.sh
root@192.168.7.2's password: 
Setting environment for SD card boot
Verifying environment!
Environment looks good. Enabling SD boot
```

## Usage with Putty

TBD
