from xml.dom import minidom

def remove_all(s, a, b):
    while a in s:
        s = s.replace(a,b)
    return s

xmldoc = minidom.parse('/home/dlu/Desktop/rebelforce.xml')
rss = xmldoc.childNodes[0]
channel = rss.getElementsByTagName('channel')[0]
itemlist = channel.getElementsByTagName('item')
for s in itemlist:
    if not 'Oxygen' in s.getElementsByTagName('title')[0].childNodes[0].data:
        channel.removeChild(s)

with open('/home/dlu/Desktop/filtered.xml', 'w') as f:
    core = xmldoc.toprettyxml().encode('utf8')
    core = remove_all(core, '\t\n', '\n')
    core = remove_all(core, '\n\n', '\n')
    f.write(core)
