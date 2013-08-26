from youtubeapi import *
import yaml

data = yaml.load(open('.private'))

yt = Youtube(data['email'], data['password'], data['key'])

subscriptions = yt.get_all_subscriptions('daviddavidlu', limit=20)
all_vids = []
for date, uri in subscriptions:
    print date, uri
    vids = yt.get_videos(uri)
    all_vids += vids

import pickle
pickle.dump(all_vids, open('allvids.pickle', 'w'))

