---
nav-title: Password Policy
nav-pos: 1
---

# Users, passwords and root access on the TXT


## Out-of-box status of user accounts
By default, the ftcommunity-TXT comes with two relevant users with the user names '**ftc**' and '**root**'. (*A third user - 'ROBOPro' is only included for compatibility reasons.*)

- user 'ftc' has **no password**
- user 'root'is **disabled**

## The "two factor" authentication
The Community Firmware (*since version 0.9.3*) has a **"two-factor authentication"**. To connect to the TXT by any network you have to accept the connection on the display of your TXT.

This means that you have to have access to your TXT's touchscreen to log on via SSH.

To change this behavior, add a password for the root user (see below for instructions).

## Enabeling the root user
To enable the user ´root´, you have to set a password for this user:


Log on to the TXT from any Linux console (or using any SSH-client, eg. PuTTY on Windows) as user 'ftc':

```ssh ftc@192.168.7.2```  

No password will be required. However, you'll have to klick "OK" in the confirmation dialog shown on the TXT screen (see above).

Within the SSH-Session, i.e. on the TXT:    

Simply type:   ```sudo passwd root ```  

You will again be prompted for a confirmatory click on the TXT-display to permit the "sudo"-command.
When setting the password for root, you will have to retype the password. 
You can now build a SSH connection to your TXT as user root using this password. There will be no confirmation dialog on the TXT screen.
