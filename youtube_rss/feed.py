from .youtubeapi import *
from .classes import categorize
import yaml
import sys
import os
from webhelpers.feedgenerator import DefaultFeed  # python-webhelpers

MAX_RSS_SIZE = 200

def create_feed(name, username, subscriptions, yt):
    all_vids = []
    for s in sorted(subscriptions):
        vids = yt.get_videos(s.url)
        all_vids += vids

    feed = DefaultFeed(
            title="%s's YouTube Vids [%s]" %
            (username, name),
            link="http://gonzo.probablydavid.com/",
            description=name)


    for video in sorted(all_vids, reverse=True)[:MAX_RSS_SIZE]:
        feed.add_item(
            title=video.title,
            link=video.get_link(),
            description=video.description)

    folder = '/home/dlu/public_html/%s'%username
    if not os.path.exists(folder):
        os.mkdir(folder)

    filename = '%s/%s.rss'%(folder, name)

    f = open(filename, 'w')
    s = feed.writeString('utf-8')
    f.write(s)
    f.close()

def update(username, download_all):

    data = yaml.load(
        open('/home/dlu/Projects/probablyscripts/youtube_rss/.private'))

    yt = Youtube(data['email'], data['password'], data['key'])

    if download_all:
        limit = None
    else:
        limit = 20

    subscriptions = yt.get_all_subscriptions(username, limit=limit)

    FILES = []

    for category, some_subs in categorize(username, subscriptions).iteritems():
        if category is None:
            category = 'youtubefeed'
        create_feed(category, username, some_subs, yt)
        FILES.append('%s.rss'%category)

    folder = '/home/dlu/public_html/%s'%username
    with open(folder + '/index.html', 'w') as htmlFile:
        htmlFile.write("<h1>%s's Youtube Feeds</h1>\n"%username)
        htmlFile.write('<ul>\n')
        for f in FILES:
            htmlFile.write(' <li><a href="%s">%s</a>\n'%(f, f))
        htmlFile.write('</ul>')

    #if 'david' in username:
    #    output = 'youtubefeed.rss'
    #else:
    #    output = '%s.rss' % username


if __name__ == '__main__':
    download_all = '--all' in sys.argv
    update('daviddavidlu', download_all)
