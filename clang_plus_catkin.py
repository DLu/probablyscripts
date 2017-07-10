#!/usr/bin/python

import os
import re
import argparse
import rospkg
import subprocess

rp = rospkg.RosPack()

INCLUDE_PATTERN = re.compile('clangIncludePaths: \[([^\]]+)\]', re.DOTALL)

parser = argparse.ArgumentParser()
parser.add_argument('packages', metavar='package', nargs='+')
parser.add_argument('-t', '--test', action='store_true')
args = parser.parse_args()

fn = os.path.expanduser('~/.atom/config.cson')
contents = open(fn).read()

m = INCLUDE_PATTERN.search(contents)
if not m:
    print 'Cannot find proper section of config file!'
    exit(0)
path_str = m.group(1)
lines = path_str.split('\n')
includes = []
indent = None
for line in lines:
    if len(line.strip()) == 0:
        continue
    if indent is None:
        indent = 0
        while line[indent] == ' ':
            indent += 1
    path = line.strip()
    if path[0] == '"' and path[-1] == '"':
        path = path[1:-1]
    includes.append(path)

for package in args.packages:
    pkg_path = rp.get_path(package)
    i_path = os.path.join(pkg_path, 'include')
    if os.path.exists(i_path) and i_path not in includes:
        print 'Adding %s...' % i_path
        includes.append(i_path)

try:
    DEVEL = subprocess.check_output(['catkin', 'locate', '-d']).strip()
    d_path = os.path.join(DEVEL, 'include')
    if os.path.exists(d_path) and d_path not in includes:
        print 'Adding %s...' % d_path
        includes.append(d_path)
except:
    None

include_strings = ['']
for line in includes:
    include_strings.append(' ' * indent + '"' + line + '"')
include_strings.append(lines[-1])

new_substr = '\n'.join(include_strings)
contents = contents.replace(path_str, new_substr)

if args.test:
    exit(0)

with open(fn, 'w') as f:
    f.write(contents)
