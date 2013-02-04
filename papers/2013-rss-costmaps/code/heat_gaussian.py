
from djikstra import *
import pylab as pl

N =100
varx = N*2
vary =N*2
resolution = 1


g = make_grid(N, N)
data = []
for a in range(1,100,resolution):
    data.append([])
    for (i,j) in g:
        g[ (i,j) ] = gaussian(i,j, dy=-N/2, A=a)
    for path_constant in range(1,100,resolution):
        print a,path_constant
        c,p = djikstra(g, (0,0), (0,N-1), constant=path_constant)
        m = max([w[0] for w in p])
        data[-1].append(m)
      

data = pl.array(data) 
pl.pcolor(data)
pl.colorbar()
pl.show()

