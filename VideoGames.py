#!/usr/bin/env python3
import argparse
import click
import pathlib
import random
import re
import time
import urllib

from metro_scrape import get_html

import requests

ROOT = pathlib.Path('/home/dlu/')

TITLE_PATTERN = re.compile(r'<h2>([^<]+)<', re.DOTALL)
DOWNLOAD_PATTERN = re.compile(r'<p><a style="color: #21363f;" href="([^"]+)">Click here to download</a></b>')
# http://downloads.khinsider.com/game-soundtracks/album/donkey-kong-country


def random_sleep():
    time.sleep(random.randint(1, 5))


def get_clean_filename(url):
    base = url.split('/')[-1]
    while '%' in base:
        base = urllib.parse.unquote(base)

    return pathlib.Path(base)


def get_game(url, simulate=False):
    page = get_html(url, url.split('/')[-1])
    title_el = page.find('h2', recursive=True)
    assert title_el
    title = title_el.text
    click.secho(title, fg='bright_white', bg='blue')

    folder = ROOT / title
    folder.mkdir(exist_ok=True)

    existing_stems = set(a.stem for a in folder.iterdir())

    table = page.find('table', {'id': 'songlist'})
    for row in table.find_all('tr'):
        if row.get('id', None):
            continue
        link = row.find('a')
        filename = get_clean_filename(link['href'])
        stem = filename.stem

        if stem in existing_stems:
            color = 'bright_cyan'
        else:
            color = 'bright_blue'

        click.secho(f'\t{stem}', fg=color)

        if args.simulate or stem in existing_stems:
            continue

        random_sleep()
        track_page = get_html('https://downloads.khinsider.com' + link['href'], 'kh_download', allow_cached=False)
        dl_link = None
        for the_span in track_page.find_all('span', class_='songDownloadLink'):
            link_el = the_span.parent
            if dl_link is None or 'flac' in link_el['href']:
                dl_link = link_el['href']

        actual_filename = get_clean_filename(dl_link)
        fn = folder / actual_filename

        res = requests.get(dl_link)
        with open(fn, 'wb') as f:
            f.write(res.content)


parser = argparse.ArgumentParser()
parser.add_argument('url', nargs='+')
parser.add_argument('-s', '--simulate', action='store_true')
args = parser.parse_args()

for url in args.url:
    get_game(url, args.simulate)
