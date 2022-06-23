import pathlib

from google_api import GoogleAPI

# If modifying these scopes, delete the token
SCOPES = ['https://www.googleapis.com/auth/contacts', 'https://www.googleapis.com/auth/contacts.other.readonly']
FIELDS = ['addresses', 'birthdays', 'emailAddresses', 'metadata', 'names', 'nicknames', 'phoneNumbers']


class GoogleContactAPI(GoogleAPI):
    # https://developers.google.com/people/v1/contacts

    def __init__(self):
        GoogleAPI.__init__(self, 'people', 'v1', SCOPES,
                           pathlib.Path('~/.config/google_contact_api.yaml').expanduser())

    def get_contact_list(self, fields, limit=0):
        next_token = None
        seen = 0
        while True:
            results = self.service.people().connections().list(
                resourceName='people/me',
                pageToken=next_token,
                pageSize=limit,
                sortOrder='LAST_MODIFIED_DESCENDING',
                personFields=','.join(fields)).execute()
            yield from results['connections']
            seen += len(results['connections'])
            next_token = results.get('nextPageToken')

            if not next_token or (limit and seen >= limit):
                break

    def get_other_contacts(self, fields=['names', 'emailAddresses', 'phoneNumbers'], limit=0):
        next_token = None
        seen = 0
        while True:
            results = self.service.otherContacts().list(
                readMask=','.join(fields),
                pageToken=next_token,
                pageSize=limit
            ).execute()
            yield from results['otherContacts']
            seen += len(results['otherContacts'])
            next_token = results.get('nextPageToken')

            if not next_token or (limit and seen >= limit):
                break

    def update_contact(self, resourceName, person):
        if 'etag' not in person:
            raise RuntimeError('etag not in person')
        fields = []
        for field in person:
            if field == 'etag':
                continue
            elif field not in FIELDS:
                raise RuntimeError(f'person contains weird field: {field}')
            else:
                fields.append(field)
        self.service.people().updateContact(resourceName=resourceName,
                                            updatePersonFields=','.join(fields),
                                            body=person
                                            ).execute()
