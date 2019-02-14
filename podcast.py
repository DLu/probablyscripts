from webhelpers.feedgenerator import DefaultFeed, Enclosure  # python-webhelpers
import os
import os.path
import yaml
import datetime
import stat
import requests

DATE_FORMAT = '%a, %d %b %Y %H:%M:%S -0500'

class Podcast(DefaultFeed):
    def __init__(self, title, link, description, image=None, thumbnail=None, prefix=None):
        DefaultFeed.__init__(self, title=title, link=link, description=description)
        self.title = title
        self.link = link
        self.image = image
        self.thumbnail = thumbnail
        self.prefix = prefix

    def add_episode(self, url, title, size, description='', date=None, link=None):
        if date is None:
            date = datetime.datetime.now()
        if self.prefix is not None:
            url = self.prefix + url.replace('http://', '')
        if link is None:
            link = self.link
        e = Enclosure(url, str(size), 'audio/mpeg')
        self.add_item(title=title, categories=['Podcasts'], link=link,
                      enclosure=e, description=description, pubdate=date)

    def __repr__(self):
        s = self.writeString('utf-8')
        A = ['title', 'link', 'enclosure', 'description', 'pubDate']
        D = {'<item>': '\n<item>\n'}
        for a in A:
            w = '</%s>' % a
            D[w] = w + '\n'
        for a, b in D.iteritems():
            s = s.replace(a, b)
        if self.image and len(self.image):
            s = s.replace('<channel>', """<channel>
<itunes:image href="%s" />
""" % self.image)
        if self.thumbnail and len(self.thumbnail):
            s = s.replace('<channel>', """<channel>
<image>
 <url>%s</url>
 <title>%s</title>
 <link>%s</link>
</image>""" % (self.thumbnail, self.title, self.link))

        if self.image and len(self.image):
            s = s.replace('<rss ', '<rss xmlns:atom="http://www.w3.org/2005/Atom" xmlns:itunes="http://www.itunes.com/dtds/podcast-1.0.dtd" xmlns:itunesu="http://www.itunesu.com/feed" ')

        return s

class YamlPodcast(Podcast):
    def __init__(self, yaml_filename):
        self.filename = yaml_filename
        self.data = yaml.load(open(yaml_filename, 'r'))
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
            except:
                print ep

    def add_yaml_episode(self, ep):
        date = datetime.datetime.strptime(ep['date'], DATE_FORMAT)
        if 'http' not in ep['filename']:
            url = self.link + '/' + ep['filename']
        else:
            url = ep['filename']
        Podcast.add_episode(self, url, ep['title'], ep['length'],
                            ep.get('description', ''), date, ep.get('link', self.link))

    def add_episode(self, title, filename, description='', date=None):
        if date is None:
            date = datetime.datetime.now()
        if type(date) is not str and type(date) is not unicode:
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

        print full_filename
        ep = {'title': title, 'filename': filename,
              'length': size, 'date': date, 'description': description}
        self.data['episodes'].append(ep)
        yaml.safe_dump(self.data, open(self.filename, 'w'), allow_unicode=True)
        self.add_yaml_episode(ep)

    def check_files(self):
        for item in self.data.get('episodes', []):
            if not os.path.exists(to_local_name(item['filename'])):
                print item['filename']

    def write_to_file(self):
        filename = os.path.join(self.folder, self.data.get('output_fn', 'podcast.xml'))
        with open(filename, 'w') as f:
            f.write(str(self))
