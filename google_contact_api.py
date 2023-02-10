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
        yield from self.get_paged_result(
            self.service.people().connections().list,
            'connections',
            max_results=limit,
            resourceName='people/me',
            sortOrder='LAST_MODIFIED_DESCENDING',
            personFields=','.join(fields)
        )

    def get_other_contacts(self, fields=['names', 'emailAddresses', 'phoneNumbers'], limit=0):
        yield from self.get_paged_result(
            self.service.otherContacts().list,
            'otherContacts',
            max_results=limit,
            readMask=','.join(fields),
        )

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
