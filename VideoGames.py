import urllib2
import re
import time
import argparse
import os
import random

TITLE_PATTERN = re.compile('<h2>([^<]+)</h2>')
TRACK_PATTERN = re.compile('<tr>\s+<td><a href="([^"]+)">([^<]+)</a></td>')
DOWNLOAD_PATTERN = re.compile('<p><a style="color: #21363f;" href="([^"]+)">Click here to download</a></b>')
#http://downloads.khinsider.com/game-soundtracks/album/donkey-kong-country
def grab(url):
    try:
        print 'Retrieving %s...'%url
        response = urllib2.urlopen(url)
        time.sleep(random.randint(1,5))
        return response.read()
    except urllib2.URLError as e:
        print type(e)

def get_game(url):
    try:
        content = grab(url)
        m = TITLE_PATTERN.search(content)
        title = m.group(1)

        folder = '/home/dlu/Music/Video Games/%s'%title
        if not os.path.exists(folder):
            os.mkdir(folder)

        m2 = TRACK_PATTERN.findall(content)
        for url, name in m2:
            track_page = grab(url)
            m3 = DOWNLOAD_PATTERN.search(track_page)

            mp3 = m3.group(1)

            with open( os.path.join(folder, name), 'w' ) as f:
                f.write( grab(mp3) )
    except urllib2.URLError as e:
        print type(e)

parser = argparse.ArgumentParser()
parser.add_argument('url', nargs='+')
args = parser.parse_args()

for url in args.url:
    get_game(url)
