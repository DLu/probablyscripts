#!/usr/bin/python3

import argparse
import collections
import pathlib

import click

import magic

STARTERS = {
    'JPEG': 'JPG',
    'GIF': 'GIF'
}


def get_type(path):
    s = magic.from_file(str(path))
    for k, v in STARTERS.items():
        if s.startswith(k):
            return v
    if 'MP4' in s or 'MPEG' in s:
        return 'MP4'
    click.secho(f'Cannot find type for {path}: {s}', fg='red')
    exit(-1)


parser = argparse.ArgumentParser()
parser.add_argument('folder', type=pathlib.Path, default=pathlib.Path('/home/dlu/Dropbox/Camera Uploads'), nargs='?')
args = parser.parse_args()

classifications = collections.defaultdict(lambda: collections.defaultdict(list))

for path in args.folder.glob('*.*'):
    t = get_type(path)
    classifications[path.suffix][t].append(path)

# for suffix in classifications:
#   for t in classifications[suffix]:
#      print(suffix, t, len(classifications[suffix][t]))

for bad_png in classifications['.png']['JPG']:
    good_jpg = bad_png.with_suffix('.jpg')
    click.secho(f'Renaming {bad_png}...', fg='blue')
    bad_png.rename(good_jpg)
