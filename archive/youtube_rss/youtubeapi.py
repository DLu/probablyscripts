import gdata.youtube
import gdata.youtube.service


class Video:

    def __init__(self, entry):
        self.title = entry.title.text
        self.description = entry.media.description.text
        self.thumbnail = entry.media.thumbnail[0].url
        self.uploader = entry.author[0].name.text
        self.date = entry.published.text
        for link in entry.link:
            href = link.href
            if not 'v=' in href:
                continue
            i = href.index('v=')
            i2 = href.index('&', i)
            self.key = href[i + 2:i2]
            break

    def get_link(self):
        return 'http://www.youtube.com/watch?v=%s' % self.key

    def get_embed_code(self):
        return '<iframe width="560" height="315" src="http://www.youtube.com/embed/%s" frameborder="0" allowfullscreen></iframe>' % self.key

    def __repr__(self):
        return "%s [%s]" % (self.title, self.uploader)

    def __lt__(self, other):
        return self.date < other.date


class Subscription:

    def __init__(self, name, url, date, thumbnail=None, dname=None):
        self.name = name
        self.url = url
        self.date = date
        self.thumbnail = thumbnail
        self.dname = dname

    def __lt__(self, other):
        return self.date < other.date

    def __repr__(self):
        return self.name


class Youtube:

    def __init__(self, email, password, key):
        yt_service = gdata.youtube.service.YouTubeService()
        yt_service.email = email
        yt_service.password = password
        yt_service.ssl = True
        yt_service.developer_key = key
        yt_service.ProgrammaticLogin()

        self.yt_service = yt_service

    def get_all_subscriptions(self, username, increment=50, limit=1):
        start_i = 0
        entries = []
        base = 'https://gdata.youtube.com/feeds/api/users/%s/subscriptions?v=2&' % username
        seen = set()

        while True:
            url = '%smax-results=%d' % (base, increment)
            if start_i > 0:
                url += '&start-index=%d' % start_i
            feed = self.yt_service.GetYouTubeVideoFeed(url)
            c = 0
            for entry in feed.entry:
                name = None
                dname = None
                thumbnail = None
                upload = None
                date = entry.updated.text

                for x in entry.extension_elements:
                    if x.tag == 'username':
                        name = x.text
                        dname = x.attributes['display']
                    elif x.tag == 'thumbnail':
                        thumbnail = x.attributes['url']

                for a in entry.link:
                    if 'upload' in a.href:
                        upload = a.href
                        break

                s = Subscription(name, upload, date, thumbnail, dname)
                if name not in seen:
                    entries.append(s)
                    seen.add(name)


                if limit is not None and len(entries) >= limit:
                    return entries
                c += 1
            if c == 0:
                break
            start_i += increment
        return entries

    def get_videos(self, subscription_uri):
        videos = []
        for entry in self.yt_service.GetYouTubeVideoFeed(subscription_uri).entry:
            videos.append(Video(entry))
        return videos
