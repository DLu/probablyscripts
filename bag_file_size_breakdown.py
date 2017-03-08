#!/usr/bin/python
import rosbag, os, argparse

# http://stackoverflow.com/questions/1094841/reusable-library-to-get-human-readable-version-of-file-size/1094933#1094933
def sizeof_fmt(num, suffix='B'):
    for unit in ['','Ki','Mi','Gi','Ti','Pi','Ei','Zi']:
        if abs(num) < 1024.0:
            return "%3.1f"%num, "%s%s" % (unit, suffix)
        num /= 1024.0
    return "%.1f"%num, "Yi%s" % suffix

parser = argparse.ArgumentParser()
parser.add_argument('bagfile')
args = parser.parse_args()

filenames = {}
bags = {}
bag = rosbag.Bag(args.bagfile)
for topic, msg, t in bag.read_messages():
    if topic not in bags:
        clean = topic[1:].replace('/', '_')
        fn = '/tmp/%s.bag'%(clean)
        filenames[topic] = fn
        bags[topic] = rosbag.Bag(fn, 'w')
    bags[topic].write(topic, msg)
bag.close()

stats = {}
for topic, sbag in sorted(bags.items()):
    sbag.close()
    bag_fn = filenames[topic]
    stats[topic] = os.path.getsize(bag_fn)
    os.remove(bag_fn)

for k,v in sorted(stats.items(), key=lambda i: -i[1]):
    n, unit = sizeof_fmt(v)
    print '%5s %3s %s'%(n, unit,k)
