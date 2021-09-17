#!/usr/bin/python3
from podcast import YamlPodcast
from pocketpy.pocket import retrieve
from pocketpy.tags import add_tags
import re
import json
import requests
import pathlib
from urllib.parse import urlsplit


def download_base_file(url, out_folder=pathlib.Path('/home/dlu/public_html/podcast/')):
    if 'podtrac' in url:
        new_url = url[url.rindex('/') + 1:]
        split = urlsplit(new_url)
        base = split.path
    else:
        split = urlsplit(url)
        base = pathlib.Path(split.path).name

    response = requests.get(url)

    outfile = out_folder / base
    with open(outfile, 'wb') as f:
        f.write(response.content)
    return base


class NPR:
    URL_PATT = re.compile(r'npr\.org')
    T_PAT = re.compile(r'<title>(.*)</title>')
    M_PAT = re.compile(r'<li class="audio-tool audio-tool-download">\s*<a href="([^"]*)"')


class WBUR:
    URL_PATT = re.compile(r'wbur\.org')
    T_PAT = re.compile(r'<title>(.*)</title>')
    M_PAT = re.compile(r'<a href="([^"]*)" class="article-audio-dl" title="Download the audio"')


class WESA:
    URL_PATT = re.compile(r'wesa\.fm')
    T_PAT = re.compile(r'<title>(.*) | 90.5 WESA</title>')
    M_PAT = re.compile(r'<a href="([^"]+)" title="[^"]+" class="jp-play"></a>')


PATTERNS = [NPR, WBUR, WESA]

yaml = '/home/dlu/public_html/podcast/david_misc.yaml'

podcast = YamlPodcast(yaml)

parent_folder = pathlib.Path(__file__).parent
config_path = parent_folder / '.creds'
config = json.load(open(config_path))

for key, entry in retrieve(config, verbose=True).items():
    if 'podcast' in entry.get('tags', {}):
        continue
    try:
        url = entry.get('resolved_url', entry.get('given_url', None))
        if url is None:
            continue
        for pattern in PATTERNS:
            if not pattern.URL_PATT.search(url):
                continue
            page = requests.get(url).text
            m = pattern.M_PAT.search(page)
            if not m:
                continue

            fn = download_base_file(m.group(1))
            m2 = pattern.T_PAT.search(page)
            if m2:
                title = m2.group(1)
            else:
                title = m.group(1)
            podcast.add_episode(title, fn, '')
            add_tags(config, [key], 'podcast')
    except Exception:
        raise

podcast.write_to_file()
