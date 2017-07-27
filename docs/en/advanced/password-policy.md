---
nav-title: Password Policy
nav-pos: 1
---

# Useres, passwords and root access on the TXT


## Out-of-box status of user accounts
By default, the ftcommunity-TXT comes with two relevant users with the user names '**ftc**' and '**root**'. (*A third user - 'ROBOPro' is only included for compatibility reasons.*)

- user 'ftc' has **no password**
- user 'root'is **disabled**

## The "two factor" authentication
The Community Firmware (*since version 0.9.3*) has a **"two-factor authentication"**. To connect to the TXT by every internet you have to accept on the display!

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