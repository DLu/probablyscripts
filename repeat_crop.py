#!/usr/bin/python

import sys
import os

if len(sys.argv)==1:
    exit(0)

px = input("X coordinate? ")
py = input("Y coordinate? ")
w = input("width? ")
h = input("height? ")
name = raw_input("name? ")
extension = raw_input("extension? ")
replace = '-x' in sys.argv

args = "-crop %dx%d+%d+%d +repage"%(w,h,px,py)

for i, arg in enumerate(sys.argv[1:]):
    arg = arg.replace(' ', '\\ ')
    if '-' == arg[0]:
        continue
    if replace:
        None
    else:
        cmd = 'convert %s %s %s%02d.%s'%(arg, args, name, i, extension)
        print cmd
        os.system(cmd)
