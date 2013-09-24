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
    found = False

    for line in lines:
        if '\t' not in line:
            newlines.append(line)
            continue
            
        ip, domains = line.split('\t')
        if domain in domains:
            found = True
            if ip[0]=='#':
                newlines.append( line[1:] )
            else:
                newlines.append( '#' + line )
        else:
            newlines.append(line)

    if found:
        return newlines
    else:
        return None

parser = argparse.ArgumentParser()
parser.add_argument('hostname')
parser.add_argument('minutes', default=5, type=int, nargs="?")
parser.add_argument('--toggle', action='store_true')
args = parser.parse_args()

seconds = args.minutes * 60

print "Initiating Change" 
lines = read_hosts()
lines = toggle(lines, args.hostname)
if lines is None:
    print "Can't find %s!"%args.hostname
    exit(0)
write_hosts(lines)

if toggle:
    exit(0)              

print "Sleeping"
sleep(seconds)

print "Reverting"
lines = toggle(lines, args.hostname)
write_hosts(lines)

