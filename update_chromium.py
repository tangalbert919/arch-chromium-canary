#!/usr/bin/python

import json, urllib.request as request, os

h1 = request.urlopen('https://versionhistory.googleapis.com/v1/chrome/platforms/win/channels/canary/versions').read().decode('utf-8')
#print(h1)
data = json.loads(h1)
#print(data['versions'][0]['version'])
os.system(f"sed -i '7s/pkgver=[[:digit:]]\{{3\}}[[:punct:]][[:digit:]][[:punct:]][[:digit:]]\{{4\}}[[:punct:]][[:digit:]]/pkgver={data['versions'][0]['version']}/g' PKGBUILD")
