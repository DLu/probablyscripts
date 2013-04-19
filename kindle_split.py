#!/usr/bin/python
import warnings
warnings.simplefilter("ignore", DeprecationWarning)

from pyPdf import PdfFileWriter, PdfFileReader #python-pypdf
from PythonMagick import * # python-pythonmagick
import sys, os.path
import pygame
from pygame.locals import *
import tempfile
import collections
import subprocess 
import time
from pyPdf import PdfFileWriter, PdfFileReader #python-pypdf
from pyPdf.generic import NameObject, createStringObject
PAGES =  None
W = 850
H = 1100
WHITE_LIMIT = 10
JUMP=2
SPLIT_BY_ASPECT = True
GUI = True

def execute(command):
    subprocess.Popen(command, \
      stderr=subprocess.STDOUT, stdout=subprocess.PIPE).communicate()[0]

class Page:
    def __init__(self, image):
        self.image = image
        self.w = self.image.size().width()
        self.h = self.image.size().height()
        self.file = tempfile.NamedTemporaryFile(suffix='.png')
        self.image.write(self.file.name)
        self.pimage = pygame.image.load(self.file.name)
        self.reset()

    def reset(self):
        self.left = 0
        self.data = {}
        self.break_points = collections.defaultdict(list)
        self.analyze_rows()
    
    def size(self):
        return self.w, self.h

    def getPct(self, x, y, dn = pow(2,16)-1):
        return self.image.pixelColor(x,y).intensity()/dn

    def is_row_white(self, y, hjump=JUMP, start=None, end=None):
        if start is None:
            start = self.left
        if end is None:
            end = self.image.columns()
        for x in range(start, end, hjump):
            p = self.getPct(x,y)
            if abs(p - 1.0) > 1e-10:
                return False
        return True

    def get_row_pattern(self, white_limit=WHITE_LIMIT, hjump=20, vjump=JUMP):
        mode = None
        streak = 0
        start = 0
        sections = []

        for y in range(0, self.image.rows(), vjump):
            white = self.is_row_white(y, hjump)

            if mode is None:
                if white:
                    mode = 0
                else:
                    mode = 1
                streak = 1
            elif mode == 0:
                if white:
                    streak += vjump
                else:
                    mode = 1
                    streak = vjump
                    start = y - vjump
            elif mode > 0:
                if white:
                    mode = -streak
                    streak = 0
                else:
                    streak += vjump
            else:
                if white:
                    streak += vjump
                    if streak > white_limit:
                        sections.append((start, -mode+vjump*2))
                        mode = 0
                else:
                    streak = (-mode) + streak + vjump * 2
                    mode = 1

            #print y, mode, streak, white
        if mode!=0:
            sections.append((start, y- start))
        return sections

    def has_columns(self, start, height, centersize = 10, jump=5):
        w = self.image.columns() - self.left
        mid = w/2
        for y in range(start, start+height, jump):
            for x in range(self.left + mid-centersize/2, self.left + mid+centersize/2+1, jump):
                if self.getPct(x, y) != 1:
                    return False
        return True

    def get_sections(self):
        sections = []
        for (start, height), J in sorted(self.data.iteritems()):
            for (left, width), chunks in sorted(J.iteritems()):
                for (top, short_height) in chunks:
                    sections.append( (left, top, width, short_height) )
        return sections

    def analyze_rows(self):
        for (start, height) in self.get_row_pattern():
            self.analyze_row(start, height)

    def delete_white_row(self, y):
        rows = []
        found = False
        for (start, height) in sorted(self.data.keys()):
            if y < start and not found:
                found = True
                if len(rows)==0:
                    continue
                (ls, lh) = rows[-1]
                rows = rows[:-1]
                nb = start + height
                rows.append( (ls, nb - ls))
            else:
                rows.append( (start, height) ) 
        self.data = {}
        for (start, height) in rows:
            self.analyze_row(start, height)

    def insert_white_row(self, y):
        rows = []
        for (start, height) in sorted(self.data.keys()):
            if y >= start and y <= start + height:
                rows.append( (start, y - start) )
                rows.append( (y, start + height - y) )
            else:
                rows.append( (start, height) ) 
        self.data = {}
        for (start, height) in rows:
            self.analyze_row(start, height)

    def kill_row(self, y):
        rows = []
        for (start, height) in sorted(self.data.keys()):
            if y >= start and y < start + height:
                continue
            else:
                rows.append( (start, height) ) 
        self.data = {}
        for (start, height) in rows:
            self.analyze_row(start, height)

    def analyze_row(self, start, height):
        cols = self.image.columns() - self.left
        if self.has_columns(start, height):
            col_list = [ (self.left, cols/2), (self.left + cols/2, cols/2) ]
        else:
            col_list = [ (self.left, cols) ]

        J = {}
        for col in col_list:
            J[ col ] = self.get_chunks(col[0], start, col[1], height)
        self.data[ (start, height) ] = J

    def should_split(self, w, h):
        ratio = w/float(h)
        return ratio < .75

    def get_chunks(self, x, y, w, h):
        if not SPLIT_BY_ASPECT or not self.should_split(w,h):
            return [(y,h)]

        center_height = y+h/2
        chosen_split_y = None

        for delta_y in range(h/4):
            for sign in [1, -1]:
                split_y = center_height + sign * delta_y
                is_white = self.is_row_white(split_y, start=x, end=x+w)
                if is_white:
                    chosen_split_y = split_y
                    break

            if chosen_split_y is not None:
                break

        if chosen_split_y is None:
            return [(y,h)]

        first_h = chosen_split_y - y
        return self.get_chunks(x,y,w,first_h) + self.get_chunks(x, chosen_split_y, w, h - first_h)

    def insert_break_point(self, cx, cy):
        for y, h in self.data:
            if cy >= y and cy < y + h:
                for x,w in self.data[(y,h)]:
                    if cx >= x and cx < x + w:
                        break_points = self.break_points[(x,y,w,h)]
                        break_points.append(cy)
                        start_y = y
                        chunks = []
                        for by in sorted(break_points):
                            chunks += self.get_chunks(x, start_y, w, by - start_y)
                            start_y = by
                        chunks += self.get_chunks(x, start_y, w, y + h - start_y)
                        self.data[ (y,h) ] [ (x,w) ] = chunks

    def insert_column_break(self, cx, cy):
        for y, h in self.data:
            if cy >= y and cy < y + h:
                cols = []
                for x,w in self.data[(y,h)]:
                    if cx >= x and cx < x + w:
                        cols.append( (x, cx-x) )
                        cols.append( (cx, x+w-cx) )
                    else:
                        cols.append( (x, w) )
                J = {}
                for col in cols:
                    J[ col ] = self.get_chunks(col[0], y, col[1], h)
                self.data[ (y, h) ] = J

    def set_left(self, x):
        self.data = {}
        self.left = x
        self.analyze_rows()

    def close(self):
        self.file.close()

