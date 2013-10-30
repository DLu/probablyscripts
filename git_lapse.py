#!/usr/bin/python

import subprocess
import sys
from math import ceil

def get_commits(filename):
    a = []
    p = subprocess.Popen(['git', 'log', filename], stdout=subprocess.PIPE)
    out, x = p.communicate()
    out = '\n\n'+out
    for b in out.split('\n\ncommit '):
        lines = b.split('\n')
        commit = lines[0].strip()
        if len(commit) == 0:
            continue
        x = {}
        x['commit'] = commit
        x['date'] = lines[2][8:]
        a.append(x)
    a.reverse()
    return a
    
def checkout(c):
    p = subprocess.Popen(['git', 'checkout', c])
    p.communicate()
    
def build_git(fn='paper.tex'):
    # TODO: Insert 'PDFLATEX_FLAGS="-interaction=batchmode"'
    p = subprocess.Popen(['latex-mk', '--pdflatex', fn], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    out, err = p.communicate()
    # TODO: Catch Error
    newfn = fn[:-4] + '.pdf'
    # TODO: Save version
    
def get_dimensions(num_pages, total_pages):
    for cols in range(1, total_pages):
        rows = ceil(total_pages/float(cols))
        ratio = rows * 11 / (cols * 8.5)
        if ratio < 1.0:
            return rows, cols
    
def make_image(pdf_file, image_file, total_pages=None):
    num_pages = 8 # TODO: Get number of pages
    if total_pages is None:
        total_pages = num_pages
    rows, cols = get_dimensions(num_pages, total_pages)
#commits = get_commits(sys.argv[1])
#for commit in commits:
#    h = commit['commit']
#    checkout(h)
    
#checkout('master')

#make_image('paper.pdf', 'paper.png')
