from math import *

def gaussian(x, y, dx=0, dy=0, A=99, var=100):
    x += dx
    y += dy
    h = sqrt(x*x+y*y)
    angle = atan2(y,x)
    mx = cos(angle) * h
    my = sin(angle) * h
    f1 = pow(mx, 2.0)/(2.0 * var)
    f2 = pow(my, 2.0)/(2.0 * var)
    return A * exp(-(f1 + f2))
    
CMAP_gaussian = (gaussian, {'A':[0,100,99], 'var':[1,1500,100]})

def linear(x, y, dx=0, dy=0, A=99, slope=1, power=2):
    x += dx
    y += dy
    d = sqrt(pow(x,2)+pow(y,2))
    return max(A-pow(d,power)*slope, 0)
    
CMAP_distance = (linear, {'A':[0,100, 99], 'slope':[0.1, 10, 1], 'power':[1,10,2]})

def inverse(x, y, dx=0, dy=0, A=99, factor=1, power=1, addend=1):
    x += dx
    y += dy
    d = sqrt(pow(x,2)+pow(y,2))
    return A / (factor * pow(d,power) + addend)
    
CMAP_inverse = (inverse, {'A': [0, 100, 99], 'factor':[.01,.1,.1], 'power':[1,5,1]})

def constant(x, y, dx=0, dy=0, A=50, xd=5, yd=5):
    x += dx
    y += dy
    if abs(x)<=xd and abs(y)<=yd:
        return A
    else:
        return 0
        
CMAP_constant = (constant, {'A': [0, 100, 20], 'xd': [0, 20, 5], 'yd': [0, 50, 5]})


