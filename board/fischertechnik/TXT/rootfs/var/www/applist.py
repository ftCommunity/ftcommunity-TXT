#! /usr/bin/env python
# -*- coding: utf-8 -*-
#

import ConfigParser
import sys, os, socket

base = "/opt/ftc"

cols = 5   # 3 is same as on TXT itself
count = 0

# request executable name of currently running app from 
# launcher
current_executable = ""
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
try:
    # Connect to server and send data
    sock.connect(("localhost", 9000))
    sock.sendall("get-app\n")
    exe_str = sock.makefile().readline().strip()
    exe_str_parts = exe_str.split('/')
    # this returns the full path. Extract last two path
    # elements only
    if len(exe_str_parts) > 1:
        current_executable = exe_str_parts[-2] + "/" + exe_str_parts[-1]
except socket.error, msg:
    print '<h2><font color="red">Launcher not responding!</font></h2>'
finally:
    sock.close()


print '<table cellspacing="20">'

# find all manifest files in the apps directory
for name in sorted(os.listdir(base + "/apps")):
    manifestfile = base + "/apps/" + name + "/manifest"
    if os.path.isfile(manifestfile):
        manifest = ConfigParser.RawConfigParser()
        manifest.read(manifestfile)

        # get various fields from manifest
        appname = manifest.get('app', 'name')
        description = manifest.get('app', 'desc')
        iconname = "apps/" + name + "/" + manifest.get('app', 'icon')
        executable = name + "/" + manifest.get('app', 'exec')
        is_running = current_executable == executable

#        print "<h1>" + current_executable ,executable + "</h1>"

        if count == 0:
            print "<tr>"

        print '<td align="center"'
        if is_running: print ' bgcolor="green"'
        print '>'
        print '<div title="' + description + '">'
        manifestfile_enc = manifestfile.replace(' ','%20')
        print '<a href="appinfo.py?manifest=' + manifestfile_enc + '">'
        print '<img src="' + iconname + '"><br>'
        print appname
        print '</a></div></td>'
        count += 1
        if count == cols:
            print "</tr>"
            count = 0

# fill columns
while count != 0:
    print "<td></td>"
    count += 1
    if count == cols:
        print "</tr>"
        count = 0
        
print "</table>"
