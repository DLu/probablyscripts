
from djikstra import *
from math import *
N =100
varx = 100
vary =100
path_constant = 50

g = make_grid(N, N)

#for path_constant in range(0,50):
#    c,p = djikstra(g, (0,0), (0,N-1), constant=path_constant)
#    m = max([a[0] for a in p])
#    print "%d\t%d"%(path_constant, m)

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
