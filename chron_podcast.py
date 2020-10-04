#!/usr/bin/python3

from bs4 import BeautifulSoup
from podcast import YamlPodcast
from dateutil.parser import parse
import requests
import os.path
import warnings
warnings.filterwarnings("ignore", category=UserWarning, module='bs4')
warnings.filterwarnings("ignore", module='urllib')

base_folder = '/home/dlu/public_html/podcast'
base_url = 'http://wesa.fm/'
def wesa_podcast(yaml_filename, url):
    podcast = YamlPodcast(os.path.join(base_folder, yaml_filename))
    req = requests.get(base_url + url, verify=False)
    soup = BeautifulSoup(req.text, 'html.parser')

    for x in soup.find_all(class_='node'):
        title_el = x.find(attrs={"property": "dc:title"})
        if not title_el:
            continue
        title = title_el.text
        audio = x.find('audio')
        if audio:
            mp3 = audio['src']
            print(mp3)
        else:
            div = x.find(class_='jp-play')
            if not div:
                continue
            mp3 = div['href']

        dd = x.find(attrs={'property': 'dc:date dc:created'})
        date = parse(dd['content'])
        cap = x.find(class_='audio-caption')
        if cap:
            caption = cap.text
        else:
            caption = 'generic'
        podcast.add_episode(title, mp3, caption, date)
    podcast.write_to_file()


# Original URL: http://wesa.fm/term/905-wesas-good-question?page=1#stream/0
wesa_podcast('good_question.yaml', 'topic/905-wesas-good-question-series#stream/0')
wesa_podcast('good_question.yaml', 'term/built-pgh')
wesa_podcast('ptr.yaml', 'term/pittsburgh-tech-report#stream/0')
