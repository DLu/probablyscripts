
from djikstra import *
from math import *
N = 30
path_constant = 2
map_constant = 98
m = 3
g = make_grid(N, N)

for i in range(N):
    x = abs(N/2-i)
    g[ (i, N/2) ] =min(100, max(0 , 2*path_constant*(m+1)*(m+1)* (x+1)) )
    print x, g[ (i,N/2)]

plan(g, (N/2,0), (N/2,N-1), constant=path_constant)
