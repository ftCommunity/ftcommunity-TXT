#! /usr/bin/env python3
# -*- coding: utf-8 -*-
import os
import urllib.request
import json
import ssl
import time
import configparser

name = 'Update'
cachefile = '/tmp/update_plugin.cache'
get_interval = 86400.0  # one day


def get_release_version():
    try:
        ctx = ssl.create_default_context()
        ctx.check_hostname = False
        ctx.verify_mode = ssl.CERT_NONE
        raw_data = urllib.request.urlopen('https://api.github.com/repos/ftCommunity/ftcommunity-TXT/releases/latest', context=ctx).read().decode()
        latest_release = json.loads(raw_data)
        release_version = latest_release['tag_name'].replace('v', '')
        return(release_version)
    except:
        return(None)


def get_current_version():
    try:
        fw_file = open('/etc/fw-ver.txt', 'r')
        current_version = fw_file.read().strip().split('-')[0]
        fw_file.close()
        return(current_version)
    except:
        return(None)


def update_avaible():
    try:
        cache = configparser.SafeConfigParser()
        cache.read(cachefile)
        next_get = cache.get('general', 'next_get')
        release_version = cache.get('general', 'release_version')
        if time.time() > float(next_get):
            release_version = get_release_version()
            next_get = str(time.time() + get_interval)
            if release_version == None:
                return(None, None, None)
    except:
        release_version = get_release_version()
        next_get = str(time.time() + get_interval)
        if release_version == None:
            return(None, None, None)
    current_version = get_current_version()
    if current_version == None:
        return(None, None, None)

    try:
        cache_w = configparser.ConfigParser()
        cache_file_w = open(cachefile, 'w')
        cache_w.add_section('general')
        cache_w.set('general', 'next_get', str(next_get))
        cache_w.set('general', 'release_version', release_version)
        cache_w.write(cache_file_w)
        cache_file_w.close()
    except:
        return(None, None, None)
    return(release_version != current_version, release_version, current_version)


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
        icon_data[2] = '. c green'
        return(icon_data)
    elif update_status == False:
        return(None)
    else:
        icon_data[2] = '. c #606060'
        return(icon_data)


def status():
    update_status, update_version, current_version = update_avaible()
    if update_status == True:
        return('Available V ' + update_version + '\nto update open the Settings App')
    elif update_status == False:
        return('Up-to-date V ' + current_version)
    else:
        return('An error occurred')
