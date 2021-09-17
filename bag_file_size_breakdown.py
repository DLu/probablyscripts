#!/usr/bin/python

import rosbag
import os, sys
import argparse
import collections
import operator

"""
Finds the size of each topic within a set of bagfiles.

The standard version is quicker, and looks at how much space each message
within the bag file takes up. This uses sys.getsizeof and generally underestimates
the size.

The deep version takes longer, and calculates how much space each topic takes
in the bagfile itself, by writing a bagfile that only contains that topic. It is
generally more accurate, although it slightly overestimates the size, because of
the metadata for each individual bag.

"""


# http://stackoverflow.com/questions/1094841/reusable-library-to-get-human-readable-version-of-file-size/1094933#1094933
def sizeof_fmt(num, suffix='B'):
    for unit in ['','Ki','Mi','Gi','Ti','Pi','Ei','Zi']:
        if abs(num) < 1024.0:
            return "%3.1f"%num, "%s%s" % (unit, suffix)
        num /= 1024.0
    return "%.1f"%num, "Yi%s" % suffix

parser = argparse.ArgumentParser()
parser.add_argument('bags', metavar='bagfile', nargs='+')
parser.add_argument('-d', '--deep', action='store_true')
args = parser.parse_args()

totals = collections.defaultdict(int)
total = 0

filenames = {}
bags = {}

try:
    for arg in args.bags:
        bag = rosbag.Bag(arg)
        for topic, msg, t in bag.read_messages():
            if args.deep:
                if topic not in bags:
                    clean = topic[1:].replace('/', '_')
                    fn = '/tmp/%s.bag'%(clean)
                    filenames[topic] = fn
                    bags[topic] = rosbag.Bag(fn, 'w')
                bags[topic].write(topic, msg)
            else:
                size = sys.getsizeof(msg)
                total += size
                totals[topic] += size
    if args.deep:
        for topic, sbag in sorted(bags.items()):
            sbag.close()
            bag_fn = filenames[topic]
            size = os.path.getsize(bag_fn)
            total += size
            totals[topic] += size
finally:
    for k,v in sorted(totals.items(), key=operator.itemgetter(1), reverse=True):
        n, unit = sizeof_fmt(v)
        print('%5s %3s %03s%% %s'%(n, unit,int(v*100/float(total)),k))

    n, unit = sizeof_fmt(total)
    print('\n%5s %3s Total'%(n, unit))

    for filename in bags.values():
        if os.path.exists(bag_fn):
            os.remove(bag_fn)
