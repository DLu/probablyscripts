import pickle
import yaml

from webhelpers.feedgenerator import RssFeed #python-webhelpers

videos = pickle.load(open('allvids.pickle'))
state = yaml.load(open('state'))
cutoff = state['date']

feed = RssFeed(title="Sample Feed", link="alsdkjf", description="David's YouTube Vids")

for video in sorted(videos):
    if video.date > cutoff:
        feed.add_item(title=video.title, link="youtube.com", description=video.description)
        item =feed.items[-1] 
        print item
        print dir(item)
        exit(0)

print feed.writeString('utf-8')
