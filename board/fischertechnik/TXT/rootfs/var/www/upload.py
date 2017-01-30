#! /usr/bin/env python3
# -*- coding: utf-8 -*-
#

import configparser
import cgi
import zipfile
import sys, os
import socket
import io
import cgitb
cgitb.enable()

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
 
upload_dir = "/tmp"

# directory were the user installed apps are located
appbase = "/opt/ftc/apps/user"

print('<div align="center">')
print("<h1>Upload</h1>")

def save_uploaded_file():
    form = cgi.FieldStorage()
    if "appfile" not in form:
        return False,"No appfile"

    fileitem = form["appfile"]
    if not fileitem.file or not fileitem.filename:
        return False,"No valid appfile"

    filename = os.path.join(upload_dir, fileitem.filename)
    if os.path.splitext(filename)[1] != ".zip":
        return False,"Not a zip file"

    print("Writing file to " + filename + "<br/>")
    open(filename, 'wb').write(fileitem.file.read())

    return True,filename

def unzip_uploaded_file(zip_name, appbase):
    print("Unpacking " + zip_name + "<br/>")

    if not zipfile.is_zipfile(zip_name):
        return False, "Not a valid zip file", ""

    fh = open(zip_name, 'rb')
    z = zipfile.ZipFile(fh)

    try:
        z.getinfo("manifest")
    except KeyError:
        fh.close()
        return False, "Not a TXT app!", ""

    # extract only the manifest to get the uuid which in turn
    # is used as the apps local directory
    manifest_str = io.StringIO(z.read("manifest").decode('utf-8'))
    manifest = configparser.RawConfigParser()
    manifest.read_file(manifest_str)
    if not manifest.has_option('app', 'uuid'):
        return False, "Manifest does not contain a UUID!", ""

    appdir = os.path.join(appbase, manifest.get('app', 'uuid'))

    print("Extracting to " + appdir + "<br/>")

    if os.path.exists(appdir):
        print("Target dir exists, overwriting contents.<br/>")
    else:
        print("Target dir does not exist, creating it.<br/>")
        try:
            os.makedirs(appdir)
        except:
            return False, "Unable to create target dir!", ""

    for name in z.namelist():
        print("Extracting " + name + " ...<br/>")
        z.extract(name, appdir)
    fh.close()

    return True, "", appdir

[ok, zip_name] = save_uploaded_file()
if ok:
    #    appdir = appbase + "/" + os.path.splitext(os.path.basename(zip_name))[0]
    [ok, result_str, appdir] = unzip_uploaded_file(zip_name, appbase)

    if not ok:
        print("<h1>Error: " + result_str + "</h1>")
    
    if os.path.isfile(zip_name):
        print("Deleting " + zip_name + "<br/>")
        os.remove(zip_name)

    # make the executable executable
    manifestfile = appdir + "/manifest"
    if os.path.isfile(manifestfile):
        manifest = configparser.RawConfigParser()
        manifest.read(manifestfile)

        # get various fields from manifest
        executable = appdir + "/" + manifest.get('app', 'exec')
        
        print("Making executable: " + executable + "<br/>")
        os.chmod(executable, 0o744)

    # finally send gui a request to refresh its icons
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        print("Requesting rescan ...<br/>")
        # Connect to server and send data
        sock.connect(("localhost", 9000))
        sock.sendall(bytes("rescan\n", "UTF-8"))
    except socket.error as msg:
        print("Unable to connect to Launcher: ", msg)

    finally:
        sock.close()

else:
    print("<h1>Error: " + zip_name + "</h1>")

print("</p>")
print('<a href="/">Home</a>')
print('</div>')

print("</body></html>")
