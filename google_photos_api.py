import pathlib

from google_api import GoogleAPI

SCOPES = ['https://www.googleapis.com/auth/photoslibrary',
          'https://www.googleapis.com/auth/photoslibrary.appendonly',
          'https://www.googleapis.com/auth/photoslibrary.sharing']


class GooglePhotosAPI(GoogleAPI):
    def __init__(self, **kwargs):
        GoogleAPI.__init__(self, 'photoslibrary', 'v1', SCOPES,
                           pathlib.Path('~/.config/google_photos_api.yaml').expanduser(),
                           static_discovery=False, **kwargs)

    def get_albums(self):
        yield from self.get_paged_result(
            self.service.albums().list,
            'albums',
        )

    def get_album_contents(self, album_id):
        # Annoyingly, for this call, pageToken goes in body
        next_token = None
        while True:
            results = self.service.mediaItems().search(
                body={'albumId': album_id, 'pageToken': next_token},
            ).execute()

            yield from results['mediaItems']
            next_token = results.get('nextPageToken')

            if not next_token:
                break
