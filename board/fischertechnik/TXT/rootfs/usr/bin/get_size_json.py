#! /usr/bin/env python3
# -*- coding: utf-8 -*-
#
import sys
import json
try:
    data = json.load(sys.stdin)
    for asset in data["assets"]:
        if asset["content_type"] == "application/zip":
            print(asset["size"])
            sys.exit(0)
            while True:
                pass
except:
    pass
sys.exit(1)
