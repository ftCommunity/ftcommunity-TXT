#! /usr/bin/env python3
# -*- coding: utf-8 -*-
#

import configparser
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
    sock.sendall(bytes("get-app\n", "UTF-8"))
    current_executable = sock.makefile().readline().strip()
except socket.error as msg:
    print('<h2><font color="red">Launcher not responding!</font></h2>')
finally:
    sock.close()

print('<table cellspacing="20">')

# return a list of directories containing apps
# searches under /opt/ftc/apps/<group>/<app>
# the returned list is srted by the name of the apps
# as stored in the manifest file
def scan_app_dirs():
    app_base = os.path.join(base, "apps")
    # scan for app group dirs first
    app_groups = os.listdir(app_base)
    # then scan for app dirs inside
    app_dirs = []
    for i in app_groups:
        try:
            app_group_dirs = os.listdir(os.path.join(app_base, i))
            for a in app_group_dirs:
                # build full path of the app dir
                app_dir = os.path.join(app_base, i, a)
                # check if there's a manifest inside that dir
                manifestfile = os.path.join(app_dir, "manifest")
                if os.path.isfile(manifestfile):
                    # get app name
                    manifest = configparser.RawConfigParser()
                    manifest.read_file(open(manifestfile, "r", encoding="utf8"))
                    appname = manifest.get('app', 'name')
                    app_dirs.append((appname, os.path.join(app_base, i, a)))
        except:
            pass
            
    # sort list by apps name
    app_dirs.sort(key=lambda tup: tup[0])

    # return a list of only the directories of the now sorted list
    return ([x[1] for x in app_dirs])

# find all manifest files in the apps directory
for app_dir in scan_app_dirs():
    manifestfile = os.path.join(app_dir, "manifest")
    manifest = configparser.RawConfigParser()
    manifest.read(manifestfile)

    # get various fields from manifest
    appname = manifest.get('app', 'name')
    description = manifest.get('app', 'desc')
    # the icon name is a little tricky as the web server accesses files
    # relative to its document root
    group_dir, app_dir_name = os.path.split(app_dir)
    group_dir_name = os.path.basename(group_dir)
    if manifest.has_option('app', 'icon'):
        iconname = os.path.join( "apps", group_dir_name, app_dir_name, manifest.get('app', 'icon'))
    else:
        iconname = "icon.png"
        
    executable = os.path.join(app_dir, manifest.get('app', 'exec'))
    exec_relative = os.path.join(group_dir_name, app_dir_name, manifest.get('app', 'exec'))
    is_running = current_executable == exec_relative

    if count == 0:
        print("<tr>")

    print('<td align="center"', end="")
    if is_running: print(' bgcolor="green"', end="")
    print('>')
    print('<div title="' + description + '">')
    manifestfile_enc = manifestfile.replace(' ','%20')
    print('<a href="appinfo.py?manifest=' + manifestfile_enc + '">')
    print('<img src="' + iconname + '"><br>')
    print(appname)
    print('</a></div></td>')
    count += 1
    if count == cols:
        print("</tr>")
        count = 0

# fill columns
while count != 0:
    print("<td></td>")
    count += 1
    if count == cols:
        print("</tr>")
        count = 0
        
print("</table>")
