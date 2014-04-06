#!/usr/bin/python

from datetime import datetime
import youtube_dl
from youtube_dl.postprocessor.ffmpeg import FFmpegExtractAudioPP
from youtube_dl.utils import encodeFilename
from webhelpers.feedgenerator import DefaultFeed, Enclosure #python-webhelpers
import subprocess
import yaml
import sys
import os

FOLDER = '/home/dlu/public_html/podcast'
HOSTNAME = 'http://gonzo.probablydavid.com/podcast'
#FOLDER = '.'
DFILENAME = '%s/podcast.yaml'%FOLDER
FILENAME = '%s/podcast2.xml'%FOLDER

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
    
def to_local_name(url):
    return url.replace(HOSTNAME, FOLDER)
    
"""def download_base_file(url):
    http://pd.npr.org/anon.npr-mp3/npr/me/2014/01/20140115_me_jbi_robot_soccer.mp3?dl=1"""
   

data = yaml.load( open(DFILENAME, 'r') )

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
    data.append( {'title': title, 'filename': HOSTNAME + "/" + filename, 'length':size, 'type': 'audio/mpeg', 'date': formatDate()} )
    
yaml.dump( data, open(DFILENAME, 'w'))



feed = DefaultFeed(title="David's Miscallaneous Podcasts", link="http://gonzo.probablydavid.com/", description="[description]")

for item in data:
    e = Enclosure(item['filename'], str(item['length']), item['type'])
    if not os.path.exists( to_local_name(item['filename']) ):
        print item['filename']    
    feed.add_item(title=item['title'], categories=["Podcasts"], link=HOSTNAME, enclosure=e, description=item.get('description', ''), pubdate=datetime.strptime(item['date'], '%a, %d %b %Y %H:%M:%S -0500'))

f = open(FILENAME, 'w')
s = feed.writeString('utf-8')
A = ['title', 'link', 'enclosure', 'description', 'pubDate']
D = {'<item>': '\n<item>\n'}
for a in A:
    w = '</%s>'%a
    D[w] = w + '\n'
for a,b in D.iteritems():
    s = s.replace(a,b)
f.write( s )
f.close()
