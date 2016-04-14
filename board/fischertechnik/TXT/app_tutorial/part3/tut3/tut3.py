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
