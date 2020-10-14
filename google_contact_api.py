import pathlib

from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

import yaml

# If modifying these scopes, delete the token
SCOPES = ['https://www.googleapis.com/auth/contacts', 'https://www.googleapis.com/auth/contacts.other.readonly']
FIELDS = ['addresses', 'birthdays', 'emailAddresses', 'metadata', 'names', 'nicknames', 'phoneNumbers']

class GoogleContactAPI:
    # https://developers.google.com/people/v1/contacts

    def __init__(self, credentials_path=pathlib.Path('~/.config/google_contact_api.yaml').expanduser()):
        creds = None
        if credentials_path.exists():
            creds = yaml.safe_load(open(credentials_path))

        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
                creds = flow.run_local_server(port=0)
            yaml.dump(creds, open(credentials_path, 'w'))

        self.service = build('people', 'v1', credentials=creds)

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
