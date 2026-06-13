import urllib.request
import re

html = urllib.request.urlopen('https://www.templatemaker.nl/en/pillowpack/').read().decode('utf-8')
matches = re.findall(r'<img[^>]+src=[\"\'](.*?)[\"\']', html)
for match in matches:
    print(match)
