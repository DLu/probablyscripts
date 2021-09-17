import pygame
import pygame.locals as keys
import time
import tempfile
import collections

W = 850
H = 1100
ModeDef = collections.namedtuple('ModeDef', ['doc', 'mode'], verbose=False)

KEYMAP = {
    keys.K_1: ModeDef('Delete white mode', 1),
    keys.K_2: ModeDef('Reposition splits mode', 2),
    keys.K_3: ModeDef('Kill row mode', 3),
    keys.K_4: ModeDef('Insert column mode', 4),
    keys.K_5: ModeDef('Insert row mode', 5),
    keys.K_6: ModeDef('Set left mode', 6),
    keys.K_7: ModeDef('Manual', 7),
    keys.K_0: ModeDef('Standard mode', 0),
}


class Viewer:

    def __init__(self, splitter):
        self.splitter = splitter
        pygame.init()
        self.screen = pygame.display.set_mode((W, H))
        self.page_no = 0
        self.mode = 0
        self.save_coords = None
        self.saved_images = {}
        self.reload_page()

    def get_current_page(self):
        return self.splitter.pages[self.page_no]

    def reload_page(self):
        pygame.draw.rect(self.screen, (255, 255, 255), (0, 0, W, H), 0)
        page = self.get_current_page()
        if self.page_no not in self.saved_images:
            try:
                temp = tempfile.NamedTemporaryFile(suffix='.png')
                page.page.image.write(temp.name)
                self.saved_images[self.page_no] = pygame.image.load(temp.name)
                temp.close()
            except Exception:
                temp = tempfile.NamedTemporaryFile(suffix='.jpg')
                page.page.image.write(temp.name)
                self.saved_images[self.page_no] = pygame.image.load(temp.name)
                temp.close()

        image = self.saved_images[self.page_no]
        scaled = pygame.transform.scale(image, (W, H))
        self.screen.blit(scaled, (0, 0))
        for section in page.get_sections():
            pygame.draw.rect(
                self.screen, (255, 0, 0), self.resize(
                    page.size(), section), 1)
        pygame.display.flip()

    def resize(self, size, dims):
        x, y, w, h = dims
        x, y = self.to_viewer(size, x, y)
        w, h = self.to_viewer(size, w, h)
        return (x, y, w, h)

    def to_viewer(self, dims, x, y):
        w, h = dims
        return x * W / w, y * H / h

    def update_mode(self, key):
        self.mode = KEYMAP[key].mode
        print(KEYMAP[key].doc, 'enabled')

    def print_doc(self):
        for doc, mode in KEYMAP.values():
            print('[%s]: %s' % (mode, doc))

    def spin(self):
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return
                if event.type == keys.KEYDOWN:
                    if event.key == keys.K_LEFT and self.page_no > 0:
                        self.page_no -= 1
                        self.reload_page()
                    elif event.key == keys.K_RIGHT and self.page_no + 1 < len(self.splitter.pages):
                        self.page_no += 1
                        self.reload_page()
                    elif event.key in KEYMAP:
                        self.update_mode(event.key)
                    elif event.key == keys.K_r:
                        print('RESET PAGE')
                        self.get_current_page().reset()
                        self.reload_page()

                if event.type == keys.MOUSEBUTTONDOWN:
                    (x, y) = event.pos
                    page = self.get_current_page()
                    (w, h) = page.size()
                    x = x * w // W
                    y = y * h // H
                    if event.button == 1:
                        if self.mode == 1:
                            page.delete_white_row(y)
                        elif self.mode == 2:
                            page.insert_break_point(x, y)
                        elif self.mode == 3:
                            page.kill_row(y)
                        elif self.mode == 4:
                            page.insert_column_break(x, y)
                        elif self.mode == 5:
                            page.insert_white_row(y)
                        elif self.mode == 6:
                            page.set_left(x)
                        elif self.mode == 7:
                            self.save_coords = (x, y)
                    self.reload_page()
                elif event.type == keys.MOUSEBUTTONUP:
                    (x, y) = event.pos
                    page = self.get_current_page()
                    (w, h) = page.size()
                    x = x * w / W
                    y = y * h / H
                    if event.button == 1 and self.mode == 7:
                        if self.save_coords is not None:
                            page.add_region(self.save_coords, (x, y))
                            self.save_coords = None
                        self.reload_page()
            time.sleep(.1)
