#!/usr/bin/python
from pocketpy.pocket import retrieve
import os
import json
import datetime
import collections
from matplotlib.pyplot import plot, show, legend

config_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '.creds')
config = json.load(open(config_path))

add_times = collections.defaultdict(int)
read_times = collections.defaultdict(int)

#date = datetime.datetime.fromtimestamp(int('1467690697'))
#add_times[date]+=1
config['state'] = 'all'


for key, entry in retrieve(config, verbose=False).iteritems():
    added = int(entry[u'time_added'])
    read = int(entry[u'time_read'])
    add_times[datetime.datetime.fromtimestamp(added)] += 1
    if read > 0:
        read_times[datetime.datetime.fromtimestamp(read)] += 1


times = []
read = []
unread = []
total = []
read_c = 0
unread_c = 0

for date in sorted(set(add_times.keys() + read_times.keys())):
    times.append(date)
    a = add_times[date]
    r = read_times[date]
    unread_c += a
    unread_c -= r
    read_c += r

    read.append(read_c)
    unread.append(unread_c)
    total.append(read_c + unread_c)

plot(times, unread, label='Unread')
plot(times, read, label='Read')
plot(times, total, label='Total')
legend()
show()
