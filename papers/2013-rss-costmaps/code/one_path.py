from djikstra import *
from parser import parse

args = parse()

N = args.size*5
fne, argmap = args.fmap

g = make_grid(N, N)
for (i,j) in g:
    g[ (i,j) ] = fne(i,j,dx=-N/2, dy=-N/2)

plan(g, (N/2,0), (N/2,N-1), constant=args.pathconstant, neighbors=True, **{})
