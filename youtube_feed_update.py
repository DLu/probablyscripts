#!/usr/bin/python
from youtube_rss.feed import update
import sys

if len(sys.argv) > 1:
    username = sys.argv[1]
else:
    username = 'daviddavidlu'

update(username, True)
