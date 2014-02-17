#!/usr/bin/python

from datetime import datetime
import youtube_dl
from youtube_dl.PostProcessor import FFmpegExtractAudioPP
from youtube_dl.utils import encodeFilename
import subprocess

#FILENAME = 'podcast.xml'
FOLDER = '/home/dlu/public_html/podcast'
FILENAME = '%s/podcast.xml'%FOLDER

TEMPLATE = """
<item>
<title>%s</title>
<link>http://gonzo.probablydavid.com/podcast/</link>
<guid>http://gonzo.probablydavid.com/podcast/%s</guid>
<description>%s</description>
<enclosure url="http://gonzo.probablydavid.com/podcast/%s" length="%d" type="audio/mpeg"/>
<category>Podcasts</category>
<pubDate>%s</pubDate>
</item>
"""

def formatDate():
    dt = datetime.now()
    return dt.strftime("%a, %d %b %Y %H:%M:%S -0500")


def download_file(url):
    fmt = FOLDER + u'/%(title)s.%(ext)s'
    ext = "mp3"
    ydl = youtube_dl.YoutubeDL({'outtmpl':fmt})
    ydl.add_post_processor(FFmpegExtractAudioPP(preferredcodec=ext))
    ydl.add_default_info_extractors()
    m = ydl.extract_info(url)
    sm = m['entries'][0]
    sm['ext'] = ext
    return ydl.prepare_filename(sm), sm['description']
    
"""def download_base_file(url):
    http://pd.npr.org/anon.npr-mp3/npr/me/2014/01/20140115_me_jbi_robot_soccer.mp3?dl=1"""
   
    
f = open(FILENAME, 'r')
lines = f.readlines()
f.close()

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
        if '.mp3' in arg:
            None
        else:
            filename, description = download_file(arg)
    else:
        filename = arg
        description = ''
    size = os.path.getsize(filename)
    title = raw_input(filename + "?")

    filename = os.path.abspath(filename)
    if FOLDER in filename:
        filename = filename[len(FOLDER)+1:]
    else:
        print "Invalid filename! %s"%filename
        exit(0)

    if len(title) <= 1: 
        base = os.path.split(filename)
        title = os.path.splitext(base[1])[0]
    entry = TEMPLATE % (title, filename, description, filename, size, date)
    newlines.append(entry)
i = -5
lines = lines[:i] + newlines + lines[i:]

f = open(FILENAME, 'w')
for line in lines:
    f.write(line)
f.close()

