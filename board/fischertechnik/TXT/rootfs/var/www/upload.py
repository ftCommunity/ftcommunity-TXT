#! /usr/bin/env python
# -*- coding: utf-8 -*-
#

import ConfigParser
import getpass
import cgi
import zipfile
import sys, os
import socket

print "Content-Type: text/html"
print ""
print '<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd">'
print '<html xmlns="http://www.w3.org/1999/xhtml">'
print '<head><meta http-equiv="Content-Type" content="text/html; charset=UTF-8" />'
print '<title>fischertechnik TXT community firmware</title>'
print '<link rel="stylesheet" href="txt.css" />'
print '<link rel="icon" href="/favicon.ico" type="image/x-icon" />'
print '</head><body>'
print '<h1><div class="outline"><font color="red">fischer</font><font color="#046ab4">technik</font>&nbsp;<font color="#fcce04">TXT</font></div></h1>'
 
upload_dir = "/tmp"
appbase = "/opt/ftc/apps"

print "<h1>Upload</h1>"

def save_uploaded_file():
    form = cgi.FieldStorage()
    if not form.has_key("appfile"):
        return False,"No appfile"

    fileitem = form["appfile"]
    if not fileitem.file or not fileitem.filename:
        return False,"No valid appfile"

    filename = os.path.join(upload_dir, fileitem.filename)
    if os.path.splitext(filename)[1] != ".zip":
        return False,"Not a zip file"

    print "Writing file to " + filename + "<br/>"
    fout = file(filename, 'wb')
    while 1:
        chunk = fileitem.file.read(4096)
        if not chunk: break
        fout.write (chunk)
    fout.close()
        
    return True,filename

def unzip_uploaded_file(zip_name, appdir):
    print "Unpacking " + zip_name + "<br/>"

    if not zipfile.is_zipfile(zip_name):
        return False, "Not a valid zip file"

    fh = open(zip_name, 'rb')
    z = zipfile.ZipFile(fh)

    try:
        z.getinfo("manifest")
    except KeyError:
        fh.close()
        return False, "Not a TXT app!"

    print "Extracting to " + appdir + "<br/>"

    if os.path.exists(appdir):
        print "Target dir exists, overwriting contents.<br/>"
    else:
        print "Target dir does not exist, creating it.<br/>"
        os.makedirs(appdir)

    for name in z.namelist():
        print "Extracting " + name + " ...<br/>"
        z.extract(name, appdir)
    fh.close()

    return True, ""

print "<p>Running as " + getpass.getuser() + "</p>"
print "<p>"

[ok, zip_name] = save_uploaded_file()
if ok:
    appdir = appbase + "/" + os.path.splitext(os.path.basename(zip_name))[0]
    [ok, result_str] = unzip_uploaded_file(zip_name, appdir)

    if not ok:
        print "<h1>Error: " + result_str + "</h1>"
    
    if os.path.isfile(zip_name):
        print "Deleting " + zip_name + "<br/>"
        os.remove(zip_name)

    # make the executable executable
    manifestfile = appdir + "/manifest"
    if os.path.isfile(manifestfile):
        manifest = ConfigParser.RawConfigParser()
        manifest.read(manifestfile)

        # get various fields from manifest
        executable = appdir + "/" + manifest.get('app', 'exec')
        
        print "Making executable: " + executable + "<br/>"
        os.chmod(executable, 0744)

    # finally send gui a request to refresh its icons
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        print "Requesting rescan ...<br/>"
        # Connect to server and send data
        sock.connect(("localhost", 9000))
        sock.sendall("rescan\n")
    except socket.error, msg:
        print "Unable to connect to Launcher: ", msg

    finally:
        sock.close()

else:
    print "<h1>Error: " + zip_name + "</h1>"

print "</p>"

print '<form action="/">'
print '<input type="submit" value="Ok"/>'
print '</form>'

print "</body></html>"
