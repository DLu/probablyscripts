#!/usr/bin/python

import rospy
from nav_msgs.msg import OccupancyGrid
from collections import Counter
import argparse
done = False

def cb(msg):
    global done
    for value, count in sorted(Counter( msg.data ).items()):
        print '%3s %7s'%(str(value), str(count))
    done = True

parser = argparse.ArgumentParser()
parser.add_argument('topic', default='/map', nargs='?')
args = parser.parse_args(rospy.myargv()[1:])

rospy.init_node('count_values')
sub = rospy.Subscriber(args.topic, OccupancyGrid, cb)
r = rospy.Rate(1)
while not done and not rospy.is_shutdown():
   r.sleep()
