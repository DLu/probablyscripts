#!/usr/bin/python

import tempfile
import argparse
import subprocess
import os

parser = argparse.ArgumentParser()

parser.add_argument('dir1')
parser.add_argument('dir2')
parser.add_argument('prefix', default='bnr_', nargs='?')

args = parser.parse_args()

dir3 = tempfile.mkdtemp()

for folder,subdirs,files in os.walk(args.dir2):
	rel = folder.replace(args.dir2, '')
	newdir = dir3 + '/' + rel
	newdir = newdir.replace(args.prefix, '')
	if not os.path.exists(newdir):
		os.mkdir(newdir)
	for fn in files:
		newfn = fn.replace(args.prefix, '')
		newpath = newdir + '/' + newfn
		with open(newpath, 'w') as f:
			contents = open( folder + '/' + fn).read()
			contents = contents.replace(args.prefix, '')
			f.write(contents)

subprocess.call(['meld', args.dir1, dir3])

subprocess.call(['rm', '-rf', dir3])

