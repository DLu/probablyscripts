import yaml
from urlgrabber.grabber import URLGrabber
from youtubeapi import *
import os
import glob
import sys
import collections

BASE = '/home/dlu/Projects/probablyscripts/youtube_rss/data'
SPLITTER = '...'

def get_categories(username):
    folder = BASE + '/' + username

    FOLDERS = {}

    for path, dirs, files in os.walk(folder):
        cat = None
        if folder != path:
            cat = path[ len(folder)+1: ]
        for fn in files:
            name = fn.split(SPLITTER)[0]
            FOLDERS[name] = cat
    return FOLDERS

def categorize(username, subscriptions):
    data = collections.defaultdict(list)
    cats = get_categories(username)
    for sub in subscriptions:
        cat = cats.get(sub.name, None)
        data[cat].append(sub)
    return data

def update_categories(username, subscriptions):
    g = URLGrabber()
    folder = BASE + '/' + username
    if not os.path.exists(folder):
        os.mkdir(folder)

    cats = get_categories(username)
    visited = set()

    for sub in subscriptions:
        if sub.name in visited:
            continue
        elif sub.name in cats:
            del cats[sub.name]
            visited.add(sub.name)
            continue
        else:
            print 'Downloading thumbnail for %s/%s'%(sub.name, sub.dname)
            ft = sub.thumbnail[-3:]
            nf = '%s/%s%s%s.%s'%(folder, sub.name, SPLITTER, sub.dname, ft)
            g.urlgrab(sub.thumbnail, filename=nf)

    for sub in cats:
        print 'Removing thumbnail for %s'%sub
        if cats[sub] is None:
            old_fn = '%s/%s*'%(folder, sub)
        else:
            old_fn = '%s/%s/%s*'%(folder, cats[sub], sub)
        for fl in glob.glob(old_fn):
            print '\t', fl
            os.remove(fl)

if __name__=='__main__':
    if len(sys.argv) > 1:
        username = sys.argv[1]
    else:
        username = 'daviddavidlu'

    data = yaml.load(
        open('/home/dlu/Projects/probablyscripts/youtube_rss/.private'))

    yt = Youtube(data['email'], data['password'], data['key'])


    update_categories(username, yt.get_all_subscriptions(username, limit=None))

