#!/usr/bin/python

import rospy
import datetime
from rosgraph_msgs.msg import Clock
last = None

def cb(msg):
    global last
    x = datetime.datetime.fromtimestamp(int(msg.clock.to_sec()))
    s = x.strftime('%Y-%m-%d %H:%M:%S')
    if s != last:
        last = s
        print(last)


rospy.init_node('clock_watcher')
sub = rospy.Subscriber('/clock', Clock, cb)
rospy.spin()
