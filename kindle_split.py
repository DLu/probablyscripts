#!/usr/bin/python3
from kindle.document import Document
from kindle.splitter import Splitter
from kindle.gui import Viewer

import pathlib
import argparse
import distutils.spawn

if __name__ == '__main__':

    if distutils.spawn.find_executable('convert') is None:
        print("Cannot find 'convert' utility. Please make sure ImageMagick is installed.")
        exit(-1)

    parser = argparse.ArgumentParser(description='Split a PDF document up into smaller pieces')
    parser.add_argument('infile', metavar='document', type=pathlib.Path)
    parser.add_argument('outfile', metavar='output_document', nargs="?", type=pathlib.Path)
    parser.add_argument('--no-gui', dest='gui', action='store_false', default=True, help="Run in command line only")
    parser.add_argument('-p', '--pages', type=int, nargs="*")
    parser.add_argument('-m', '--manual', dest="manual", action="store_true", default=False,
                        help="Manually select regions to include")

    args = parser.parse_args()

    if not args.outfile:
        args.outfile = args.infile.with_name(args.infile.stem + '_.pdf')
    elif args.outfile.is_dir():
        args.outfile /= args.infile.name

    d = Document(args.infile, args.pages)
    splitter = Splitter(d, args.manual)

    if args.gui:
        v = Viewer(splitter)
        if args.manual:
            v.mode = 7
        v.print_doc()
        v.spin()
    splitter.save(args.outfile)
