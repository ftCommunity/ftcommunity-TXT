#! /usr/bin/env python3
# -*- coding: utf-8 -*-
#

import sys, string, os, time
import asyncio
import websockets
import subprocess
import socket

FILE = "/tmp/app.log"
#FILE = "/var/log/syslog"

def dump_html():
    print('Content-Type: text/html')
    print('')
    print('<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd">')
    print('<html xmlns="http://www.w3.org/1999/xhtml">')
    print('<head><meta http-equiv="Content-Type" content="text/html; charset=UTF-8" />')
    print('<title>fischertechnik TXT community firmware</title>')
    print('<link rel="stylesheet" href="txt.css">')
    print('<link rel="icon" href="/favicon.ico" type="image/x-icon" />')
    print('</head><body>')
    print('<h1><div class="outline"><font color="red">fischer</font><font color="#046ab4">technik</font>&nbsp;<font color="#fcce04">TXT</font></div></h1>')
    
    print('<h1>Application console log</h1>')
    print('<div id="file"></div>')
    print('    <script type="text/javascript" charset="utf-8">')
    print('        var ws = new WebSocket("ws://"+document.location.hostname+":9001/");')
    print('        ws.onmessage = function(evt) {')
    print('            var objDiv = document.getElementById("file");')
    print('            objDiv.innerHTML += evt.data;')
    print('            objDiv.scrollTop = objDiv.scrollHeight - div.clientHeight;')
    print('            objDiv.animate({scrollTop: objDiv.scrollHeight});')
    print('        };')
    print('    </script>')
    print('</body></html>')
    sys.stdout.flush()

def htmlize(s):
    s = s.replace("&", "&amp;")
    s = s.replace("<", "&lt;")
    s = s.replace(">", "&gt;")
    s = s.replace("\n", "<br/>")
    return s

def notify_launcher(str):
    # Create a socket (SOCK_STREAM means a TCP socket)
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        # Connect to server and send data
        sock.connect(("localhost", 9000))
        sock.sendall(bytes(str + "\n", "UTF-8"))
    except socket.error as msg:
        pass
    finally:
        sock.close()

@asyncio.coroutine
def handler(websocket, path):
    with open(FILE, 'r') as fin:
        line = fin.readline()
        while(websocket.open):
            if line:
                yield from websocket.send(htmlize(line))
            else:
                yield from asyncio.sleep(0.01)
            line = fin.readline()

    asyncio.get_event_loop().stop()


if os.fork():
    sys.exit(0)

os.setsid()

if os.fork():
    # request log file creation from launcher
    notify_launcher("logging-start")

    # this is the server process which reads the file, monitors
    # it for new contents and forwards it to the client
    loop = asyncio.get_event_loop()
    start_server = websockets.serve(handler, "", 9001)
    websocket_server = loop.run_until_complete(start_server)

    try:
        loop.run_forever()
    finally:
        websocket_server.close()
        loop.run_until_complete(websocket_server.wait_closed())

    notify_launcher("logging-stop")
    sys.exit(0)

# some delay to make sure the server is listening
time.sleep(2)
dump_html()

