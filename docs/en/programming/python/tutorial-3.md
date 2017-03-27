---
nav-title: Controlling A Model
---
# Programming in Python: Controlling A Model

Warning: This tutorial is outdated and needs to be updated!

The previous tutorials have show how to get started with an app ([Programming Python: The First App](tutorial-1.md)) and how to ease development
([Programming Python: Development](tutorial-2.md)). This part will show how to interact with a model.

The code for this tutorial can be found in the [apps repository](https://github.com/ftCommunity/ftcommunity-apps/tree/master/packages/app_tutorial_3).

## Including the necessary libraries

The community firmware already ships with the [ftrobopy module](https://github.com/ftrobopy/ftrobopy) which provides python bindings to interface to the Fischertechnik specific input and output connectors on the TXT. These can easily be included into the application started in Tutorial #1:


```
#! /usr/bin/env python3
# -*- coding: utf-8 -*-
#
import sys
import ftrobopy                                              # Import the ftrobopy module
from TxtStyle import *

class FtcGuiApplication(TxtApplication):
    def __init__(self, args):
        TxtApplication.__init__(self, args)

        # create the empty main window
        w = TxtWindow("Tut_3a")

        try:
            txt = ftrobopy.ftrobopy("localhost", 65000)      # connect to TXT's IO controller
        except:
            txt = None                                       # set TXT to "None" of connection failed

	if not txt:
	    # display error of TXT could no be connected
            # error messages is centered and may span
            # over several lines
	    err_msg = QLabel("Error connecting IO server")   # create the error message label
            err_msg.setWordWrap(True)                        # allow it to wrap over several lines
            err_msg.setAlignment(Qt.AlignCenter)             # center it horizontally
            w.setCentralWidget(err_msg)                      # attach it to the main output area

        w.show()
        self.exec_()        

if __name__ == "__main__":
    FtcGuiApplication(sys.argv)
```

Runnng this app on the TXT as decribed in Tutorial #1 will hopefully look similar (except the app name of course). If it does and no error message is being displayed then the app has successfully connected itself to the sperate server process running on the TXT providing access to the TXTs inputs and outputs.

We use a QLabel for the output of the error message. You can learn more about this e.g. in the [PyQt turorials](http://www.tutorialspoint.com/pyqt/index.htm). There's even one page explaining the [usage of the QLabel](http://www.tutorialspoint.com/pyqt/pyqt_qlabel_widget.htm).

The expamples from the tutorial don't exacly match what we are doing here since they are meant to run on a regular PC and don't use the TXT styled windows. Most of the differences are limited to the main application and the main window. When it comes to the usage of widgets only very few differences exist. E.g. the QLabel itself works the same on the PC and on the TXT.

## Controlling an output

Of course we want our little app to do something special. So please connect a light to O1 on your TXT. You can use the "Pedestrian Lights" model from the [ROBOTICS TXT Discovery Set](http://www.fischertechnik.de/desktopdefault.aspx/tabid-21/39_read-307/usetemplate-2_column_pano/).

We'll implement a button on screen to switch it on and off. We initialize the TXTs input and output ports to sane defaults and add a first button to the GUI:


```
#! /usr/bin/env python3
# -*- coding: utf-8 -*-
#
import sys
import ftrobopy                                              # Import the ftrobopy module
from TxtStyle import *

class FtcGuiApplication(TxtApplication):
    def __init__(self, args):
        TxtApplication.__init__(self, args)

        # create the empty main window
        w = TxtWindow("Tut_3b")

        try:
            txt = ftrobopy.ftrobopy("localhost", 65000)      # connect to TXT's IO controller
        except:
            txt = None                                       # set TXT to "None" of connection failed

	if not txt:
	    # display error of TXT could no be connected
            # error messages is centered and may span
            # over several lines
	    err_msg = QLabel("Error connecting IO server")   # create the error message label
            err_msg.setWordWrap(True)                        # allow it to wrap over several lines
            err_msg.setAlignment(Qt.AlignCenter)             # center it horizontally
            w.setCentralWidget(err_msg)                      # attach it to the main output area
        else:
            # initialization went fine. So the main gui
            # is being drawn
            button = QPushButton("Toggle O1")                # create a button labeled "Toggle O1"
            w.setCentralWidget(button)                       # attach it to the main output area

	    # configure all TXT outputs to normal mode
            M = [ txt.C_OUTPUT, txt.C_OUTPUT, txt.C_OUTPUT, txt.C_OUTPUT ]
            I = [ (txt.C_SWITCH, txt.C_DIGITAL ),
                  (txt.C_SWITCH, txt.C_DIGITAL ),
                  (txt.C_SWITCH, txt.C_DIGITAL ),
                  (txt.C_SWITCH, txt.C_DIGITAL ),
                  (txt.C_SWITCH, txt.C_DIGITAL ),
                  (txt.C_SWITCH, txt.C_DIGITAL ),
                  (txt.C_SWITCH, txt.C_DIGITAL ),
                  (txt.C_SWITCH, txt.C_DIGITAL ) ]
            txt.setConfig(M, I)
            txt.updateConfig()

        w.show()
        self.exec_()

if __name__ == "__main__":
    FtcGuiApplication(sys.argv)
```

You'll now see a push button being displayed when you run this app on the TXT. To make it do something we need to connect the button to some function.


```
#! /usr/bin/env python3
# -*- coding: utf-8 -*-
#
import sys
import ftrobopy                                              # Import the ftrobopy module
from TxtStyle import *

class FtcGuiApplication(TxtApplication):
    def __init__(self, args):
        TxtApplication.__init__(self, args)

        # create the empty main window
        w = TxtWindow("Tut_3c")

        try:
            self.txt = ftrobopy.ftrobopy("localhost", 65000) # connect to TXT's IO controller
        except:
            self.txt = None                                  # set TXT to "None" of connection failed

	if not self.txt:
	    # display error of TXT could no be connected
            # error messages is centered and may span
            # over several lines
	    err_msg = QLabel("Error connecting IO server")   # create the error message label
            err_msg.setWordWrap(True)                        # allow it to wrap over several lines
            err_msg.setAlignment(Qt.AlignCenter)             # center it horizontally
            w.setCentralWidget(err_msg)                      # attach it to the main output area
        else:
            # initialization went fine. So the main gui
            # is being drawn
            button = QPushButton("Toggle O1")                # create a button labeled "Toggle O1"
	    button.clicked.connect(self.on_button_clicked)   # connect button to event handler
            w.setCentralWidget(button)                       # attach it to the main output area

	    # configure all TXT outputs to normal mode
            M = [ self.txt.C_OUTPUT, self.txt.C_OUTPUT, self.txt.C_OUTPUT, self.txt.C_OUTPUT ]
            I = [ (self.txt.C_SWITCH, self.txt.C_DIGITAL ),
                  (self.txt.C_SWITCH, self.txt.C_DIGITAL ),
                  (self.txt.C_SWITCH, self.txt.C_DIGITAL ),
                  (self.txt.C_SWITCH, self.txt.C_DIGITAL ),
                  (self.txt.C_SWITCH, self.txt.C_DIGITAL ),
                  (self.txt.C_SWITCH, self.txt.C_DIGITAL ),
                  (self.txt.C_SWITCH, self.txt.C_DIGITAL ),
                  (self.txt.C_SWITCH, self.txt.C_DIGITAL ) ]
            self.txt.setConfig(M, I)
            self.txt.updateConfig()

	    # initially switch light on
            self.light_on = True                             # remember that the light is on
	    self.txt.setPwm(0,512)                           # set PWm to 512 (full on)

        w.show()
        self.exec_()

    # an event handler for our button (called a "slot" in qt)
    # it will be called whenever the user clicks the button
    def on_button_clicked(self):
	self.light_on = not self.light_on                   # change state
        if self.light_on:                                   # set output accordingly
    	    self.txt.setPwm(0,512)                          # PWN=512 means full on
        else:
    	    self.txt.setPwm(0,0)                            # PWM=0 means off

if __name__ == "__main__":
    FtcGuiApplication(sys.argv)
```

This app finally allows you to switch the lamp on and off by setting the PWN values to 512 (on) and 0 (off). We've added a handler that is called whenever the user clicks the button. To make the txt variable available to all member functions it was made a member of the class by prepending "self.". There are also tutorials that explaing the the self keyword and [Pythons object oriented approach in general](http://www.tutorialspoint.com/python/python_classes_objects.htm).


## Reading an input

Now that we can control one of the outputs we of course also want to read an input. Please connect a push button to to I1.

There's no method of an input establishing some kind of communication by itself. Instead we need to regularly check it's state by polling it. Most simple programs would just run a closed loop constantly reading the input and checking it for changes. With the full Qt GUI running in parallel and also needing to be serviced we cannot just grab the whole process by implementing a closed loop. Instead we somehow need to do the polling in parallel to the GUI processing.

Qt provides timers for things that have to done regularily. And much like the button before the timer calls an event handler to do the task. So we add a QTimer that fires ten times a second (every 100ms) and that reads the state of the input. Whenever the input changes state from 1 to 0 we change the state of the lamp:

```
#! /usr/bin/env python3
# -*- coding: utf-8 -*-
#
import sys
import ftrobopy                                              # Import the ftrobopy module
from TxtStyle import *

class FtcGuiApplication(TxtApplication):
    def __init__(self, args):
        TxtApplication.__init__(self, args)

        # create the empty main window
        w = TxtWindow("Tut_3e")

        txt_ip = os.environ.get('TXT_IP')                    # try to read TXT_IP environment variable
        try:
            self.txt = ftrobopy.ftrobopy("localhost", 65000) # connect to TXT's IO controller
        except:
            self.txt = None

        vbox = QVBoxLayout()

        if not self.txt:
            # display error of TXT could no be connected
            # error messages is centered and may span
            # over several lines
            err_msg = QLabel("Error connecting IO server")   # create the error message label
            err_msg.setWordWrap(True)                        # allow it to wrap over several lines
            err_msg.setAlignment(Qt.AlignCenter)             # center it horizontally
            vbox.addWidget(err_msg)                          # attach it to the main output area
        else:
            # initialization went fine. So the main gui
            # is being drawn
            button = QPushButton("Toggle O1")                # create a button labeled "Toggle O1"
            button.clicked.connect(self.on_button_clicked)   # connect button to event handler
            vbox.addWidget(button)                           # attach it to the main output area

            # configure all TXT outputs to normal mode
            M = [ self.txt.C_OUTPUT, self.txt.C_OUTPUT, self.txt.C_OUTPUT, self.txt.C_OUTPUT ]
            I = [ (self.txt.C_SWITCH, self.txt.C_DIGITAL ),
                  (self.txt.C_SWITCH, self.txt.C_DIGITAL ),
                  (self.txt.C_SWITCH, self.txt.C_DIGITAL ),
                  (self.txt.C_SWITCH, self.txt.C_DIGITAL ),
                  (self.txt.C_SWITCH, self.txt.C_DIGITAL ),
                  (self.txt.C_SWITCH, self.txt.C_DIGITAL ),
                  (self.txt.C_SWITCH, self.txt.C_DIGITAL ),
                  (self.txt.C_SWITCH, self.txt.C_DIGITAL ) ]
            self.txt.setConfig(M, I)
            self.txt.updateConfig()

            # initially switch light on
            self.light_on = True                             # remember that the light is on
            self.txt.setPwm(0,512)                           # set PWm to 512 (full on)

            self.timer = QTimer(self)                        # create a timer
            self.timer.timeout.connect(self.on_timer)        # connect timer to on_timer slot
            self.timer.start(100);                           # fire timer every 100ms (10 hz)

            self.button_state = False                        # assume initually the button is not pressed

        w.centralWidget.setLayout(vbox)
        w.show()
        self.exec_()

    def toggle_light(self):
        self.light_on = not self.light_on                   # change state
        if self.light_on:                                   # set output accordingly
            self.txt.setPwm(0,512)                          # PWN=512 means full on
        else:
            self.txt.setPwm(0,0)                            # PWM=0 means off

    # an event handler for our button (called a "slot" in qt)
    # it will be called whenever the user clicks the button
    def on_button_clicked(self):
        self.toggle_light()

    # an event handler for the timer (also a qt slot)
    def on_timer(self):
        # check if input state differs from saved state
        if self.button_state != self.txt.getCurrentInput(0):
            # change saved state to reflect input state
            self.button_state = not self.button_state
            # toggle lamp state if button has been pressed
            if self.button_state:
                self.toggle_light()

if __name__ == "__main__":
    FtcGuiApplication(sys.argv)
```

With this app the lamp will change state whenever you press the button on screen or the physical button connected to input I1.

![](tut3_img1.png)

# Running the app on a PC

TXT apps can also be run on a PC as explained in [Programming Python: Development](tutorial-2.md). This is even possible with an app like this making use of the TXTs inputs and outputs. The ftrobopy module was actually written for this use case. All you need to do is to put the `ftcobopy.py` file to the same location where you placed the `TxtStyle.py` in the first Tutorial.

Now we only need to tell the app to connect from the PC to the TXT to control its IOs. In order to do so replace this line in your program:

```
            self.txt = ftrobopy.ftrobopy("localhost", 65000) # connect to TXT's IO controller
```

with e.g.

```
            self.txt = ftrobopy.ftrobopy("192.168.7.2", 65000) # connect to TXT's IO controller
```

if your TXT is connected via USB.

It's rather inconvenient to change this line wheever switching back and forth between the PC and the TXT for app execution. The following version satisfies both needs:

```
        txt_ip = os.environ.get('TXT_IP')
        if txt_ip == None: txt_ip = "localhost"
        try:
            txt = ftrobopy.ftrobopy(txt_ip, 65000)
        except:
            txt = None
```

It tries to read an environment variable named `TXT_IP`. If it exists it will use that to connect to the TXT. If it doesn't then it will fall back to the default "localhost" which means that it's the local machine itself providing the IO ports.

On your PC you simple need to set this environment variable like this under Linux:

```
$ export TXT_IP=192.168.7.2
```

You can even place this into the `.bashrc` file in your home directory so you don't have to care at all anymore. The same app will run on the TXT and on your PC.

The whole program now looks like this:

```
#! /usr/bin/env python3
# -*- coding: utf-8 -*-
#
import sys
import ftrobopy                                              # Import the ftrobopy module
from TxtStyle import *

class FtcGuiApplication(TxtApplication):
    def __init__(self, args):
        TxtApplication.__init__(self, args)

        # create the empty main window
        w = TxtWindow("Tut_3e")

        txt_ip = os.environ.get('TXT_IP')                    # try to read TXT_IP environment variable
        if txt_ip == None: txt_ip = "localhost"              # use localhost otherwise
        try:
            self.txt = ftrobopy.ftrobopy(txt_ip, 65000)      # try to connect to IO server
        except:
            self.txt = None

        vbox = QVBoxLayout()

        if not self.txt:
            # display error of TXT could no be connected
            # error messages is centered and may span
            # over several lines
            err_msg = QLabel("Error connecting IO server")   # create the error message label
            err_msg.setWordWrap(True)                        # allow it to wrap over several lines
            err_msg.setAlignment(Qt.AlignCenter)             # center it horizontally
            vbox.addWidget(err_msg)                          # attach it to the main output area
        else:
            # initialization went fine. So the main gui
            # is being drawn
            button = QPushButton("Toggle O1")                # create a button labeled "Toggle O1"
            button.clicked.connect(self.on_button_clicked)   # connect button to event handler
            vbox.addWidget(button)                           # attach it to the main output area

            # configure all TXT outputs to normal mode
            M = [ self.txt.C_OUTPUT, self.txt.C_OUTPUT, self.txt.C_OUTPUT, self.txt.C_OUTPUT ]
            I = [ (self.txt.C_SWITCH, self.txt.C_DIGITAL ),
                  (self.txt.C_SWITCH, self.txt.C_DIGITAL ),
                  (self.txt.C_SWITCH, self.txt.C_DIGITAL ),
                  (self.txt.C_SWITCH, self.txt.C_DIGITAL ),
                  (self.txt.C_SWITCH, self.txt.C_DIGITAL ),
                  (self.txt.C_SWITCH, self.txt.C_DIGITAL ),
                  (self.txt.C_SWITCH, self.txt.C_DIGITAL ),
                  (self.txt.C_SWITCH, self.txt.C_DIGITAL ) ]
            self.txt.setConfig(M, I)
            self.txt.updateConfig()

            # initially switch light on
            self.light_on = True                             # remember that the light is on
            self.txt.setPwm(0,512)                           # set PWm to 512 (full on)

            self.timer = QTimer(self)                        # create a timer
            self.timer.timeout.connect(self.on_timer)        # connect timer to on_timer slot
            self.timer.start(100);                           # fire timer every 100ms (10 hz)

            self.button_state = False                        # assume initually the button is not pressed

        w.centralWidget.setLayout(vbox)
        w.show()
        self.exec_()

    def toggle_light(self):
        self.light_on = not self.light_on                   # change state
        if self.light_on:                                   # set output accordingly
            self.txt.setPwm(0,512)                          # PWN=512 means full on
        else:
            self.txt.setPwm(0,0)                            # PWM=0 means off

    # an event handler for our button (called a "slot" in qt)
    # it will be called whenever the user clicks the button
    def on_button_clicked(self):
        self.toggle_light()

    # an event handler for the timer (also a qt slot)
    def on_timer(self):
        # check if input state differs from saved state
        if self.button_state != self.txt.getCurrentInput(0):
            # change saved state to reflect input state
            self.button_state = not self.button_state
            # toggle lamp state if button has been pressed
            if self.button_state:
                self.toggle_light()

if __name__ == "__main__":
    FtcGuiApplication(sys.argv)
```
