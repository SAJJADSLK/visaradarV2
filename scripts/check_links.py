#!/usr/bin/env python3
"""Checks every official-source link written by build.py (data/official_links.json). Run from a network that can reach them."""
import json,sys,urllib.request
bad=0
for u in sorted(set(json.load(open("data/official_links.json")))):
    try:
        r=urllib.request.urlopen(urllib.request.Request(u,headers={"User-Agent":"VisaRadar-linkcheck"}),timeout=20); print("OK ",r.status,u)
    except Exception as x: bad+=1; print("BAD",u,x)
sys.exit(1 if bad else 0)
