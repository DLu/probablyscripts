#!/usr/bin/python

from datetime import datetime

TEMPLATE = """
<item>
<title>%s</title>
<link>http://gonzo.probablydavid.com/podcast/</link>
<guid>http://gonzo.probablydavid.com/podcast/%s</guid>
<description>  </description>
<enclosure url="http://gonzo.probablydavid.com/podcast/%s" length="%d" type="audio/mpeg"/>
<category>Podcasts</category>
<pubDate>%s</pubDate>
</item>
"""

def formatDate():
    dt = datetime.now()
    return dt.strftime("%a, %d %b %Y %H:%M:%S -0500")

f = open('podcast.xml', 'r')
lines = f.readlines()

pd = False
date = formatDate()
for i, line in enumerate(lines):
	if 'lastBuildDate' in line or (not pd and 'pubDate' in line):
		i1 = line.index('>')
		i2 = line.index('<', i1)
		newline = line[:i1+1] + date + line[i2:]
		lines[i] = newline
		if not pd and 'pubDate' in line:
			pd = True

newlines = []

import sys
import os

for arg in sys.argv[1:]:
	if 'http' in arg:
		None
	filename = arg
	size = os.path.getsize(filename)
	title = raw_input(filename + "?")
	if len(title) <= 1: 
		base = os.path.split(filename)
		title = os.path.splitext(base[1])[0]
	entry = TEMPLATE % (title, filename, filename, size, date)
	newlines.append(entry)
i = -5
lines = lines[:i] + newlines + lines[i:]
print "".join(lines)
