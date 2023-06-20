from feedgen.feed import FeedGenerator

import os
import os.path
import yaml
import datetime
import stat
import pytz
import requests


DATE_FORMAT = '%a, %d %b %Y %H:%M:%S -0500'


class Podcast(FeedGenerator):
    def __init__(self, title, link, description, image=None, thumbnail=None, prefix=None):
        FeedGenerator.__init__(self)
        self.load_extension('podcast')
        self.title(title)
        self.my_link = link
        self.link(href=link)
        self.subtitle(description)
        if thumbnail:
            self.logo(thumbnail)
        self.prefix = prefix

    def add_episode(self, url, title, size, description='', date=None, link=None):
        if date is None:
            date = datetime.datetime.now()
        date = pytz.utc.localize(date)
        if self.prefix is not None:
            url = self.prefix + url.replace('http://', '')
        fe = self.add_entry(order='append')
        fe.id(url)
        fe.title(title)
        fe.description(description)
        fe.published(date)
        fe.enclosure(url, str(size), 'audio/mpeg')

    def __repr__(self):
        return self.rss_str(pretty=True).decode()


class YamlPodcast(Podcast):
    def __init__(self, yaml_filename):
        self.filename = yaml_filename
        self.data = yaml.safe_load(open(yaml_filename, 'r'))
        Podcast.__init__(self, self.data['title'], self.data['link'],
                         self.data.get('description', ''),
                         self.data.get('image', ''),
                         self.data.get('thumbnail', ''),
                         self.data.get('prefix', None))

        self.basedir = os.path.dirname(os.path.abspath(self.filename))
        self.folder = self.data.get('folder', self.basedir)
        for ep in sorted(self.data.get('episodes', []),
                         key=lambda ep: datetime.datetime.strptime(ep['date'], DATE_FORMAT)):
            try:
                self.add_yaml_episode(ep)
            except Exception:
                print(ep)
                raise

    def add_yaml_episode(self, ep):
        date = datetime.datetime.strptime(ep['date'], DATE_FORMAT)
        if 'http' not in ep['filename']:
            url = self.my_link + '/' + ep['filename']
        else:
            url = ep['filename']
        Podcast.add_episode(self, url, ep['title'], ep['length'],
                            ep.get('description', ''), date, ep.get('link', self.my_link))

    def add_episode(self, title, filename, description='', date=None):
        if date is None:
            date = datetime.datetime.now()
        if not isinstance(date, str):
            date = date.strftime(DATE_FORMAT)

        if 'http' not in filename:
            full_filename = os.path.join(self.folder, filename)
            size = os.path.getsize(full_filename)
            st = os.stat(full_filename)
            os.chmod(full_filename, st.st_mode | stat.S_IROTH)
        else:
            full_filename = filename

            for ep in self.data['episodes']:
                if filename == ep['filename']:
                    return

            response = requests.head(full_filename)
            size = response.headers['content-length']

        ep = {'title': title, 'filename': filename,
              'length': size, 'date': date, 'description': description}
        self.data['episodes'].append(ep)
        self.data['episodes'].sort(
            key=lambda ep: datetime.datetime.strptime(ep['date'], DATE_FORMAT)
        )
        yaml.safe_dump(self.data, open(self.filename, 'w'), allow_unicode=True)
        self.add_yaml_episode(ep)
        return True

    # def check_files(self):
    #     for item in self.data.get('episodes', []):
    #         if not os.path.exists(to_local_name(item['filename'])):
    #             print(item['filename'])

    def write_to_file(self):
        filename = os.path.join(self.folder, self.data.get('output_fn', 'podcast.xml'))
        with open(filename, 'w') as f:
            f.write(str(self))
