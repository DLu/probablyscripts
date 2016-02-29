from webhelpers.feedgenerator import DefaultFeed, Enclosure #python-webhelpers
import os, os.path
import yaml
import datetime
import stat

DATE_FORMAT = '%a, %d %b %Y %H:%M:%S -0500'

class Podcast(DefaultFeed):
    def __init__(self, title, link, description, image):
        DefaultFeed.__init__(self, title=title, link=link, description=description)
        self.link = link

    def add_episode(self, url, title, size, description='', date=None):
        if date is None:
            date = datetime.datetime.now()        
            
        e = Enclosure(url, str(size), 'audio/mpeg')
        self.add_item(title=title, categories=['Podcasts'], link=self.link,
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
        return s

class YamlPodcast(Podcast):
    def __init__(self, yaml_filename):
        self.filename = yaml_filename
        self.data = yaml.load(open(yaml_filename, 'r'))
        Podcast.__init__(self, self.data['title'], self.data['link'], 
                            self.data.get('description', ''),
                            self.data.get('image', ''))

        self.basedir = os.path.dirname(os.path.abspath(self.filename))
        self.folder = self.data.get('folder', self.basedir)
        for ep in self.data.get('episodes', []):
            self.add_yaml_episode(ep)
            
    def add_yaml_episode(self, ep):        
        date = datetime.datetime.strptime(ep['date'],DATE_FORMAT)
        url = self.link + '/' + ep['filename']
        Podcast.add_episode(self, url, ep['title'], ep['length'], 
                            ep.get('description', ''), date)
                                
    def add_episode(self, title, filename, description=''):
        date = datetime.datetime.now().strftime(DATE_FORMAT)
        full_filename = os.path.join(self.folder, filename)
        print full_filename
        size = os.path.getsize(full_filename)
        st = os.stat(full_filename)
        os.chmod(full_filename, st.st_mode | stat.S_IROTH)
        ep = {'title': title, 'filename': filename,
              'length': size, 'date': date, 'description': description}
        self.data['episodes'].append(ep)
        yaml.dump(self.data, open(self.filename, 'w'))
        self.add_yaml_episode(ep) 
        
    def check_files(self):
        for item in self.data.get('episodes', []):    
            if not os.path.exists(to_local_name(item['filename'])):
                print item['filename']
                
    def write_to_file(self):
        filename = os.path.join( self.folder, self.data.get('output_fn', 'podcast.xml') )
        with open(filename, 'w') as f:
            f.write(str(self))
