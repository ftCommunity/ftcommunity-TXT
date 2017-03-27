---
nav-title: Development
---
# Programming in Python: Development

Warning: This tutorial is outdated and needs to be updated!

[[Tutorial 1: The first app]] introduced a basic first app. The whole development cycle used the standard way to upload the app to the TXT via the Web interface. Unfortunately this way of developing an app is not very convenient. This tutorial will present some useful shortcuts to speed development up.

# App update via SSH

During development usually only single files are being changed and it's not necessary to remove and re-install the entire app on the TXT during the develoment phase. Instead single files can be uploaded to the TXT via SSH.

With a command line SSH client the `test.py` from tutorial 1 can be updated like this if the IP address of your TXT is 192.168.0.12 (use the TXTs netinfo app to find the ip address of your TXT):

```
scp test.py root@192.168.0.12:/opt/ftc/apps/user/191fe5a6-313b-4083-af65-d1ad7fd6d281/
```

This will copy the new `test.py` file into the correct directory on the TXT. The directory target name on the TXT is the uuid from the manifest in the ZIP file you initially uploaded. E.g. if your apps manifest contained the line  ```uuid: 191fe5a6-313b-4083-af65-d1ad7fd6d281``` then the target directory is `/opt/ftc/apps/user/191fe5a6-313b-4083-af65-d1ad7fd6d281`

You can now start your updated app on the TXT using the launcher.

Currently the root password of the TXT is `root`. Later the root login will probably be disabled by default. We'll then provide information how to activate it.

# Starting apps via SSH

When apps are being started using the launcher no debug output and no error message are visible. This may be a problem during development. You can launch apps when being logged in into the TXT via SSH (preferrably as user "ftc"). In order to start the test app log into the TXT via SSH first. Then type:

```
$ export PYTHONPATH=/opt/ftc
$ /opt/ftc/apps/user/191fe5a6-313b-4083-af65-d1ad7fd6d281/test.py
```

Again the path is derived from the UUID in the manifest file of your app.

You'll then see the error messages and debug output on the remote shell.

# Start/stop apps via telnet/netcat

SSH is not the only way to start apps remotely. The TXTs launcher implements a little command server to start and stop apps. This has been added to be used via the web interface but can also be used with tools like telnet or netcat.

Connect to the TXT via telnet on port 9000 using the command `telnet 192.168.0.12 9000`. Once connected you can enter `launch test/test.py` to launch the test app. The command `stop-app` will stop the currently running app. The command `quit` will close the telnet connection to the TXT.

The same can be achived with netcat. E.g. `echo "stop-app" | nc 192.168.0.12 9000` will stop the currently running app.

# Running TXT apps on the PC

Using the TXT for development still isn't very convenient. Fortunately TXT apps can be run an a PC. Currently all TXT apps are based on the [Python](https://www.python.org/) language and the [Qt Framework](http://www.qt.io/). The combination of both is named [PyQt](https://riverbankcomputing.com/software/pyqt/intro). PyQt comes pre-installed with the TXT community firmware. When running TXT apps on a PC PyQt has to be installed in the PC.

Another approach to integrate Python with Qt is named `PySide`. We are not using PySide on the TXT. But PyQt and PySide are quite similar and it may possible to run TXT apps under PySide with minimal modifications. But this has not been tested.

## Using a Linux PC

PyQt is available for all major linux distributions. Use your favorite package managager and search for a package named `pyqt` or `python-qt` or similar. Install this on your PC.

The TXT apps come with a special Qt TXT theming. In order to run TXT apps on the PC the files implementing this theme have also to be installed on the PC.

Please copy the file `TxtStyle.py` and the entire `themes` subdirectory to the same place on your PC. You can get these files from the [Repository](https://github.com/ftCommunity/ftcommunity-TXT/tree/master/board/fischertechnik/TXT/rootfs/opt/ftc).

If you placed the files into the directory of you app then you don't have to do anything else. If you placed them somewhere else you need to make notify python of this directory. E.g. if `TxtStyle.py` and the `themes` directory have been placed under `/tmp/mytxtenv` then you need to enter:

```
export PYTHONPATH=/tmp/mytxtenv
```
to tell python about it.

Please make sure you have made your python program executable like this:

```
$ chmod +x test.py
```

You can now run your app locally on your PC by typing:

```
$ ./test.py
```

The file `TxtStyle.py` detects that you are running the app on a PC and creates a Window of 240x320 pixels for it.

You might notice that the Apps don't look 100% the same. One reason is a different font handling on the TXT and on the desktop PC. Furthermore the Qt and Python versions are not necessarily the same on the TXT and on the PC. Furthermore the app runs under the X11 window system on a PC while the TXT uses the QWS window manager for embedded systems. But the differences are small enough to allow for convenient app development on a PC.

![Running on a TXT](tut2_img1.png) ![Running on a PC](tut2_img2.png)

Small font rendering differences on TXT (left) and PC (right)

## Using a Windows PC (by LK)

On all Versions which python supports is it possible to develop and test applications for the
TXT.

At first you need a python version, which is ok with the PyQt Version: For this you need to check first which Python version you need. Look at: https://www.riverbankcomputing.com/software/pyqt/download, there is a part which
is called „Binary Packages“ go there and downloads one version (64bit/32bit) for every download look for the Python version.

**Example:**
If your download name is: `PyQt4-4.11.4-gpl-Py3.4-Qt4.8.7-x64.exe`:
Do you get PyQt version 4-4.11.4 or Qt version 4.8.7
You need Python version 3.4 (Note: every other Python version can go, but maybe not
correct)

Your version is a 64bit version.
Now download (https://www.python.org/download/releases/3.4.3/) and install the Python
version which you found before.
Now you can go through the installer.
Now you should be able to start PyQt Programs!

Before you can start developing you Programs you must first download one file and one
directory. Go for it at https://github.com/ftCommunity/ftcommunity-TXT/tree/master/board/fischertechnik/TXT/rootfs/opt/ftc and download the themes folder and next to the `TxtStyle.py` file. Copy it into your Path in which your Python program is.

Like on Linux the Window don’t looks like at the TXT. Why can you read in the end of the
Linux contribution. But to show you how it looks on Windows here is it:

![Running on a Windows PC](tut2_img3.png)

(Tipp: It’s normal that the TxtStyle modul says: “('Unable to connect to launcher:’ ConnectionRefusedError (10061, 'Es konnte keine Verbindung hergestellt werden, da der Zielcomputer die Verbindung verweigerte', None, 10061, None))”, and think on it your PC is normaly really faster than the TXT!)
