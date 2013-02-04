#!/usr/bin/python

from functions import *
from djikstra import *
from metrics import all_metrics
import sys
import pylab
import matplotlib
from collections import defaultdict
from progressbar import *

OTHER_PARAMS = {'P': [0, 60, 50], 'N': [5, 100, 100], 'angle': [0, 180, 0], 'eight': [0,1,0], 'resolution': [2, 100, 10], 'resolution2': [2,100,10]}
FRACTION = .1

WIDE = False

def get_args(oargs):
    G = globals().keys()[:]
    MAGIC = 'CMAP_'
    functions = [v[len(MAGIC):] for v in G if MAGIC in v]

    function_name = None
    for fne in functions:
        if fne in oargs:
            function_name = fne
            break
    if function_name is None:
        print "Function not specified!"
        print "Options are:"
        for fne in functions:
            print "\t%s"%fne
        exit(1)
          
    (function, args) = globals()[MAGIC + function_name]  
    params = {}
    unknowns = []
    
    for arg in oargs:
        if arg==function_name:
            continue
        elif ':' in arg:
            i = arg.index(':')
            name = arg[:i]
            value = arg[i+1:]
            if name in args or name in OTHER_PARAMS:
                params[name] = float(value)
            else:
                print "Unknown variable %s"%name
                exit(1)
        elif arg in args or arg in OTHER_PARAMS:
            unknowns.append(arg)
        else:
            print "Unknown argument %s"%arg
            exit(1)
            
    for name, (lo, hi, default) in args.items() + OTHER_PARAMS.items():
        if name in params:
            continue
        elif name in unknowns:
            params[name] = (lo, hi)
        else:
            params[name] = default
            
    return function, function_name, args, params, unknowns
    
def super_path(function, args, params):
    N = int( params['N'] )
    if WIDE:
        g = make_grid(N*3, N)
    else:
        g = make_grid(N,N)
    fn_params = {}
    p_params = {}
    
    for param, value in params.iteritems():
        if param in args:
            fn_params[param] = value
            
    for (i,j) in g:
        if WIDE:
            g[ (i,j) ] = function(i,j,dx=-3*N/2, dy=-N/2, **fn_params)
        else:
            g[ (i,j) ] = function(i,j,dx=-N/2, dy=-N/2, **fn_params)

    radius = N/2-N*FRACTION
    angle = params.get('angle', 0)
    s_angle = radians(angle)
    e_angle = radians(angle + 180)
    sx = int(N/2 - cos( s_angle ) * radius)
    sy = int(N/2 + sin( s_angle ) * radius)
    if WIDE:
        ex = 3*N-N*FRACTION-1
    else:
        ex = int(N/2 - cos( e_angle) * radius)
    ey = int(N/2 + sin( e_angle ) * radius)
    (score, path) = djikstra(g, (sx,sy), (ex,ey), constant=params['P'], neighbors=params['eight'])
    return g, score, path
    
def param_values((low, hi), resolution):
    d = hi - low
    values = []
    for i in range(int(resolution)):
        value = low + d * float(i) / (resolution - 1)
        values.append(value)
    return values
    
def clean_text(s):
    return ' '.join(s.split('_')).title()
    
def get_description(params, unknowns):
    desc = []
    for p,v in params.iteritems():
        if p in unknowns:
            continue
        elif p=='eight':
            if v==1.0:
                desc.append('EightConnected')
        elif p in ['resolution', 'angle', 'resolution2']:
            continue
        else:
            desc.append( '%s=%.1f'%(p,v) )
    return ', '.join(desc)   
    
def get_labels(array):
    N = len(array)
    if N<=5:
        return ([a+.5 for a in range(N)], array)
    else:
    
        return ( [0, N], [array[0], array[N-1]])
    
if __name__=='__main__':
    (function, name, args, params, unknowns) = get_args(sys.argv[1:])
    if len(unknowns)==0:
        # One path
        g, score, path = super_path(function, args, params)
        N = int( params['N'] )
        for m_name, metric in all_metrics:
            print m_name, metric(path, N)
        m = MapDrawer()
        m.data = g
        m.path = path
        m.draw()
    elif len(unknowns)==1:
        # graph
        resolution = params['resolution']


        param = unknowns[0]
        the_range = params[param]
        xs = param_values(the_range, resolution)
        ys = defaultdict(list)
        widgets = [Percentage(), ' ', Bar(marker='*',left='[',right=']'),' ', ETA()] 
        pbar = ProgressBar(widgets=widgets, maxval=len(xs))
        pbar.start()
        i = 0
        
        for value in xs:
            params[param] = value
            g, score, path = super_path(function, args, params)
            
            pbar.update(i)
            i += 1
            
            N = int( params['N'] )
            for m_name, metric in all_metrics:
                ys[m_name].append( metric(path, N) )

        desc = get_description(params, unknowns)
        for m_name in ys:
            pylab.plot(xs,ys[m_name], 'o-')
            pylab.xlabel(param)
            cm = clean_text(m_name)
            cn = clean_text(name)
            pylab.title('%s: %s\n%s'%(cm, cn, desc))
            fig = pylab.gcf()
            fig.canvas.set_window_title('%s - %s (%s)'%(cn, desc, cm))
            pylab.show()


    elif len(unknowns)==2:
        # heat map  
        resolution = params['resolution']
        resolution2 = params['resolution2']
        N = int( params['N'] )
        
        param, param2 = unknowns
        range1, range2 = params[param], params[param2]
        xs = param_values(range1, resolution)
        ys = param_values(range2, resolution2)
        print param, xs
        print param2, ys

        data = defaultdict(list)
        widgets = [Percentage(), ' ', Bar(marker='*',left='[',right=']'),' ', ETA()] 
        pbar = ProgressBar(widgets=widgets, maxval=len(xs)*len(ys))
        pbar.start()
        i = 0

        for v1 in xs:
            params[param] = v1
            for m_name, metric in all_metrics:
                data[m_name].append([])

            for v2 in ys:
                pbar.update(i)
                i += 1
                params[param2] = v2
                g, score, path = super_path(function, args, params)
                for m_name, metric in all_metrics:
                    data[m_name][-1].append( metric(path, N) )

        pbar.finish()
                    
        colors = [('black')] + [(pylab.cm.jet(i)) for i in xrange(1,255)] + [('white')]
        new_map = matplotlib.colors.LinearSegmentedColormap.from_list('new_map', colors, N=256)
                    
        desc = get_description(params, unknowns)
        for m_name, metric in all_metrics:    
            cm = clean_text(m_name)
            cn = clean_text(name)
              
            mdata = pylab.array(data[m_name]) 
            pylab.pcolor(mdata, cmap=new_map)
            cbar = pylab.colorbar()
            cbar.set_label(cm)

            pylab.xlabel(param2)
            labels = get_labels(ys)
            pylab.xticks(labels[0], labels[1]) 
            
            pylab.ylabel(param)
            labels = get_labels(xs)
            pylab.yticks(labels[0], labels[1])
            
            pylab.title('%s: %s\n%s'%(cm, cn, desc))
            fig = pylab.gcf()
            fig.canvas.set_window_title('%s - %s (%s)'%(cn, desc, cm))


            pylab.show()
    else:
        print "Too Many Unknowns"
