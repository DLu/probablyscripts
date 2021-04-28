import pathlib
import urllib

from dateutil import parser as dateparser

import libsonic

import yaml

STANDARD_IGNORE_KEYS = {
    'path',
    'suffix',
    'type',
    'size',
    'bookmarkPosition',
    'bitRate',
    'contentType',
    'isDir',
    'parent',
    'starred',
    'playCount',
    'albumId',
    'artistId',
    'discNumber',
    'transcodedSuffix',
    'transcodedContentType'
}


def set_window_title(s):
    print(f'\33]0;{s}\a', end='', flush=True)


class SubsonicConnection:
    def __init__(self, config_filename='~/.subsonic_config', ignore=None):
        path = pathlib.Path(config_filename).expanduser()
        if not path.exists():
            print(f'{path} not found!')
            exit(-1)
        self.keys = yaml.safe_load(open(path))
        if 'serverPath' not in self.keys:
            self.keys['serverPath'] = 'rest'
        self.conn = libsonic.Connection(**self.keys)
        self.ignore_keys = set(STANDARD_IGNORE_KEYS)
        if ignore:
            self.ignore_keys.update(ignore)

    def process_song(self, song):
        for key in self.ignore_keys:
            if key in song:
                del song[key]
        for k, v in song.items():
            try:
                song[k] = int(v)
            except ValueError:
                pass
        if 'created' in song:
            song['created'] = int(dateparser.parse(song['created']).timestamp())
        return song

    def get_songs_by_genre(self, genre, musicFolderId=None, page=500):
        count = 0
        while True:
            q = self.conn._getQueryDict({'genre': genre,
                                         'count': page,
                                         'offset': count,
                                         'musicFolderId': musicFolderId,
                                         })
            req = self.conn._getRequest('getSongsByGenre.view', q)
            res = self.conn._doInfoReq(req)
            if res['status'] == 'failed':
                print(yaml.safe_dump(res))
                raise RuntimeError(res['error']['message'])
            songs = res['songsByGenre'].get('song', [])
            if len(songs) == 0:
                break

            for song in songs:
                yield self.process_song(song)
                count += 1

    def get_top_level_folders(self):
        mres = self.conn.getMusicFolders()
        for music_folder in mres['musicFolders']['musicFolder']:
            mf_id = music_folder['id']

            ires = self.conn.getIndexes(mf_id)
            for group in ires.get('indexes', {}).get('index', []):
                for folder in group.get('artist', []):
                    yield mf_id, folder['name'], folder['id']

    def get_folder_contents(self, mf_id, top_folder_id):
        queue = [top_folder_id]
        while queue:
            fid = queue.pop(0)
            try:
                fres = self.conn.getMusicDirectory(fid)
            except ConnectionResetError:
                queue.append(fid)

            for child in fres.get('directory', {}).get('child', []):
                if child.get('isDir'):
                    queue.append(child['id'])
                    continue

                tipo = child.get('type')
                if tipo in ['music', 'podcast']:
                    child['folder'] = mf_id
                    yield self.process_song(child)

    def get_streaming_url(self, song_id):
        url = '{baseUrl}:{port}/{serverPath}/stream.view?'.format(**self.keys)

        var = {'id': song_id,
               'c': 'my_python_streamer',
               'u': self.keys['username'],
               'p': self.keys['password'],
               'v': self.conn.apiVersion
               }

        return url + urllib.parse.urlencode(var)

    def display_info(self, song_info):
        print(song_info['title'])
        if 'year' in song_info:
            print(f'{song_info["album"]} ({song_info["year"]})')
        else:
            print(song_info['album'])
        print(song_info.get('artist'))
        print()
        set_window_title('{title} - {album}'.format(**song_info))

    def scrobble(self, song_id):
        self.conn.scrobble(song_id)
