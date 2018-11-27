#!/usr/bin/python
import psutil
import collections
import argparse
import subprocess

def match_pattern(patterns, name):
    for pattern in patterns:
        if pattern == 'ros' and 'Microsoft' in name:
            continue
        if pattern in name:
            return True

USER = 'dlu'
parser = argparse.ArgumentParser()
parser.add_argument('patterns', metavar='pattern', nargs='*')
parser.add_argument('-g', '--gazebo', action='store_true')
args = parser.parse_args()

if args.gazebo:
    args.patterns += ['rviz', 'gz', 'ros']

if len(args.patterns) == 0:
    # Print Processes
    D = collections.defaultdict(int)

    for proc in psutil.process_iter():
        if USER not in proc.username():
            continue
        D[proc.name()] += 1

    rows, columns = map(int, subprocess.check_output(['stty', 'size']).split())
    s = ''
    for name, count in sorted(D.items(), key=lambda x: (-x[1], x[0])):
        new_bit = "%02d %-30s " % (count, name)
        if len(s) < columns and len(s) + len(new_bit) > columns:
            print(s)
            s = new_bit
        else:
            s += new_bit
    print(s)
else:
    for proc in psutil.process_iter():
        if USER not in proc.username():
            continue
        elif match_pattern(args.patterns, proc.name()):
            print("Killing: %s" % proc.name() + ' '.join(proc.cmdline()))
            proc.terminate()
