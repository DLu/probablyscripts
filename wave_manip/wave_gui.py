import pygame, sys
from pygame.locals import *

class WaveGUI:
    def __init__(self, size=(640,480)):
        pygame.init()
        self.screen = pygame.display.set_mode((640,480))
        self.quit = False
        self.clip = None
        
    def add_clip(self, wave):
        self.clip = wave
        
    def ok(self):
        return not self.quit
        
    def update(self):
        for event in pygame.event.get():
            if event.type==QUIT:
                pygame.quit()
                self.quit = True
                return
        size = self.screen.get_size()
        pygame.draw.rect(self.screen, (255,255,255), Rect((0,0), size))
        
        if self.clip is not None:
            start = (100,100)
            bsize = (440,200)
            midy = start[1] + bsize[1]/2
            pygame.draw.rect(self.screen, (0,0,0), Rect(start, bsize), 1)
            form = self.clip.partition(bsize[0])
            for i, mag in enumerate(form):
                x = start[0] + i
                y2 = midy - bsize[1]*mag
                y = midy + bsize[1]*mag
                pygame.draw.line(self.screen, (0,0,255), (x,y), (x,y2))
            

        pygame.display.update()
        


