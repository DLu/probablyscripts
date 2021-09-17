#!/usr/bin/python3
import subprocess
import collections
import os.path


def GetHumanReadable(size, precision=2):
    suffixes = ['B', 'KB', 'MB', 'GB', 'TB']
    suffixIndex = 0
    while size > 1024 and suffixIndex < 4:
        suffixIndex += 1  # increment the index of the suffix
        size = size / 1024.0  # apply the division
    if suffixIndex == 0:
        precision = 0
    return '%.*f%s' % (precision, size, suffixes[suffixIndex])


SHAS = {}
for line in subprocess.check_output('git rev-list --objects --all | sort -k 2', shell=True).decode().split('\n'):
    line = line.strip()
    if len(line) == 0:
        continue
    parts = line.split(' ')
    if len(parts) == 1:
        continue
    sha, _, name = line.partition(' ')
    SHAS[sha] = name

FileTypes = collections.defaultdict(int)

cmd = 'git gc 2> /dev/null && git verify-pack -v .git/objects/pack/pack-*.idx 2> /dev/null '
cmd += '| egrep "^\\w+ blob\\W+[0-9]+ [0-9]+ [0-9]+$" | sort -k 3 -n -r  '

for line in subprocess.check_output(cmd, shell=True).decode().split('\n'):
    parts = line.split(' ')
    if len(parts) < 4:
        continue
    sha = parts[0]
    size = int(parts[4])
    if sha not in SHAS:
        continue
    print('%10s %s' % (GetHumanReadable(size, 1), SHAS[sha]))
    ft = os.path.splitext(SHAS[sha])[-1]
    FileTypes[ft] += size
print()
for ft, size in sorted(FileTypes.items(), key=lambda x: x[1], reverse=True):
    print('%10s %s' % (GetHumanReadable(int(size), 1), ft))

# print SIZES
