import yaml
from urlgrabber.grabber import URLGrabber
from youtubeapi import *
import os

BASE = 'youtube_rss/data'
        
if __name__=='__main__':

    data = yaml.load(
        open('/home/dlu/Projects/probablyscripts/youtube_rss/.private'))

    yt = Youtube(data['email'], data['password'], data['key'])
    
    username = 'daviddavidlu'
    g = URLGrabber()
    
    folder = BASE + '/' + username
    if not os.path.exists(folder):
        os.mkdir(folder)
        
    for sub in yt.get_all_subscriptions(username, limit=None):
        print sub.name, sub.dname, sub.thumbnail
        ft = sub.thumbnail[-3:]
        nf = '%s/%s...%s.%s'%(folder, sub.name, sub.dname, ft)

        local_filename = g.urlgrab(sub.thumbnail, filename=nf)        

