#!/usr/bin/python3

from podcast import YamlPodcast

import youtube_dl
from youtube_dl.postprocessor.ffmpeg import FFmpegExtractAudioPP
from mutagen.easyid3 import EasyID3
import argparse
import pathlib
from urllib.parse import urlsplit
import requests

FOLDER = pathlib.Path('/home/dlu/public_html/podcast/')


def download_file(url, out_folder):
    fmt = out_folder + u'/%(title)s.%(ext)s'
    ext = 'mp3'
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
    split = urlsplit(url)
    fn = pathlib.Path(split.path)
    outfile = pathlib.Path(out_folder) / fn.name
    response = requests.get(url)
    with open(outfile, 'wb') as f:
        f.write(response.content)

    return fn.name, ''


STATIC_PATTERNS = [
    (pathlib.Path('/home/dlu/Dropbox/Podcasts/'), '*.mp3'),
]


def static_files():
    files = []
    for folder, g_pattern in STATIC_PATTERNS:
        for subpath in folder.glob(g_pattern):
            subpath.rename(FOLDER / subpath.name)
            files.append(subpath.name)
    return files


yaml = FOLDER / 'david_misc.yaml'
files = []

parser = argparse.ArgumentParser()
parser.add_argument('filenames', metavar='filename', nargs='*')
parser.add_argument('-p', '--prompt', action='store_true')
args = parser.parse_args()

for filename in args.filenames:
    if filename.endswith('.yaml'):
        yaml = filename
    else:
        files.append(filename)

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
        title = input(filename + '? ')
    if len(title) <= 1:
        path = pathlib.Path(filename)
        title = path.stem
    if args.prompt:
        description = input('Description for %s? ' % title)

    podcast.add_episode(title, filename, description)

podcast.write_to_file()
