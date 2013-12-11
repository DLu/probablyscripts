#!/usr/bin/python

import sys
from time import sleep, time
import argparse
import collections
import datetime
import subprocess
from quotes import get_random_quote

#HOSTS = 'hosts'
HOSTS = '/etc/hosts'
WARNING_SOUND = '/home/dlu/Sounds/smb_warning.wav'

def play_sound(fn):
    subprocess.Popen(['aplay', fn], stderr=subprocess.PIPE).communicate()
    

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
            canonical = domains.split(' ')[0]
            if ip[0]=='#':
                newlines.append( line[1:] )
            else:
                newlines.append( '#' + line )
        else:
            newlines.append(line)

    if found:
        return newlines, canonical
    else:
        return None

def today():
    return datetime.datetime.now().strftime("%Y-%m-%d")

def clock_in(lines, hostname, elapsed):
    if lines[-1][0] == '#':
        date, data = lines[-1][1:].split('|')
        date = date.strip()
        data = collections.defaultdict(float, eval(data))
        if date!=today():
            report(data, True)
            date = today()
            data = collections.defaultdict(float)                    
        insert = False
    else:
        date = today()
        data = collections.defaultdict(float)
        insert = True
    
    
    data[hostname] += elapsed
    
    line = '# %s | %s'%(date, str(dict(data)))
    report(data)
    if insert:
        lines.append(line)
    else:
        lines[-1] = line
    return lines
    
def time_to_string(t):
    s = int(t)%60
    m = int(t/60)%60
    h = int(t/3600)
    return "%02d:%02d:%02d"%(h,m,s)
    

def report(data, yesterday=False):
    if yesterday:
        s = "Yesterday's Report"
    else:
        s = "Today's Report"
        
    print '===== %17s ====='%s 

    total = 0
    
    for host, t in sorted(data.items(), key=lambda a: a[1], reverse=True):
        total += t
        print "%-20s %s"%(host, time_to_string(t))

    print "============================="
    print "%-20s %s"%("Total", time_to_string(total))

def typing_test():
    q = get_random_quote()
    s = ''
    try:
        while s != q[0]:
            print q[0]
            s = raw_input().strip()
    except:
        exit(0)
    print '- %s'%q[1]

parser = argparse.ArgumentParser()
parser.add_argument('hostname', nargs="+")
parser.add_argument('minutes', default=5, type=int, nargs="?")
parser.add_argument('--toggle', action='store_true')
args = parser.parse_args()

typing_test()

seconds = args.minutes * 60

print "Initiating Change" 
lines = read_hosts()
canonicals = []
for hostname in args.hostname:
    lines, canonical = toggle(lines, hostname)
    canonicals.append(canonical)
    if lines is None:
        print "Can't find %s!"%hostname
        exit(0)
write_hosts(lines)

if args.toggle:
    exit(0)
                 
start = time()
    
try:
    while seconds > 0:
        print "Sleeping"
        try:
            sleep(seconds)
        except KeyboardInterrupt:
            print "KILL"
            sleep(1)
            break
            
        play_sound(WARNING_SOUND)
        print "Time is up%s"%('!'*20)
finally:
    elapsed = time() - start

    print "Reverting"
    for hostname in args.hostname:
        lines, canonical = toggle(lines, hostname)

    for canonical in canonicals:
        lines = clock_in(lines, canonical, elapsed)

    write_hosts(lines)

