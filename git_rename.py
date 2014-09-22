#!/usr/bin/python

import subprocess
import sys

OLD_PATTERN = sys.argv[1]
NEW_PATTERN = sys.argv[2]

for arg in sys.argv[3:]:
    if OLD_PATTERN not in arg:
        continue
    parts = list(arg.partition(OLD_PATTERN))
    parts[1] = NEW_PATTERN
    new_arg = ''.join(parts)
    
    cmd = ['git', 'mv', arg, new_arg]
    print cmd
    
    subprocess.call(cmd)
    
