from math import *
from pylab import *

def distance(a, b):
    return sqrt( pow(a[0]-b[0],2) + pow(a[1]-b[1],2))
    
def resample(path, resolution):
    np = []
    remaining = 0
    for a,b in zip(path[:-1], path[1:]):
        dx = b[0]-a[0]
        dy = b[1]-a[1]
        angle = atan2(dy, dx)
        ddx = cos(angle) * resolution
        ddy = sin(angle) * resolution
        #if sign(dx)<0 and sign(dy)<0:
        #    ddx *= -1

        d = distance(a,b) - remaining
        N = int(floor(d / resolution))
        for i in range(N+1):
            x = a[0] + i * ddx + cos(angle) * remaining
            y = a[1] + i * ddy + sin(angle) * remaining
            np.append((x,y))
        remaining = resolution - distance(np[-1], b)
    return np

    
    
"""def METRIC_path_distance(path, N):
    d = 0
    for a,b in zip(path[:-1], path[1:]):
        d += distance(a,b)
    return d"""
    
def METRIC_closest_distance(path, N):
    d = 1E100
#    pt = (N*1.5, N/2)
    pt = (N/2, N/2)
    for a in path:
        d2 = distance(a, pt)
        d = min(d,d2)
    return d
    
"""
def METRIC_integral(path, N, resolution=.5):
    center = (N/2, N/2)
    total = 0
    for pt in resample(path, resolution):
        total += resolution * distance(pt, center)
    return total
    """
MAGIC = 'METRIC_'
j = globals().keys()
all_metrics = [(a[len(MAGIC):], globals()[a]) for a in j if MAGIC in a]
