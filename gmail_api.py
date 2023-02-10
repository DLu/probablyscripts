import collections
import pathlib
import base64
import mimetypes
from google_api import GoogleAPI
from email.message import EmailMessage
from email.utils import COMMASPACE

# If modifying these scopes, delete the token
SCOPES = ['https://www.googleapis.com/auth/gmail.send',
          'https://www.googleapis.com/auth/gmail.readonly',
          'https://www.googleapis.com/auth/gmail.modify'
          ]


class GMailAPI(GoogleAPI):
    # https://developers.google.com/gmail/api

    def __init__(self, **kwargs):
        GoogleAPI.__init__(self, 'gmail', 'v1', SCOPES,
                           pathlib.Path('~/.config/gmail_api.yaml').expanduser(), **kwargs)

    def send_email(self, subject='', text='', send_to=[], bcc=[], send_from=None, html=False, files=[], images={}):
        assert isinstance(send_to, list)
        assert isinstance(bcc, list)
        if len(send_to) == 0:
            print('No recipients.')
            return

        message = EmailMessage()
        message.make_mixed()

        message['To'] = COMMASPACE.join(send_to)
        message['Subject'] = subject
        if bcc:
            message['BCC'] = COMMASPACE.join(bcc)
        if send_from:
            message['From'] = send_from

        if html:
            message.add_attachment(text, subtype='html')
        else:
            message.set_content(text)

        for fn in files:
            fn = pathlib.Path(fn)
            if not fn.exists():
                raise RuntimeError(f'Cannot find file: {fn}')

            with open(fn, 'rb') as fil:
                message.add_attachment(fil.read(), maintype='application', subtype='octet-stream',
                                       filename=fn.name)

        for cid, fn in images.items():
            fn = pathlib.Path(fn)
            if not fn.exists():
                raise RuntimeError(f'Cannot find image: {fn}')

            the_type = mimetypes.guess_type(fn)[0].split('/')
            with open(fn, 'rb') as im_f:
                message.add_attachment(im_f.read(),
                                       maintype=the_type[0],
                                       subtype=the_type[1],
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

    def get_messages(self, query='', user_id='me'):
        """List all Messages of the user's mailbox matching the query.

        Args:
          query: String used to filter messages returned.
                 Eg.- 'from:user@some_domain.com' for Messages from a particular sender.
          user_id: User's email address. The special value "me" can be used to indicate the authenticated user.

        Returns:
        List of Messages that match the criteria of the query. Note that the
        returned list contains Message IDs, you must use get with the
        appropriate ID to get the details of a Message.
        """
        response = self.service.users().messages().list(userId=user_id,
                                                        q=query).execute()
        messages = []
        if 'messages' in response:
            messages.extend(response['messages'])

        while 'nextPageToken' in response:
            page_token = response['nextPageToken']
            response = self.service.users().messages().list(userId=user_id, q=query, pageToken=page_token).execute()
            if 'messages' in response:
                messages.extend(response['messages'])

        return messages

    def get_threads(self, query='in:inbox', user_id='me'):
        threads = collections.defaultdict(list)
        for m in self.get_messages(query, user_id):
            threads[m['threadId']].append(m)
        return dict(threads)

    def get_message(self, msg_id, user_id='me'):
        """Get a Message with given ID.

          Args:
            user_id: User's email address. The special value "me"
            can be used to indicate the authenticated user.
            msg_id: The ID of the Message required.

          Returns:
            A Message.
        """
        message = self.service.users().messages().get(userId=user_id, id=msg_id).execute()
        return message

    def get_thread(self, thread_id, user_id='me'):
        message = self.service.users().threads().get(id=thread_id, userId=user_id, format='minimal').execute()
        return message

    def get_labels(self, user_id='me'):
        response = self.service.users().labels().list(userId=user_id).execute()
        return response['labels']

    def add_labels(self, msg_id, msg_labels, user_id='me'):
        body = {'addLabelIds': msg_labels, 'removeLabelIds': []}
        message = self.service.users().messages().modify(userId=user_id, id=msg_id, body=body).execute()
        return message
