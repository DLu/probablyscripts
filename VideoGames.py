import re
import requests
import time
import argparse
import os
import random
import urllib

from bs4 import BeautifulSoup

TITLE_PATTERN = re.compile(r'<h2>([^<]+)</h2>')
DOWNLOAD_PATTERN = re.compile(r'<p><a style="color: #21363f;" href="([^"]+)">Click here to download</a></b>')
#http://downloads.khinsider.com/game-soundtracks/album/donkey-kong-country
def grab(url):
    try:
        response = requests.get(url)
        time.sleep(random.randint(1,5))
        return response.text
    except Exception as e:
        print type(e)

def get_game(url):
    content = grab(url)
    m = TITLE_PATTERN.search(content)
    title = m.group(1)
    print title

    folder = '/home/dlu/Desktop/%s'%title
    if not os.path.exists(folder):
        os.mkdir(folder)

    soup = BeautifulSoup(content, 'lxml')
    table = soup.find('table', {'id': 'songlist'})
    for row in table.find_all('tr'):
        if row.get('id', None):
            continue
        link = row.find('a')

        base = link['href'].split('/')[-1]
        while '%' in base:
            base = urllib.unquote(base)
        print '\t', base

        fn = os.path.join(folder, base)
        if os.path.exists(fn):
            continue

        track_page = grab('https://downloads.khinsider.com' + link['href'])
        soup2 = BeautifulSoup(track_page, 'lxml')
        mp3 = soup2.find('a', {'style': 'color: #21363f;'})

        res = requests.get(mp3['href'])
        with open(os.path.join(folder, fn), 'w' ) as f:
            f.write(res.content)

parser = argparse.ArgumentParser()
parser.add_argument('url', nargs='+')
args = parser.parse_args()

for url in args.url:
    get_game(url)
