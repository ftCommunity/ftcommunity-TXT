#! /usr/bin/env python3
# -*- coding: utf-8 -*-
#

import sys, string, os, time
import asyncio
import websockets
import subprocess
import socket

FILE = "/tmp/app.log"

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

def htmlize(s):
    s = s.replace("&", "&amp;")
    s = s.replace("<", "&lt;")
    s = s.replace(">", "&gt;")
    s = s.replace("\n", "<br/>")
    return s

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

time.sleep(1)

os.setsid()

# request log file creation from launcher
notify_launcher("logging-start")

# this is the server process which reads the file, monitors
# it for new contents and forwards it to the client
loop = asyncio.get_event_loop()
start_server = websockets.serve(handler, "", 8999)
websocket_server = loop.run_until_complete(start_server)

try:
    loop.run_forever()
finally:
    websocket_server.close()
    loop.run_until_complete(websocket_server.wait_closed())

notify_launcher("logging-stop")

