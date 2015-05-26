#!/usr/bin/python

import subprocess
import os
import mimetypes

for root, dirs, files in os.walk('.'):
    for fn in files:
        if '~' in fn:
            continue
        full = root + '/' + fn
        ftype = mimetypes.guess_type(full)[0]
        
        if not ftype or not ('text' in ftype or 'x-httpd-php' in ftype):
            print ftype
            continue
        s = raw_input(full)
        if 'q' in s or 'x' in s:
            exit(1)
        elif s == 'sf':
            break
        elif 's' in s:
            continue
        else:
            if 'x-tex' in ftype:
                mode = ['--mode=tex']
            elif 'html' in ftype or 'php' in ftype:
                mode = ['--mode=html']
            elif 'java' in ftype:
                mode = ['--mode=ccpp']
            else:
                mode = []
            subprocess.call(['aspell'] + mode + ['-x', '-c', full])

