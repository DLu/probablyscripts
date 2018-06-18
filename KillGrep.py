#!/usr/bin/python
import psutil
import collections
import sys

USER = 'dlu'

if len(sys.argv) <= 1:
    key = None
else:
    key = sys.argv[1]

D = collections.defaultdict(int)

for proc in psutil.process_iter():
    if USER not in proc.username():
        continue
    if key is None:
        D[proc.name()] += 1
    elif key in proc.name():
        print "Killing: %s" % proc.name(), ' '.join(proc.cmdline())
        proc.terminate()

s = ''
for name, count in sorted(D.items(), key=lambda x: (-x[1], x[0])):
    s += "%02d %-30s " % (count, name)
    if len(s) > 95:
        print s
        s = ''
print s
