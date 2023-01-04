Section "Module"
        Load "fb"
        Load "shadow"
        Load "fbdevhw"
EndSection

Section "Device"
        Identifier      "Configured Video Device"
	Driver "fbdev"
	Option "fbdev" "/dev/fb0"
        Option "Rotate" "CW"
EndSection

Section "Monitor"
        Identifier      "Configured Monitor"
	DisplaySize     370 490
EndSection

Section "Screen"
        Identifier      "Default Screen"
        Monitor         "Configured Monitor"
        Device          "Configured Video Device"
        SubSection "Display"
                Virtual 240 320
        EndSubSection
EndSection

Section "InputClass"
	Identifier "tslib touchscreen catchall"
	MatchIsTouchscreen "on"
	MatchDevicePath "/dev/input/event0"
	Driver "tslib"
	Option "TransformationMatrix" "0 75 0 -100 0 6 0 0 6"
EndSection
