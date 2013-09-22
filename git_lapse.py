#!/usr/bin/python

import subprocess
import sys

def get_commits(filename):
    a = []
    p = subprocess.Popen(['git', 'log', filename], stdout=subprocess.PIPE)
    out, x = p.communicate()
    out = '\n\n'+out
    for b in out.split('\n\ncommit '):
        lines = b.split('\n')
        commit = lines[0].strip()
        if len(commit) == 0:
            continue
        x = {}
        x['commit'] = commit
        x['date'] = lines[2][8:]
        a.append(x)
    a.reverse()
    return a
    
def checkout(c):
    p = subprocess.Popen(['git', 'checkout', c])
    p.communicate()
    
commits = get_commits(sys.argv[1])
for commit in commits:
    h = commit['commit']
    checkout(h)
    
checkout('master')
