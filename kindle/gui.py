import pygame
from pygame.locals import *
import time
import collections

W = 850
H = 1100
ModeDef = collections.namedtuple('ModeDef', ['doc', 'mode'], verbose=False)

KEYMAP = {
	K_1: ModeDef("Delete white mode", 1),
	K_2: ModeDef("Reposition splits mode", 2),
	K_3: ModeDef("Kill row mode", 3),
	K_4: ModeDef("Insert column mode", 4),
	K_5: ModeDef("Insert row mode", 5),
	K_6: ModeDef("Set left mode", 6),
	K_0: ModeDef("Standard mode", 0),
}

class Viewer:
    def __init__(self, splitter):
        self.splitter = splitter
        pygame.init()
        self.screen = pygame.display.set_mode((W,H))
        self.page_no = 0
        self.mode = 0
        self.reload_page()

    def reload_page(self):
        pygame.draw.rect(self.screen, (255,255,255), (0,0,W,H), 0)
        page = self.splitter.pages[self.page_no]
        image = page.page.pimage
        scaled = pygame.transform.scale(image, (W, H))
        self.screen.blit(scaled, (0,0))
        for section in page.get_sections():
            pygame.draw.rect(self.screen, (255,0,0), self.resize(page.size(), section), 1)
        pygame.display.flip()

    def resize(self, size, (x,y,w,h)):
        x,y = self.to_viewer(size, x, y)
        w,h = self.to_viewer(size, w,h)
        return (x,y,w,h)

    def to_viewer(self, (w, h), x, y):
        return x * W / w, y * H / h

    def update_mode(self, key):
        self.mode = KEYMAP[key].mode
        print KEYMAP[key].doc, "enabled"

    def print_doc(self):
        for doc, mode in KEYMAP.values():
            print "[%s]: %s" % (mode, doc)

    def spin(self):
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT: return
                if event.type == KEYDOWN:
                    if event.key == K_LEFT and self.page_no > 0:
                        self.page_no -= 1
                        self.reload_page()
                    elif event.key == K_RIGHT and self.page_no + 1 < len(self.splitter.pages):
                        self.page_no += 1
                        self.reload_page()
                    elif event.key in KEYMAP:
                        self.update_mode(event.key)
                    elif event.key == K_r:
                        print "RESET PAGE"
                        self.splitter.pages[ self.page_no ].reset()
                        self.reload_page()

                if event.type == MOUSEBUTTONDOWN:  
                    (x,y) = event.pos
                    page = self.splitter.pages[ self.page_no ]
                    (w,h) = page.size()
                    x = x * w / W
                    y = y * h / H
                    if event.button == 1:
                        if self.mode == 1:
                            page.delete_white_row(y)
                        elif self.mode == 2:
                            page.insert_break_point(x,y)
                        elif self.mode == 3:
                            page.kill_row(y)
                        elif self.mode == 4:
                            page.insert_column_break(x,y)
                        elif self.mode == 5:
                            page.insert_white_row(y)
                        elif self.mode == 6:
                            page.set_left(x)
                    self.reload_page()
            time.sleep(.1)