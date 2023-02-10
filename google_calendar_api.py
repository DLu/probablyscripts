import pathlib

from google_api import GoogleAPI
# If modifying these scopes, delete the token
SCOPES = ['https://www.googleapis.com/auth/calendar.readonly']


class GoogleCalendarAPI(GoogleAPI):
    # https://developers.google.com/calendar/api/guides/overview

    def __init__(self):
        GoogleAPI.__init__(self, 'calendar', 'v3', SCOPES,
                           pathlib.Path('~/.config/google_calendar_api.yaml').expanduser())

    def get_events(self, calendarId='primary', maxResults=250, **kwargs):
        # https://developers.google.com/calendar/api/v3/reference/events/list
        yield from self.get_paged_result(
            self.service.events().list,
            'items',
            max_results=maxResults,
            max_results_param_name='maxResults',
            calendarId=calendarId,
            **kwargs
        )
