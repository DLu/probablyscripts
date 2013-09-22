from youtubeapi import *
import yaml
import sys

MAX_RSS_SIZE = 200

def update(download_all, save_it):

    data = yaml.load(open('/home/dlu/Projects/probablyscripts/youtube_rss/.private'))

    yt = Youtube(data['email'], data['password'], data['key'])

    if download_all:
        limit = None
    else:
        limit = 20

    subscriptions = yt.get_all_subscriptions('daviddavidlu', limit=limit)
    all_vids = []
    for date, uri in subscriptions:
        print date, uri
        vids = yt.get_videos(uri)
        all_vids += vids

    if save_it:
        import pickle
        pickle.dump(all_vids, open('allvids.pickle', 'w'))
    else:
        from webhelpers.feedgenerator import DefaultFeed #python-webhelpers

        feed = DefaultFeed(title="David's YouTube Vids", link="http://gonzo.probablydavid.com/", description="")

        for video in sorted(all_vids, reverse=True)[:MAX_RSS_SIZE]:
            feed.add_item(title=video.title, link=video.get_link(), description=video.description)

        f = open('/home/dlu/public_html/youtubefeed.rss', 'w')
        s = feed.writeString('utf-8')
        f.write( s )
        f.close()
        
if __name__=='__main__':
    download_all = '--all' in sys.argv
    save_it = '--save' in sys.argv
    update(download_all, save_it)
    