class Document:
    def __init__(self, filename):
        self.original = filename
        self.read(filename)

    def read(self, filename, density=72):
        input1 = PdfFileReader(file(filename))
        self.info = input1.getDocumentInfo()
        n = input1.getNumPages()
        self.pages = []
        self.mypages = range(n)
        if PAGES is not None:
            self.mypages = PAGES
        for i in self.mypages:
            sys.stdout.write("\rReading page %d of %d"%(i+1, n))
            sys.stdout.flush()
            im = Image()
            im.density('%d'%density)
            im.read('%s[%d]'%(filename, i))
            self.pages.append(Page(im))
        sys.stdout.write("\n")
        sys.stdout.flush()

    def save(self, filename):
        temps = []
        for (i,page) in zip(self.mypages, self.pages):
            for j, section in enumerate(page.get_sections()):
                sys.stdout.write("\rWriting Image for page %d/%d, section %d/%d     "%(i+1, len(self.pages), j+1, len(page.get_sections())))
                sys.stdout.flush()
                sectionfile = tempfile.NamedTemporaryFile(suffix='.png')
                temps.append(sectionfile)

                (x,y,w,h) = section
                pagefn = "%s[%d]"%(self.original, i)
                density = 300
                x = int(x*density / 72)
                y = int(y*density / 72)
                w = int(w*density / 72)
                h = int(h*density / 72)
                execute(["convert", "-density", str(density), pagefn, "-crop", '%dx%d%+d%+d'%(w,h,x,y), '-trim',  '+repage', '-trim', sectionfile.name])
        sys.stdout.write("\n")
        sys.stdout.flush()

        sections = temps

        midfile = 'x.pdf'
        execute(["convert"] + [f.name for f in sections] + [midfile])
        for f in sections:
            f.close()

        output = PdfFileWriter()
        infoDict = output._info.getObject()

        infoDict.update({
            NameObject('/Title'): createStringObject(self.info.get('title', "david")),
            NameObject('/Author'): createStringObject(self.info.get('author', ""))
        })

        input1 = PdfFileReader(file(midfile, "rb"))
        for pn in range(input1.getNumPages()):
            output.addPage(input1.getPage(pn))
        outputStream = file(outfile, "wb")
        output.write(outputStream)
        outputStream.close()
        execute(['rm', midfile])

    def preprocess(self):
        for page in self.pages:
            page.get_sections()

    def close(self):
        for page in self.pages:
            page.close()

