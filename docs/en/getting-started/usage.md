---
nav-title: Usage
---
# Using the community firmware GUI

When the TXT is done booting, you should see the launcher with its circular icons:

![Launcher](https://raw.githubusercontent.com/wiki/ftCommunity/ftcommunity-TXT/txt_cw.jpg "example image with other apps")

The black status bar at the top of the launcher displays the current time and some symbols that show if the TXT ist connected to a network and other system information. Tapping on the status bar displays some more details:
 
![Launcher](https://raw.githubusercontent.com/wiki/ftCommunity/ftcommunity-TXT/launcher-with-info-menu.png "launcher with system info details")

Tapping in the blurry area below the info display takes you back to the launcher.

If more than nine apps are installed on the TXT, you can scroll forward through the installed apps by tapping the triangular icons on the bottom right (forward) or top left (backward) position on the screen.

Finally, tapping one of the circular app icons will start the corresponding app &mdash; in this example, the "About" app that displays some information about the community firmware:
 
![About](https://raw.githubusercontent.com/wiki/ftCommunity/ftcommunity-TXT/about.png "screenshot of the 'about' app")

Some apps &mdash; like the about app &mdash; provide additional options that can be accessed by tapping the "three bars" symbol to the left of the title bar:

![About](https://raw.githubusercontent.com/wiki/ftCommunity/ftcommunity-TXT/about-with-menu.png "screenshot of the 'about' app with ")

Tapping the "x" to the right of the title bar or a short press (one second or less) of the hardware "on/off" button will stop the app and take you back to the launcher screen.

Pressing the hardware "on/off" button for two seconds or more will shut down the TXT.

# Connecting to a WiFi network

You can use the "WiFi" app to set up a connection to your local WiFi network. 

Connection settings are automatically persisted on the SD card, and the TXT will automatically reconnect to a known WiFi network on the next boot. If the TXT is connected to a WiFi network, a small WiFi symbol will be shown in the 

# Accessing the web interface

The community firmware comes with a builtin web interface which can be used to launch and manage the apps installed on the TXT from a browser. You can access the web interface by pointing your browser at `http://<ip-address-of-your-txt>` where `<ip-address-of-your-txt>` is the IP address of the TXT. You can find the IP address by tapping on the launcher status bar. In the example above, the IP address is 192.168.0.30, so you would point your browser at `http://192.168.0.30` to access the web interface. Note that your TXT will probably have a different IP address.
