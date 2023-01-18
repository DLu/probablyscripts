import pathlib
import json
import yaml

from google.auth.transport.requests import Request
import google.oauth2.credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build


def credentials_to_dictionary(credentials):
    json_s = credentials.to_json()
    return json.loads(json_s)


class GoogleAPI:
    def __init__(self, name, version, scopes, credentials_path, secrets_file_path=pathlib.Path('credentials.json')):
        creds = None
        if credentials_path.exists():
            creds_d = yaml.safe_load(open(credentials_path))
            creds = google.oauth2.credentials.Credentials.from_authorized_user_info(creds_d)

        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(secrets_file_path, scopes)
                creds = flow.run_local_server()
            yaml.dump(credentials_to_dictionary(creds), open(credentials_path, 'w'))

        self.service = build(name, version, credentials=creds)
