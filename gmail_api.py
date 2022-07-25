import pathlib
import base64
from google_api import GoogleAPI
from email.message import EmailMessage
from email.utils import COMMASPACE

# If modifying these scopes, delete the token
SCOPES = ['https://www.googleapis.com/auth/gmail.send']


class GMailAPI(GoogleAPI):
    # https://developers.google.com/gmail/api

    def __init__(self):
        GoogleAPI.__init__(self, 'gmail', 'v1', SCOPES,
                           pathlib.Path('~/.config/gmail_api.yaml').expanduser())

    def send_email(self, subject='', text='', send_to=[], bcc=[], send_from=None, html=False, files=[], images={}):
        assert isinstance(send_to, list)
        assert isinstance(bcc, list)
        if len(send_to) == 0:
            print('No recipients.')
            return

        message = EmailMessage()
        message.make_alternative()

        message['To'] = COMMASPACE.join(send_to),
        message['Subject'] = subject
        if bcc:
            message['BCC'] = COMMASPACE.join(bcc)
        if send_from:
            message['From'] = send_from

        if html:
            message.add_alternative(text.encode('utf-8'), maintype='text', subtype='html')
        else:
            message.set_content(text)

        for fn in files:
            fn = pathlib.Path(fn)
            if not fn.exists():
                raise RuntimeError(f'Cannot find file: {fn}')

            with open(fn, 'rb') as fil:
                message.add_alternative(fil.read(), maintype='application', subtype='octet-stream',
                                        filename=fn.name)

        for cid, fn in images.items():
            raise NotImplementedError("Inline images currently don't work.")
            fn = pathlib.Path(fn)
            if not fn.exists():
                raise RuntimeError(f'Cannot find image: {fn}')

            with open(fn, 'rb') as im_f:
                message.add_alternative(im_f.read(),
                                        maintype='application',
                                        subtype='octet-stream',
                                        cid=f'<{cid}>',
                                        disposition='inline')
        self.send_email_message(message)

    def send_email_message(self, message, debug=False):
        create_message = {
            'raw': base64.urlsafe_b64encode(message.as_bytes()).decode()
        }
        ret = self.service.users().messages().send(userId='me', body=create_message).execute()
        if debug:
            print(ret)
