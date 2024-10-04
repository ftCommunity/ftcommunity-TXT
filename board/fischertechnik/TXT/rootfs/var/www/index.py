#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
from applist import print_apptable

print("""
<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd">
<html xmlns="http://www.w3.org/1999/xhtml">
  <head>
    <meta http-equiv="Content-Type" content="text/html; charset=UTF-8" />
    <meta http-equiv="cache-control" content="max-age=0" />
    <meta http-equiv="cache-control" content="no-cache" />
    <meta http-equiv="expires" content="0" />
    <meta http-equiv="expires" content="Tue, 01 Jan 1980 1:00:00 GMT" />
    <meta http-equiv="pragma" content="no-cache" />
    <title>fischertechnik TXT community firmware</title>
    <link rel="stylesheet" href="txt.css" />
    <link rel="icon" href="/favicon.ico" type="image/x-icon" />
  </head>
  
  <body>
    <h1><div class="outline"><font color="red">fischer</font><font color="#046ab4">technik</font>&nbsp;<font color="#fcce04">TXT</font></div></h1>
    <center><a href="https://github.com/ftCommunity/ftcommunity-TXT" target="ft-community">community edition</a></center>

    <center><div>
	<hr/>

	<h2>Installed apps</h2>""")

print_apptable()

print("""
	<hr/>
	<h2>App upload</h2>
	<form action="upload.py" method="post" enctype="multipart/form-data">
	  <p>Choose a zip file containing a TXT app to upload:</p>
	  <input name="appfile" type="file" size="30" accept="application/zip"/>
	  <button type="submit">Upload</button>
	</form>
	
    </div></center>
    
  </body>
</html>""")
