---
nav-title: Controlling A Model
nav-pos: 3
---
# Programming in Python: Controlling A Model

The previous tutorials have shown how to get started with an app ([Programming Python: The First App](tutorial-1.md)) and how to ease development
([Programming Python: Development](tutorial-2.md)). This part will show how to interact with a model.

The code for this tutorial can be found in [Github](https://github.com/ftCommunity/ftcommunity-TXT/tree/master/docs/_includes/examples/python/tutorial-3).

## Including the necessary libraries

The community firmware already ships with the [ftrobopy module](https://github.com/ftrobopy/ftrobopy) which provides python bindings to interface to the Fischertechnik specific input and output connectors on the TXT. These can easily be included into the application started in Tutorial #1:


```
{% include examples/python/tutorial-3/app_tutorial3_1.py %}
```

Runnng this app on the TXT as decribed in Tutorial #1 will hopefully look similar (except the app name of course). If it does and no error message is being displayed then the app has successfully connected itself to the sperate server process running on the TXT providing access to the TXTs inputs and outputs.

We use a QLabel for the output of the error message. You can learn more about this e.g. in the [PyQt tutorials](http://www.tutorialspoint.com/pyqt/index.htm). There's even one page explaining the [usage of the QLabel](http://www.tutorialspoint.com/pyqt/pyqt_qlabel_widget.htm). The examples from the tutorial don't exacly match what we are doing here since they are meant to run on a regular PC and don't use the TXT styled windows. Most of the differences are limited to the main application and the main window. When it comes to the usage of widgets only very few differences exist. E.g. the QLabel itself works the same on the PC and on the TXT.

## Controlling an output

Of course we want our little app to do something special. So please connect a light to O1 on your TXT. You can use the "Pedestrian Lights" model from the [ROBOTICS TXT Discovery Set](https://www.fischertechnik.de/en/products/playing/robotics/524328-robotics-txt-discovery-set).

We'll implement a button on screen to switch a light on and off. We initialize the TXTs input and output ports to sane defaults and add a first button to the GUI:


```
{% include examples/python/tutorial-3/app_tutorial3_2.py %}
```

You'll now see a push button being displayed when you run this app on the TXT. To make it do something we need to connect the button to some function.

```
{% include examples/python/tutorial-3/app_tutorial3_3.py %}
```


This app finally allows you to switch the lamp on and off by setting the PWN values to 512 (on) and 0 (off). We've added a handler that is called whenever the user clicks the button. To make the txt variable available to all member functions it was made a member of the class by prepending "self.". There are also tutorials that explain the self keyword and [Pythons object oriented approach in general](http://www.tutorialspoint.com/python/python_classes_objects.htm).


## Reading an input

Now that we can control one of the outputs we of course also want to read an input. Please connect a push button to I1.

There's no method of an input establishing some kind of communication by itself. Instead we need to regularly check its state by polling it. Most simple programs would just run a closed loop constantly reading the input and checking it for changes. With the full Qt GUI running in parallel and also needing to be serviced we cannot just grab the whole process by implementing a closed loop. Instead we somehow need to do the polling in parallel to the GUI processing.

Qt provides timers for things that have to be done regularily. And much like the button before the timer calls an event handler to do the task. So we add a QTimer that fires ten times a second (every 100ms) and that reads the state of the input. Whenever the input changes state from 1 to 0 we change the state of the lamp:

```
{% include examples/python/tutorial-3/app_tutorial3_4.py %}
```

With this app the light will change state whenever you press the button on screen or the physical button connected to input I1.

![tut3_img1](tut3_img1.png)


# Running the app on a PC

TXT apps can also be run on a PC as explained in [Programming Python: Development](tutorial-2.md). This is even possible with an app like this making use of the TXTs inputs and outputs. The ftrobopy module was actually written for this use case. All you need to do is to put the `ftrobopy.py` file to the same location where you placed the `TouchStyle.py` in the earlier tutorial.

Now we only need to tell the app to connect from the PC to the TXT to control its IOs. In order to do so replace this line in your program:

```
            self.txt = ftrobopy.ftrobopy("localhost", 65000) # connect to TXT's IO controller
```

with e.g.

```
            self.txt = ftrobopy.ftrobopy("192.168.7.2", 65000) # connect to TXT's IO controller
```

if your TXT is connected via USB.

It's rather inconvenient to change this line whenever switching back and forth between the PC and the TXT for app execution. The following version satisfies both needs:

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

**Before executing the app on your PC, you have to start the FT-GUI on your TXT.**

The whole program now looks like this:
```
{% include examples/python/tutorial-3/app_tutorial3_5.py %}
```