class Viewer:
    def __init__(self, document):
        self.document = document
        pygame.init()
        self.screen = pygame.display.set_mode((W,H))
        self.page_no = 0
        self.mode = 0
        self.reload_page()

    def reload_page(self):
        pygame.draw.rect(self.screen, (255,255,255), (0,0,W,H), 0)
        page = self.document.pages[self.page_no]
        image = page.pimage
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

    def spin(self):
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT: return
                if event.type == KEYDOWN:
                    if event.key == K_LEFT and self.page_no > 0:
                        self.page_no -= 1
                        self.reload_page()
                    elif event.key == K_RIGHT and self.page_no + 1 < len(self.document.pages):
                        self.page_no += 1
                        self.reload_page()
                    elif event.key == K_1:
                        print "Delete white mode enabled"
                        self.mode = 1
                    elif event.key == K_2:
                        print "Reposition splits mode enabled"
                        self.mode = 2
                    elif event.key == K_3:
                        print "Kill Row mode enabled"
                        self.mode = 3
                    elif event.key == K_4:
                        print "Insert column mode enabled"
                        self.mode = 4
                    elif event.key == K_5:
                        print "Insert row mode enabled"
                        self.mode = 5
                    elif event.key == K_6:
                        print "Set left mode enabled"
                        self.mode = 6
                    elif event.key == K_0:
                        print "Standard Mode enabled"
                        self.mode = 0
                    elif event.key == K_r:
                        print "RESET PAGE"
                        self.document.pages[ self.page_no ].reset()
                        self.reload_page()

                if event.type == MOUSEBUTTONDOWN:  
                    (x,y) = event.pos
                    page = self.document.pages[ self.page_no ]
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
        
if __name__ == '__main__':
    if len(sys.argv)==2:
        infile = sys.argv[1]
        outfile = os.path.splitext(infile)[0] + "_.pdf"
    elif len(sys.argv)==3:
        (infile, outfile) = sys.argv[1:3]
    else:
        print "Usage: kindle_split input.pdf [output.pdf]"%sys.argv[0]
        sys.exit(1)

    d = Document(infile)
    d.preprocess()
    if GUI:
        v = Viewer(d)
        v.spin()
    d.save(outfile)
    d.close()
