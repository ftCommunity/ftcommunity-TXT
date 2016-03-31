#! /usr/bin/env python
# -*- coding: utf-8 -*-
#

import cgi
import sys, os
import socket

referrer = os.environ.get("HTTP_REFERER")

print "Content-Type: text/html"
print ""
print '<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd">'
print '<html xmlns="http://www.w3.org/1999/xhtml">'
print '<head><meta http-equiv="Content-Type" content="text/html; charset=UTF-8" />'
print '<meta http-equiv="refresh" content="1;url='+referrer+'">'
print '<title>fischertechnik TXT community firmware</title>'
print '<link rel="stylesheet" href="txt.css">'
print '<link rel="icon" href="/favicon.ico" type="image/x-icon" />'
print '</head><body>'
print '<h1><div class="outline"><font color="red">fischer</font><font color="#046ab4">technik</font>&nbsp;<font color="#fcce04">TXT</font></div></h1>'

arguments = cgi.FieldStorage()
appname = arguments['app'].value
executable = arguments['exec'].value
print "<h1>Launching " + appname + " ...</h1>"

print '<center><img src="brick.gif"/></center>'

# Create a socket (SOCK_STREAM means a TCP socket)
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
try:
    # Connect to server and send data
    sock.connect(("localhost", 9000))
    sock.sendall("launch " + executable + "\n")
except socket.error, msg:
    print "<h2>Unable to connect to Launcher!</h2>"
    print "<h2>" , msg, "</h2>"
finally:
    sock.close()

print "</body></html>"
