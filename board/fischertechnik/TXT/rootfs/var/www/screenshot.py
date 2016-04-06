#! /usr/bin/env python3
# -*- coding: utf-8 -*-
#

import sys, os, subprocess, platform

print("Content-Type: text/html")
print("")
print('<?xml version="1.0" encoding="iso-8859-1"?>')
print('<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN"')
print('         "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">')
print('<html xmlns="http://www.w3.org/1999/xhtml" xml:lang="en" lang="en">')
print(' <head>')
print('  <title>Screenshot taken</title>')
print(' </head>')
print(' <body>')
print('  <h1>Screenshot taken</h1>')

# for PC based tests use imagemagicks import to grab the X screen. The user
# ownign the screen needs to give access with "xhost +" beforehand
if platform.machine() == "armv7l":
    COMMAND = "fbgrab screenshot.png"
else:
    COMMAND = "import -display :0 -window root -geometry 320x240 screenshot.png"

app = subprocess.Popen(COMMAND.split())
while app.poll() == None:
    pass

print(' </body>')
print('</html>')


