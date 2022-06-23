import pathlib
import yaml

from google_api import GoogleAPI


class SheetAPI(GoogleAPI):
    def __init__(self):
        GoogleAPI.__init__(self, 'sheets', 'v4', ['https://www.googleapis.com/auth/spreadsheets.readonly'],
                           pathlib.Path('~/.config/sheet_api.yaml').expanduser())
        self.api = self.service.spreadsheets()
        self.sheet_id = None

    def set_sheet_id(self, sheet_id):
        self.sheet_id = sheet_id

    def get_range(self, range_spec=None):
        return self.api.values().get(spreadsheetId=self.sheet_id, range=range_spec).execute()['values']

    def get_dictionaries(self, range_spec=None):
        rows = []
        labels = None
        for row in self.get_range(range_spec):
            if labels is None:
                labels = row
                continue
            rows.append(dict(zip(labels, row)))
        return rows


s = SheetAPI()
s.set_sheet_id('116bnk0vRaIAU1jKQ54bDLLCuGMJGL6lQ5N8RfU5g-AM')
print(yaml.dump(s.get_dictionaries('Master!A1:G30')))
