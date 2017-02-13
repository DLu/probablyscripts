#!/usr/bin/python

import tempfile
import argparse
import subprocess
import os, collections

def fix_string(s, replacements):
    for k,v in replacements:
        s = s.replace(k,v)
    return s

parser = argparse.ArgumentParser()

parser.add_argument('dir1')
parser.add_argument('dir2')
parser.add_argument('-r', '--replacements', nargs='*')

args = parser.parse_args()
replacements = []
if args.replacements:
    for s in args.replacements:
        k,_,v = s.partition('=')
        replacements.append((k,v))

dir3 = tempfile.mkdtemp()

for folder,subdirs,files in os.walk(args.dir2):
    rel = folder.replace(args.dir2, '')
    newdir = dir3 + '/' + rel
    newdir = fix_string(newdir, replacements)
    if not os.path.exists(newdir):
        os.mkdir(newdir)
    for fn in files:
        newfn = fix_string(fn, replacements)
        newpath = newdir + '/' + newfn
        with open(newpath, 'w') as f:
            contents = open( folder + '/' + fn).read()
            contents = fix_string(contents, replacements)
            f.write(contents)

subprocess.call(['meld', args.dir1, dir3])

subprocess.call(['rm', '-rf', dir3])

