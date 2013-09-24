#!/usr/bin/python

import sys
from time import sleep
import argparse

HOSTS = '/etc/hosts'
#HOSTS = 'hosts'

def read_hosts():
    return open(HOSTS, 'r').readlines()


def write_hosts(lines):
    f = open(HOSTS, 'w')
    for line in lines:
        f.write(line)
    f.close()

def toggle(lines, domain):
    newlines = []

    for line in lines:
        if '\t' not in line:
            newlines.append(line)
            continue
            
        ip, domains = line.split('\t')
        if domain in domains:
            if ip[0]=='#':
                newlines.append( line[1:] )
            else:
                newlines.append( '#' + line )
        else:
            newlines.append(line)

    return newlines

parser = argparse.ArgumentParser()
parser.add_argument('hostname')
parser.add_argument('minutes', default=5, type=int, nargs="?")
args = parser.parse_args()

seconds = args.minutes * 60

print "Initiating Change" 
lines = read_hosts()
lines = toggle(lines, args.hostname)
write_hosts(lines)                

print "Sleeping"
sleep(seconds)

print "Reverting"
lines = toggle(lines, args.hostname)
write_hosts(lines)

