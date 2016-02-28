#!/usr/bin/python

from podcast import YamlPodcast

import youtube_dl
from youtube_dl.postprocessor.ffmpeg import FFmpegExtractAudioPP
from youtube_dl.utils import encodeFilename

import sys
import os
import urllib2

def download_file(url, out_folder):
    fmt = out_folder + u'/%(title)s.%(ext)s'
    ext = "mp3"
    ydl = youtube_dl.YoutubeDL({'outtmpl': fmt})
    ydl.add_post_processor(FFmpegExtractAudioPP(preferredcodec=ext))
    ydl.add_default_info_extractors()
    m = ydl.extract_info(url)
    if 'entries' in m:
        sm = m['entries'][0]
    else:
        sm = m
    sm['ext'] = ext
    return ydl.prepare_filename(sm), sm['title'], sm['description']


def to_local_name(url):
    return url.replace(HOSTNAME, FOLDER)


def download_base_file(url, out_folder='.'):
    split = urllib2.urlparse.urlsplit(url)
    base = os.path.basename(split.path)

    response = urllib2.urlopen(url)
    contents = response.read()

    outfile = '%s/%s' % (out_folder, base)
    f = open(outfile, 'w')
    f.write(contents)
    f.close()

    return base, ''

yaml = '/home/dlu/public_html/podcast/david_misc.yaml'
files = []
for arg in sys.argv[1:]:
    if arg[-4:]=='yaml':
        yaml = arg
    else:
        files.append(arg)
        
podcast = YamlPodcast(yaml)

for arg in files:
    title = ''
    if 'http' in arg:
        if '.mp3' in arg:
            filename, title = download_base_file(arg, podcast.folder)
            description = ''
        else:
            filename, title, description = download_file(arg, podcast.folder)
    else:
        filename = arg
        description = ''
    
    if len(title) == 0:
        title = raw_input(filename + "? ")

    if len(title) <= 1:
        title = os.path.splitext(filename)[0]
        
    podcast.add_episode(title, filename, description)

podcast.write_to_file()
