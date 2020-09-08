#!/usr/bin/python3

from podcast import YamlPodcast

import youtube_dl
from youtube_dl.postprocessor.ffmpeg import FFmpegExtractAudioPP
from mutagen.easyid3 import EasyID3
import argparse
import glob
import os
import pathlib
import shutil


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
    filename = ydl.prepare_filename(sm)
    return filename.replace(out_folder + '/', ''), sm['title'], sm['description']


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


STATIC_PATTERNS = [
    '/home/dlu/Desktop/*Disney Dish*mp3',
    '/home/dlu/Dropbox/Podcasts/*mp3'
]


def static_files():
    files = []
    for pattern in STATIC_PATTERNS:
        for filename in glob.glob(pattern):
            base = os.path.basename(filename)
            shutil.move(filename, '/home/dlu/public_html/podcast/' + base)
            files.append(base)
    return files


yaml = '/home/dlu/public_html/podcast/david_misc.yaml'
files = []

parser = argparse.ArgumentParser()
parser.add_argument('filenames', metavar='filename', nargs='*', type=pathlib.Path)
parser.add_argument('-p', '--prompt', action='store_true')
args = parser.parse_args()

for filename in args.filenames:
    if filename.suffix == '.yaml':
        yaml = str(filename)
    else:
        files.append(str(filename))


podcast = YamlPodcast(yaml)

files += static_files()

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
        try:
            audio = EasyID3(podcast.folder + '/' + filename)
            title = audio.get('title', [''])[0]
        except Exception:
            raise

    if len(title) == 0 and args.prompt:
        title = input(filename + "? ")
    if len(title) <= 1:
        title = os.path.splitext(filename)[0]
    if args.prompt:
        description = input('Description for %s? ' % title)

    podcast.add_episode(title, filename, description)

podcast.write_to_file()
