#!/usr/bin/python
import sys
import os.path

def get_camel_case(name, first=True):
    parts = name.split('_')
    s = ''
    cap = first

    for part in parts:
        if cap:
            s += part[0].upper()
            s += part[1:]
        else:
            cap = True
            s += part
            
    return s

in_file, out_file = sys.argv[1:3]
in_base = os.path.splitext(in_file)[0]
out_base = os.path.splitext(out_file)[0]

replacements = {get_camel_case(in_base): get_camel_case(out_base), in_base.upper():out_base.upper()}

contents = open(in_file, 'r').read()
for old_s, new_s in replacements.iteritems():
    contents = contents.replace(old_s, new_s)

output = open(out_file, 'w')
output.write(contents)
output.close()
