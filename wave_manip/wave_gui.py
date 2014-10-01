import pygame
import sys
from pygame.locals import *
import audio_player

MSTART = (50, 50)
MHEIGHT = 200


class WaveGUI:

    def __init__(self, clip):
        pygame.init()
        self.screen = pygame.display.set_mode((640, 480))
        self.quit = False
        self.clip = clip

        self.m_width = self.screen.get_width() - MSTART[0] * 2
        self.chunk, self.sampled = self.clip.partition(self.m_width)

        self.player = audio_player.AudioPlayer(clip)

    def ok(self):
        return not self.quit

    def update(self):
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                self.quit = True
                return

            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_p:
                    self.player.start(self.clip.get_clip(0, 5))

        size = self.screen.get_size()
        pygame.draw.rect(self.screen, (255, 255, 255), Rect((0, 0), size))

        if self.player.inc is not None:
            x = self.player.inc / self.chunk
        else:
            x = None

        self.draw_wave(MSTART, (self.m_width, MHEIGHT), self.sampled, x)

        pygame.display.update()

    def draw_wave(self, start, size, data, t=None):
        midy = start[1] + size[1] / 2
        pygame.draw.rect(self.screen, (0, 0, 0), Rect(start, size), 1)
        for i, mag in enumerate(data):
            x = start[0] + i
            y2 = midy - size[1] * mag
            y = midy + size[1] * mag
            pygame.draw.line(self.screen, (0, 0, 255), (x, y), (x, y2))

        if t is not None and t < size[0]:
            x = t + start[0]
            pygame.draw.line(
                self.screen, (255, 0, 0), (x, start[1]), (x, start[1] + size[1]))
