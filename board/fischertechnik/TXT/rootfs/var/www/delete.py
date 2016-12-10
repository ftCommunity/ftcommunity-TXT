#! /usr/bin/env python3
# -*- coding: utf-8 -*-
#

import configparser
import getpass
import cgi
import zipfile
import sys, os
import socket
import shutil

print("Content-Type: text/html")
print("")
print('<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd">')
print('<html xmlns="http://www.w3.org/1999/xhtml">')
print('<head><meta http-equiv="Content-Type" content="text/html; charset=UTF-8" />')
print('<title>fischertechnik TXT community firmware</title>')
print('<link rel="stylesheet" href="txt.css" />')
print('<link rel="icon" href="/favicon.ico" type="image/x-icon" />')
print('</head><body>')
print('<h1><div class="outline"><font color="red">fischer</font><font color="#046ab4">technik</font>&nbsp;<font color="#fcce04">TXT</font></div></h1>')

print('<center>')
 
appbase = "/opt/ftc/apps"
arguments = cgi.FieldStorage()
name = arguments['app'].value

# make sure there's a manifest file
manifestfile = appbase + "/" + name + "/manifest" 
if os.path.isfile(manifestfile):
    manifest = configparser.RawConfigParser()
    manifest.read_file(open(manifestfile, "r", encoding="utf8"))
    appname = manifest.get('app', 'name')

    print('<h1>Deleting "' + appname + '" app ...</h1/>')
    
    deldir = appbase + "/" + name
    print('Removing ' + deldir + ' and all files below<br/>')
    shutil.rmtree(deldir)
    
    # finally send gui a request to refresh its icons
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        print("Requesting rescan ...</br>")
        # Connect to server and send data
        sock.connect(("localhost", 9000))
        sock.sendall(bytes("rescan\n", "UTF-8"))
    except socket.error as msg:
        print("<h1>Unable to connect to Launcher: ", msg, "</h1>")

else:
    print('<h1>Error: Application not found</h1/>')


print('<p/>')
print('<a href="/">Home</a>')
print('</center>')
print("</body></html>")
