#!/usr/bin/python3
import argparse
import pathlib
import re

import eyed3

import tabulate

key_tags = ['track_num', 'title', 'album', 'artist', 'recording_date', 'genre', 'disc']


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-t', '--title_case', action='store_true')
    parser.add_argument('-w', '--write', action='store_true')
    parser.add_argument('-n', '--overwrite_numbers', action='store_true')
    parser.add_argument('-p', '--pattern', help='regular expression - groups are track and title')
    parser.add_argument('-a', '--album')
    parser.add_argument('-y', '--year')
    parser.add_argument('-g', '--genre')
    parser.add_argument('-r', '--artist')
    args = parser.parse_args()

    rows = []
    tracks = []
    folder = pathlib.Path('.')
    for pattern in ['*.mp3', '*.flac']:
        tracks += folder.glob(pattern)
    tracks.sort()

    if args.pattern:
        pattern = re.compile(args.pattern)

    for i, filename in enumerate(tracks):
        id3 = eyed3.load(filename)
        if not id3:
            print(f'Cannot load id3: {filename}')
            continue
        if id3.tag is None:
            id3.tag = eyed3.id3.tag.Tag()
        if args.overwrite_numbers:
            id3.tag.track_num = i + 1, len(tracks)

        if args.pattern:
            m = pattern.match(filename.stem)
            if m:
                id3.tag.track_num = int(m.group(1)), len(tracks)
                if id3.tag.title:
                    pass
                else:
                    id3.tag.title = f'{m.group(2)}'

            if args.title_case:
                id3.tag.title = id3.tag.title.title()

        if args.artist:
            id3.tag.artist = args.artist

        if args.year:
            id3.tag.recording_date = args.year

        if args.album:
            id3.tag.album = args.album
        if args.genre:
            id3.tag.genre = args.genre

        d = {'filename': filename.stem}
        if id3.tag:
            for tag in key_tags:
                d[tag] = getattr(id3.tag, tag, None)
                if tag == 'track_num':
                    d[tag] = f'{d[tag].count}/{d[tag].total}'

        rows.append(d)

        if args.write:
            id3.tag.save()

    print(tabulate.tabulate(rows, headers='keys'))
