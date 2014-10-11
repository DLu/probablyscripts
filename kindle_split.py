#!/usr/bin/python
import warnings
warnings.simplefilter("ignore", DeprecationWarning)

from kindle.document import *
from kindle.splitter import *
from kindle.gui import Viewer

import sys
import os.path
import argparse
import distutils.spawn

if __name__ == '__main__':

    if distutils.spawn.find_executable('convert') is None:
        print "Cannot find 'convert' utility. Please make sure ImageMagick is installed."
        sys.exit(1)

    parser = argparse.ArgumentParser(description='Split a PDF document up into smaller pieces')
    parser.add_argument('infile', metavar='document')
    parser.add_argument('outfile', metavar='output_document', nargs="?")
    parser.add_argument('--no-gui', dest='gui', action='store_false', default=True, help="Run in command line only")
    parser.add_argument('-p', '--pages', type=int, nargs="*")
    parser.add_argument('-m', '--manual', dest="manual", action="store_true", default=False, help="Manually select regions to include")

    args = parser.parse_args()

    if not args.outfile:
        args.outfile = os.path.splitext(args.infile)[0] + "_.pdf"
    elif os.path.isdir(args.outfile):
        outfile = outfile + '/' + os.path.split(infile)[1]

    d = Document(args.infile, args.pages)
    splitter = Splitter(d, args.manual)

    if args.gui:
        v = Viewer(splitter)
        if args.manual:
            v.mode = 7
        v.print_doc()
        v.spin()
    splitter.save(args.outfile)
