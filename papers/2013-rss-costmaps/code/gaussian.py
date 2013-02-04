from super_script import *
from metrics import METRIC_closest_distance
import sys

(function, name, args, params, unknowns) = get_args(['gaussian', 'P:50', 'A:95'])

def d(v):
    params['var'] = v
    g, score, path = super_path(function, args, params)
    return METRIC_closest_distance(path, params.get('N'))
    
print d(float(sys.argv[1]))
