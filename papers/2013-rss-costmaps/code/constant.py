
from djikstra import *

N = 30
dx = 5
path_constant = 1
map_constant = 50

g = make_grid(N, N)

for i in range(N/2-dx, N/2+dx+1):
    g[ (i, N/2) ] = map_constant

plan(g, (N/2,0), (N/2,N-1), constant=path_constant)
