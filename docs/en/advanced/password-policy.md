---
nav-title: Password Policy
nav-pos: 1
---

# Useres, passwords and root access on the TXT


## Out-of-box status of user accounts
By default, the ftcommunity-TXT comes with two relevant users with the user names 'ftc' and 'root'. (A third user - 'ROBOPro' is only included for compatibility reasons and of no further relevance here.)

- user 'ftc'     has no password
- user 'root'     is disabled

## The "two factor" authentication
Community-firmware-versions built after September 21, 2016 show a confirmation dialog on the screen of the TXT when the user 'ftc' logs on via SSH and when a sudo-command is executed. ([https://forum.ftcommunity.de/viewtopic.php?f=8&t=3429&start=560#p26486](Communityforum)).

This means that you have to have access to your TXT's touchscreen to log on via SSH.

To change this behavior, add a password for the root user (see below for instructions).

## Enabeling the root user
To enable the root user, you have to set a password for the user ftc first; then you're able to set a password for user 'root':

Set a password for user 'ftc':
Log on to the TXT from any Linux console (or using any SSH-client, eg. PuTTY on Windows) as user 'ftc' 
```ssh ftc@192.168.7.2```  
No password will be required. However, you'll have to klick "OK" in the confirmation dialog shown on the TXT screen (see above).

Within the SSH-Session, i.e. on the TXT:    

Simply type
    ```sudo passwd root ```  

You will again be prompted for a confirmatory click on the TXT-display to permit the "sudo"-command.

> ### For older versions
> Should this fail, you may have to set a password for the user ftc first (particularly in fw-builds older than September 28, 2016): 

> 1. Set a password for the current user (=ftc)  
>      ```passwd ```   
>      and follow the instructions  

> 2. Set a password for the user 'root'  
>     ```sudo passwd root ```  

>     Attention: You'll first be prompted for a password by _sudo_ - this means you have to enter the password of the current user (ftc) - i.e. the one you just set for 'ftc'

Now you should be able to log in to the TXT as root user as well - e.g. to run updates of the TXT over the air.

Try if you can log on as root using
```ssh root@192.168.7.2 ```  
and your new root password.