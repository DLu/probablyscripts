#!/usr/bin/python3

from podcast import YamlPodcast
from dateutil.parser import parse
import requests
import pathlib
from xml.dom.minidom import parseString as parse_xml
import warnings

warnings.filterwarnings('ignore', module='urllib')

base_folder = pathlib.Path('/home/dlu/public_html/podcast')
url = 'https://feeds.npr.org/500005/podcast.xml'


podcast = YamlPodcast(base_folder / 'npr_news.yaml')

req = requests.get(url, verify=False)
xml = parse_xml(req.text)
for item in xml.getElementsByTagName('item'):
    title = item.getElementsByTagName('title')[0].childNodes[0].nodeValue
    print(title)
    if 'Trailer' in title:
        continue
    enc = item.getElementsByTagName('enclosure')[0]
    mp3 = enc.getAttribute('url')
    date = parse(item.getElementsByTagName('pubDate')[0].childNodes[0].nodeValue)
    podcast.add_episode(title, mp3, date=date)


podcast.write_to_file()
