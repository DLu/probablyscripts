import argparse
import click
import collections
import pathlib
from tqdm import tqdm

import mutagen

music_types = ['.mp3', '.ogg', '.flac', '.m4a']
needs_work = ['.wav', '.opus', '.mp4', '.aiff']
CANONICAL_GENRES = ['Showtunes', 'Soundtrack', 'Video Game', 'Comedy', 'Classical', 'Rock', 'Muppets', 'Jazz',
                    'Holiday', 'Disney', 'A Cappella', 'Movie Song', 'Childrens', 'Mashup', 'Brass', 'Pop', 'Funk',
                    'Trombone', 'Television', 'Chiptune', 'Dialog', 'Band Music', 'Vocal', 'Oldies', 'Indie', 'Rap',
                    'Choir', 'Disco', 'Techno', 'Karaoke', 'Country', 'Sound Effects', 'Miscellaneous',
                    'Alternative', 'Nerdcore Hip-Hop', 'Ragtime', 'Electronic']


def recursive_glob(folder):
    queue = [folder]
    while queue:
        root = queue.pop(0)
        for subpath in sorted(root.iterdir()):
            if subpath.is_dir():
                queue.append(subpath)
            elif subpath.suffix.lower() in music_types + needs_work:
                yield subpath


def get_genre(id3):
    for field_name in ['genre', 'TCON', '©gen']:
        try:
            if id3.get(field_name):
                key = id3[field_name]
                if isinstance(key, list) and len(key) == 1:
                    key = key[0]
                elif not isinstance(key, str):
                    key = str(key)
                return key
        except ValueError:
            pass


def get_track_id(id3):
    for field_name in ['musicbrainz_trackid', 'TXXX:MusicBrainz Release Track Id']:
        if id3.get(field_name):
            return id3[field_name]


parser = argparse.ArgumentParser()
parser.add_argument('mode', choices=['genre', 'musicbrainz'], default='genre', nargs='?')
parser.add_argument('-f', '--folder', type=pathlib.Path, default=pathlib.Path('/media/bespin/Music/'), nargs='?')
parser.add_argument('-a', '--all-folders', action='store_true')
args = parser.parse_args()

values = collections.Counter()
problem_folders = collections.defaultdict(lambda: collections.defaultdict(list))

try:
    for path in tqdm(list(recursive_glob(args.folder))):
        id3 = mutagen.File(path)

        if args.mode == 'genre':
            genre = get_genre(id3)
            if not genre:
                genre = 'null'
            if genre not in CANONICAL_GENRES:
                problem_folders[path.parent][genre].append(path.name)

            values[genre] += 1
        else:
            tag = get_track_id(id3)
            if tag:
                values[True] += 1
            else:
                values[False] += 1
                problem_folders[path.parent][False].append(path.name)
except KeyboardInterrupt:
    pass

if not values:
    exit(0)

# Print Values
total = 0
solid = 0
for k, v in values.most_common():
    total += v
    s = f'{v:5} {k:20}'
    if k in CANONICAL_GENRES or k is True:
        click.secho(s, fg='white', bg='blue')
        solid += v
    else:
        click.secho(s, fg='black', bg='yellow')
click.secho()

# Print Problem Folders
for folder, folder_values in sorted(problem_folders.items()):
    if not args.all_folders and len(folder_values) == 1 and 'null' in folder_values:
        continue
    click.secho(f'{str(folder):50}', bg='white', fg='black')
    if args.mode == 'musicbrainz':
        continue
    for genre in sorted(folder_values, key=lambda d: -len(folder_values[d])):
        click.secho(f'\t{genre}', fg='yellow')
        for song in sorted(folder_values[genre]):
            click.secho(f'\t\t{str(song)}')


click.secho()
click.secho(f'{solid}/{total} ({solid * 100 / total:.2f})', fg='green')
