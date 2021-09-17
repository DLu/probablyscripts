#!/usr/bin/python

from matplotlib.pyplot import plot, show, legend
import rosbag
import collections
import argparse

parser = argparse.ArgumentParser()
parser.add_argument('bagfile')
parser.add_argument('fields', metavar='field', nargs='+')
args = parser.parse_args()

data = {}
fields = collections.defaultdict(dict)
styles = {}

for field in args.fields:
    topic, _, subfield = field.partition('.')
    if topic[0] != '/':
        styles[field] = topic[0]
        topic = topic[1:]
    data[field] = {}
    fields[topic][subfield] = field

for topic, msg, t in rosbag.Bag(args.bagfile).read_messages():
    if topic not in fields:
        continue
    for subfield, field in fields[topic].iteritems():
        data[field][t.to_sec()] = getattr(msg, subfield)

for field in data:
    dd = sorted(data[field].items())
    plot([a[0] for a in dd], [a[1] for a in dd], styles.get(field, '-'), label=field)
legend()
show()
