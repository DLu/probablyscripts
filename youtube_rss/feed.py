from .youtubeapi import *
import yaml
import sys

MAX_RSS_SIZE = 500


def update(username, download_all, save_it):

    data = yaml.load(
        open('/home/dlu/Projects/probablyscripts/youtube_rss/.private'))

    yt = Youtube(data['email'], data['password'], data['key'])

    if download_all:
        limit = None
    else:
        limit = 20

    subscriptions = yt.get_all_subscriptions(username, limit=limit)
    all_vids = []
    for s in sorted(subscriptions):
        vids = yt.get_videos(s.url)
        all_vids += vids

    if save_it:
        import pickle
        pickle.dump(all_vids, open('allvids.pickle', 'w'))
    else:
        from webhelpers.feedgenerator import DefaultFeed  # python-webhelpers

        feed = DefaultFeed(
            title="%s's YouTube Vids" %
            username,
            link="http://gonzo.probablydavid.com/",
            description="")

        for video in sorted(all_vids, reverse=True)[:MAX_RSS_SIZE]:
            feed.add_item(
                title=video.title,
                link=video.get_link(),
                description=video.description)

        if 'david' in username:
            output = 'youtubefeed.rss'
        else:
            output = '%s.rss' % username

        f = open('/home/dlu/public_html/%s' % output, 'w')
        s = feed.writeString('utf-8')
        f.write(s)
        f.close()

if __name__ == '__main__':
    download_all = '--all' in sys.argv
    save_it = '--save' in sys.argv
    update(download_all, save_it)
