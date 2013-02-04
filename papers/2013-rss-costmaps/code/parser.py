from functions import *

import argparse

def parse():
    G = globals().keys()[:]
    MAGIC = 'CMAP_'
    functions = [v[len(MAGIC):] for v in G if MAGIC in v]

    parser = argparse.ArgumentParser(description='')
    parser.add_argument('modifier', choices=functions)
    parser.add_argument('-N', '--size', default=100, type=int, nargs="?")
    parser.add_argument('-p', '--pathconstant', default=50, type=int, nargs="?")
    #parser.add_argument('target_filename', default=None, nargs="?")
    #parser.add_argument('-p', '--print', action='store_true', dest='should_print')
    #parser.add_argument('-g', '--graph', action='store_true', dest='should_graph')

    args = parser.parse_args()
    args.fmap = globals()[MAGIC + args.modifier]
    
    return args
