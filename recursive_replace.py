#!/usr/bin/python

import argparse
import os

parser = argparse.ArgumentParser()
parser.add_argument('needle')
parser.add_argument('replacement', nargs='?')

args = parser.parse_args()
print args
for path, folders, files in os.walk('.'):
    if '.git' in path:
        continue
    for file in files:
        full_path = os.path.join(path, file)
        s = open(full_path).read()
        if args.needle in s:
            print full_path, s.count(args.needle)
            if args.replacement is None:
                continue
            s = s.replace(args.needle, args.replacement)
            with open(full_path, 'w') as f:
                f.write(s)
