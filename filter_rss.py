from xml.dom import minidom
xmldoc = minidom.parse('/home/dlu/Desktop/rebelforce.xml')
rss = xmldoc.childNodes[0]
channel = rss.getElementsByTagName('channel')[0]
itemlist = channel.getElementsByTagName('item')
#print(itemlist[0].attributes['name'].value)
for s in itemlist:
    if not 'Oxygen' in s.getElementsByTagName('title')[0].childNodes[0].data:
        channel.removeChild(s)
#    else:
#        print s.getElementsByTagName('title')[0].childNodes[0].data
#    print(s.attributes['name'].value)

with open('/home/dlu/Desktop/filtered.xml', 'w') as f:
    f.write(xmldoc.toprettyxml().encode('utf8'))
