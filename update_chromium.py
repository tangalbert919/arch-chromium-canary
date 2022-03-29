import json, urllib.request as request, os

h1 = request.urlopen('https://omahaproxy.appspot.com/all.json?os=win').read().decode('utf-8')
#print(h1)
data = json.loads(h1)
#print(data[0]['versions'][1]['version'])
os.system(f"sed -i '7s/pkgver=[[:digit:]]\{{3\}}[[:punct:]][[:digit:]][[:punct:]][[:digit:]]\{{4\}}[[:punct:]][[:digit:]]/pkgver={data[0]['versions'][1]['version']}/g' PKGBUILD")
