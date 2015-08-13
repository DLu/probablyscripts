from xml.dom import minidom
import sys
from urllib import urlopen

def remove_all(s, a, b):
    while a in s:
        s = s.replace(a,b)
    return s

original, output, pattern = sys.argv[1:]

xmldoc = minidom.parse(urlopen(original))
rss = xmldoc.childNodes[0]
channel = rss.getElementsByTagName('channel')[0]
itemlist = channel.getElementsByTagName('item')
n = len(itemlist)
c = 0
for s in itemlist:
    if not pattern in s.getElementsByTagName('title')[0].childNodes[0].data:
        channel.removeChild(s)
        c+=1
print "Removed %d/%d items"%(c,n)
with open(output, 'w') as f:
    core = xmldoc.toprettyxml().encode('utf8')
    core = remove_all(core, '\t\n', '\n')
    core = remove_all(core, '\n\n', '\n')
    f.write(core)
