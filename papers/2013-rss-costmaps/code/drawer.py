#!/usr/bin/python
import pygame

class MapDrawer:
    def __init__(self):
        self.width = self.height = 800
        self.screen = pygame.display.set_mode((self.width,self.height))
        self.data = None
        self.path = None
        self.redraw()
        
    def redraw(self, W=None, H=None):
        pygame.draw.rect(self.screen, (0,0,255), (0,0,self.width, self.height))
        if self.data is None:
            pygame.display.flip()
            return
            
        if W is None or H is None:
            for x,y in self.data:
                W = max(W,x)
                H = max(H,y)
            W+=1
            H+=1
            
        w = self.width / W
        h = self.height / H
        w = h = min(w, h)

        bp = max(int(w*5)/2, 1)
        sp = max(int(w*.3)/2, 1)
        lw = max(2,int(w*.1))

        for i in range(H):
            y = h * (H - i - 1)
            for j in range(W):
                x = j * w
                val = self.data[ (j, i) ]
                c = int(255 - val * 255 / 100)
                if c >= 0:
                    pygame.draw.rect(self.screen, (c,c,c), (x,y,w,h))
#                pygame.draw.rect(self.screen, (0,0,0), (x,y,w,h), 1)

        if self.path is not None:
            pts = []

            for pt in self.path:
                (x,y) = pt
                nx = int((x+.5)*w)
                ny = int((H-y-.5)*h)
                if pt == self.path[0]:
                    radius = bp
                    pygame.draw.circle(self.screen, (0,255,0), (nx,ny), radius)
                elif pt == self.path[-1]:
                    radius = bp
                    pygame.draw.circle(self.screen, (255,0,0), (nx,ny), radius)
                else:
                    radius = sp
                pts.append([nx,ny])
            pygame.draw.lines(self.screen, (0,0,255), False, pts, lw)

        pygame.display.flip()
    def draw(self):
        self.redraw()
        raw_input()


