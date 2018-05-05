#! /usr/bin/env python3
# -*- coding: utf-8 -*-
import os
from pathlib import Path
import urllib.request
import json
import ssl
import time
import configparser
import semantic_version
from PyQt4.QtCore import QCoreApplication

cachefile = '/tmp/update_plugin.cache'
get_interval = 86400.0  # one day
global next_get
next_get = None
global cache_rel_ver
cache_rel_ver = None


def name():
    return QCoreApplication.translate("PluginSysUpdate", "Update")


def get_release_version():
    try:
        ctx = ssl.create_default_context()
        ctx.check_hostname = False
        ctx.verify_mode = ssl.CERT_NONE
        raw_data = urllib.request.urlopen('https://api.github.com/repos/ftCommunity/ftcommunity-TXT/releases/latest', context=ctx).read().decode()
        latest_release = json.loads(raw_data)
        release_version = semantic_version.Version(latest_release['tag_name'].replace('v', ''))
        return(release_version)
    except:
        return(None)


def get_current_version():
    try:
        current = semantic_version.Version(Path('/etc/fw-ver.txt').read_text())
        return(semantic_version.Version(to_str(current)))
    except:
        return(None)


def to_str(ver):
    return(str(ver.major) + "." + str(ver.minor) + "." + str(ver.patch))


def update_avaible():
    global next_get
    global cache_rel_ver
    if cache_rel_ver != None:
        release_version = cache_rel_ver
        if time.time() > next_get:
            release_version = get_release_version()
            next_get = time.time() + get_interval
            if release_version == None:
                return(None, None, None)
    else:
        release_version = get_release_version()
        next_get = time.time() + get_interval
        if release_version == None:
            return(None, None, None)
    current_version = get_current_version()
    if current_version == None:
        return(None, None, None)
    cache_rel_ver = release_version
    return(current_version < release_version, release_version, current_version)


def icon():
    icon_data = ['16 16 2 1 ', '  c None', '. c white',
                 '                ',
                 '       ..       ',
                 '      ....      ',
                 '     ......     ',
                 '    ........    ',
                 '   ..........   ',
                 '  ............  ',
                 ' .............. ',
                 '    ........    ',
                 '    ........    ',
                 '    ........    ',
                 '    ........    ',
                 '    ........    ',
                 '    ........    ',
                 '    ........    ',
                 '                ']
    update_status, update_version, current_version = update_avaible()
    if update_status == True:
        return(icon_data)
    elif update_status == False:
        return(None)
    else:
        icon_data[2] = '. c #606060'
        return(icon_data)


def status():
    update_status, update_version, current_version = update_avaible()
    if update_status == True:
        return(QCoreApplication.translate("PluginSysUpdate", "Available V") + to_str(update_version))
    elif update_status == False:
        return(QCoreApplication.translate("PluginSysUpdate", "Up-to-date V") + to_str(current_version))
    else:
        return(QCoreApplication.translate("PluginSysUpdate", "An error occurred"))
