#!/usr/bin/python

import argparse
import os
import shutil

parser = argparse.ArgumentParser()
parser.add_argument('needle')
parser.add_argument('replacement', nargs='?')

args = parser.parse_args()
print args
for path, folders, files in os.walk('.'):
    for file in files:
        if args.needle not in file:
            continue
        full_path = os.path.join(path, file)
        print full_path
        if args.replacement is None:
            continue
        replacement_path = os.path.join(path, file.replace(args.needle, args.replacement))
        if os.path.exists(replacement_path):
            print "Can't move", full_path
        shutil.move(full_path, replacement_path)
