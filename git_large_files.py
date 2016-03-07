#!/usr/bin/python
import subprocess

def GetHumanReadable(size,precision=2):
    suffixes=['B','KB','MB','GB','TB']
    suffixIndex = 0
    while size > 1024 and suffixIndex < 4:
        suffixIndex += 1 #increment the index of the suffix
        size = size/1024.0 #apply the division
    if suffixIndex==0:
        precision = 0
    return "%.*f%s"%(precision,size,suffixes[suffixIndex])

SHAS = {}
for line in subprocess.check_output('git rev-list --objects --all | sort -k 2', shell=True).split('\n'):
    line = line.strip()
    if len(line)==0:
        continue
    parts = line.split(' ')
    if len(parts)==1:
        continue
    sha, name = line.split(' ')
    SHAS[sha] = name


for line in subprocess.check_output('git gc 2> /dev/null && git verify-pack -v .git/objects/pack/pack-*.idx 2> /dev/null | egrep "^\w+ blob\W+[0-9]+ [0-9]+ [0-9]+$" | sort -k 3 -n -r  ', shell=True).split('\n'):
    parts = line.split(' ')
    if len(parts)<4:
        continue
    sha = parts[0]
    size = parts[4]
    if sha not in SHAS:
        continue
    print '%10s %s'%(GetHumanReadable(int(size), 1), SHAS[sha])

#print SIZES
