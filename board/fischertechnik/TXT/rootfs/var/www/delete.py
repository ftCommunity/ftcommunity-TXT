#! /usr/bin/env python
# -*- coding: utf-8 -*-
#

import cgi
import sys, os

print "Content-Type: text/html"
print ""
print '<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">'
print '<html xmlns="http://www.w3.org/1999/xhtml">'
print '<head><meta http-equiv="Content-Type" content="text/html; charset=UTF-8" />'
print '<meta http-equiv="refresh" content="1;url=/">'
print '<title>fischertechnik TXT community firmware</title>'
print '<link rel="stylesheet" href="txt.css"></head>'
print '<link rel="icon" href="/favicon.ico" type="image/x-icon" />'
print '</head><body>'
print '<h1><div class="outline"><font color="red">fischer</font><font color="#046ab4">technik</font>&nbsp;<font color="#fcce04">TXT</font></div></h1>'
 
arguments = cgi.FieldStorage()
print "<h1>Deleting " + arguments['app'].value + " ...</h1>"

os.system("rm apps/ " + arguments['app'].value")

print "</body></html>"
