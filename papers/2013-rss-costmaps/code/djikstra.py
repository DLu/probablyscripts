from heapq import heappush, heappop
from drawer import MapDrawer
from math import *
LETHAL = 99

def get_nbors(grid, current, eight=False):
    (x,y) = current
    nbors = []
    if eight:
        deltas = [(1,0), (-1,0), (0,1), (0,-1), (1,1), (-1,-1), (-1,1), (1,-1)]
    else:
        deltas = [(1,0), (-1,0), (0,1), (0,-1)]
    for (dx, dy) in deltas:
        nbor = (x + dx, y + dy)
        if nbor in grid:
            nbors.append(nbor)
    return nbors
    
def get_distance(c1, c2):
    return sqrt(pow(c1[0]-c2[0], 2)+pow(c1[1]-c2[1], 2))

def djikstra(grid, start, goal, constant=10, neighbors=0):
    total = {start: grid[start]}
    visited = set()
    current = start
    src = {}
    q = []
    while True:
        if current==goal:
            break
        score = total[current]
        for nbor in get_nbors(grid, current, neighbors):
            if nbor in visited or grid[nbor]>=LETHAL:
                continue
            d = score + grid[nbor] + constant *get_distance(current, nbor)
            if nbor not in total or total[nbor] > d:
                total[nbor] = d
                src[nbor] = current
                heappush(q, (d, nbor))
        visited.add(current)
        
        current = None
        while current is None:
            d, next = heappop(q)
            if next in visited:
                if len(q)==0:
                    return None
            else:
                current = next
    score = total[goal]
    path = [goal]
    current = goal
    while current != start:
        current = src[current]
        path.append(current)
    path.reverse()
    return score, path


def make_grid(W,H):
    grid = {}
    for i in range(W):
        for j in range(H):
            grid[ (i,j) ] = 0
    return grid
    
