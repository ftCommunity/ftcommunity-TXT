#! /usr/bin/env python3
# -*- coding: utf-8 -*-
#
import json
import sys

try:
    data = json.load(sys.stdin)
    for asset in data.get("assets", []):
        ctype = asset.get("content_type", "")
        name = asset.get("name", "")
        if ctype in ("application/zip", "application/x-zip-compressed") or name.lower().endswith(".zip"):
            print(asset["size"])
            sys.exit(0)
except Exception:
    pass
sys.exit(1)
