from youtubeapi import *
import yaml

data = yaml.load(open('.private'))

yt = Youtube(data['email'], data['password'], data['key'])

subscriptions = yt.get_all_subscriptions('daviddavidlu')
for date, uri in subscriptions:
    vids = yt.get_videos(uri)
    for v in vids:
        print v.title
        print v.get_embed_code()
        
