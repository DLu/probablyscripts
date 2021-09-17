#!/usr/bin/python

from pysrt import SubRipFile
import sys

subs = SubRipFile.open(sys.argv[1])
for s in subs:
    print s.text
    print s.start.milliseconds
