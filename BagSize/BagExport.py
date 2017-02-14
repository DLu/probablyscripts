from bnr_data_researcher.baginfo import parse_info
import rosbag, os

BAGS = {'data': 'data_2016-02-23-10-17-08_7.bag',
'shelf': 'data_shelf_2016-02-23-10-17-41_5.bag',
'summary': 'data_summary_2016-02-23-09-44-59_0.bag',
'xtion': 'data_xtion_2016-02-23-10-13-15_3.bag'
}

TIME_FILTER = True
START = 1456240661.06 
END = 1456240868.81

f = open('output.csv', 'w')

for bag_name, filename in BAGS.iteritems():
    print bag_name
    f.write(bag_name + '\n')
    stats = {}
    filenames = {}
    #stats['Total'] = os.path.getsize(filename)
    
    bags = {}
    bag = rosbag.Bag(filename)
    for topic, msg, t in bag.read_messages():
        print bag_name, (t.to_sec()-START), (END-t.to_sec())
        if TIME_FILTER:
            if t.to_sec() < START:
                continue
            elif t.to_sec() > END:
                break
        if topic not in bags:
            clean = topic[1:].replace('/', '_')
            fn = '%s_%s.bag'%(bag_name, clean)
            filenames[topic] = fn
            bags[topic] = rosbag.Bag(fn, 'w')
        bags[topic].write(topic, msg)
    for topic, bag in sorted(bags.items()):
        bag.close()
        bag_fn = filenames[topic]
        stats[topic] = os.path.getsize(bag_fn)
        f.write('%s %d\n'%(topic, stats[topic]))
    

    for k,v in sorted(stats.iteritems()):
        print '%s\t%s'%(k,v)
f.close()
