from djikstra import *
from parser import parse

args = parse()

N = args.size
fne, argmap = args.fmap

g = make_grid(N, N)

xs = range(1,100)
ys = []
for x in xs:
    A = x
    for (i,j) in g:
        g[ (i,j) ] = gaussian(i,j, dy=-N/2, varx=varx, vary=vary, A=x)
    c,p = djikstra(g, (0,0), (0,N-1), constant=path_constant)
    m = max([a[0] for a in p])
    print "%d\t%d"%(x, m)
    ys.append(m)
import pylab
pylab.plot(xs,ys)
pylab.show()




g = make_grid(N, N)
for (i,j) in g:
    g[ (i,j) ] = fne(i,j,dx=-N/2, dy=-N/2)

plan(g, (N*3/4,0), (N/4,N-1), constant=args.pathconstant, **{})
