#!/usr/bin/python
from podcast import YamlPodcast
from pocketpy.pocket import retrieve
from pocketpy.tags import add_tags
import urllib2
import re, os, json
import pprint


def download_base_file(url, out_folder='/home/dlu/public_html/podcast/'):
    if 'podtrac' in url:
        base = url[ url.rindex('/')+1 : ]
    else:
        split = urllib2.urlparse.urlsplit(url)
        base = os.path.basename(split.path)

    response = urllib2.urlopen(url)
    contents = response.read()

    outfile = '%s/%s' % (out_folder, base)
    f = open(outfile, 'w')
    f.write(contents)
    f.close()
    return base


class NPR:
    URL_PATT = re.compile('npr\.org')
    T_PAT = re.compile('<title>(.*)</title>')
    M_PAT = re.compile('<li class="audio-tool audio-tool-download">\s*<a href="([^"]*)"')

class WBUR:
    URL_PATT = re.compile('wbur\.org')
    T_PAT = re.compile('<title>(.*)</title>')
    M_PAT = re.compile('<a href="([^"]*)" class="article-audio-dl" title="Download the audio"')

class WESA:
    URL_PATT = re.compile('wesa\.fm')
    T_PAT = re.compile('<title>(.*) | 90.5 WESA</title>')
    M_PAT = re.compile('<a href="([^"]+)" title="[^"]+" class="jp-play"></a>')


PATTERNS = [NPR, WBUR, WESA]

yaml = '/home/dlu/public_html/podcast/david_misc.yaml'

podcast = YamlPodcast(yaml)

config_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '.creds')
config = json.load(open(config_path))

for key, entry in retrieve(config, verbose=True).iteritems():
    if 'podcast' in entry.get('tags', {}):
        continue
    try:
        url = entry.get('resolved_url', entry.get('given_url', None))
        if url is None:
            continue
        for pattern in PATTERNS:
            if not pattern.URL_PATT.search(url):
                continue
            page = urllib2.urlopen(url).read()
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
    except:
        None

podcast.write_to_file()
