import gdata.youtube
import gdata.youtube.service

class Video:
    def __init__(self, entry):
        self.title = entry.title.text
        self.description = entry.media.description.text
        self.thumbnail = entry.media.thumbnail[0].url
        self.uploader = entry.author[0].name.text
        self.date = entry.published.text
        link = entry.link[0].href
        i = link.index('v=')
        i2 = link.index('&', i)
        self.key = link[i+2:i2]
        
    def get_embed_code(self):
        return '<iframe width="560" height="315" src="http://www.youtube.com/embed/%s" frameborder="0" allowfullscreen></iframe>' % self.key

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

        while True:
            url = '%smax-results=%d'%(base, increment)
            if start_i > 0:
                url += '&start-index=%d'%start_i
            feed = self.yt_service.GetYouTubeVideoFeed(url)
            c = 0
            for entry in feed.entry:
                date = entry.published.text 
                for a in entry.link:
                    if 'upload' in a.href:
                        entries.append((date, a.href))
                        break
                if len(entries)>=limit:
                    return entries
                c+=1
            if c==0:
                break
            start_i += increment
        return entries
        
    def get_videos(self, subscription_uri):
        videos = []
        for entry in self.yt_service.GetYouTubeVideoFeed(subscription_uri).entry:
            videos.append(Video(entry))   
        return videos    
      
