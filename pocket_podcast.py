#!/usr/bin/python
from podcast import YamlPodcast
from pocketpy.auth import auth
from pocketpy.pocket import retrieve
from pocketpy.tags import add_tags
import urllib2
import re, os
import pprint


def download_base_file(url, out_folder='/home/dlu/public_html/podcast/'):
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

yaml = '/home/dlu/public_html/podcast/david_misc.yaml'

podcast = YamlPodcast(yaml)

config = auth({})

for key, entry in retrieve(config, verbose=True).iteritems():
    if 'podcast' in entry.get('tags', {}):
        continue
    url = entry.get('resolved_url', entry.get('given_url', None))
    if url is None:
        continue
    if 'npr' in url:
        page = urllib2.urlopen(url).read()
        m = NPR.M_PAT.search(page)
        if m:
            fn = download_base_file(m.group(1))

            m2 = NPR.T_PAT.search(page)
            if m2:
                title = m2.group(1)
            else:
                title = m.group(1)
            podcast.add_episode(title, fn, '')
            add_tags(config, [key], 'podcast')


podcast.write_to_file()
