#!/usr/bin/python
import warnings
warnings.simplefilter("ignore", DeprecationWarning)

from kindle.document import *
from kindle.splitter import *
from kindle.gui import Viewer

import sys, os.path
import distutils.spawn

GUI = True
        
if __name__ == '__main__':
    if len(sys.argv)==2:
        infile = sys.argv[1]
        outfile = os.path.splitext(infile)[0] + "_.pdf"
    elif len(sys.argv)==3:
        (infile, outfile) = sys.argv[1:3]
        if os.path.isdir(outfile):
            outfile = outfile + '/' + os.path.split(infile)[1]
    elif distutils.spawn.find_executable('convert') is None:
    	print "Cannot find 'convert' utility. Please make sure ImageMagick is installed."
    	sys.exit(1)
    else:
        print "Usage: kindle_split input.pdf [output.pdf]"%sys.argv[0]
        sys.exit(1)

    d = Document(infile)
    splitter = Splitter(d)

    if GUI:
        v = Viewer(splitter)
        v.print_doc()
        v.spin()
    splitter.save(outfile)

