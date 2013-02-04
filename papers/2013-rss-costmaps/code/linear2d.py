from djikstra import *
from functions import *
N =100
path_constant = 1

g = make_grid(N, N)
for (i,j) in g:
    g[ (i,j) ] = linear(i,j,dx=-N/2, dy=-N/2, slope=5)

plan(g, (N/2,0), (N/2,N-1), constant=path_constant)
