#!/usr/bin/python
from pyPdf import PdfFileWriter, PdfFileReader #python-pypdf
from PythonMagick import * # python-pythonmagick
import sys, os.path
import pygame
import tempfile
from subprocess import call
from pyPdf import PdfFileWriter, PdfFileReader #python-pypdf
from pyPdf.generic import NameObject, createStringObject
PAGES = None # [5]
W = 850
H = 1100
MIN_SIZE = 50
WHITE_LIMIT = 20
JUMP=7
SPLIT_BY_ASPECT = True
GUI = False

import time
starttime = time.time()
def mark(s):
    print "%s\t%6.2f"%(s, time.time()-starttime)

class Page:
    def __init__(self, image):
        self.image = image
        self.w = self.image.size().width()
        self.h = self.image.size().height()
        self.file = tempfile.NamedTemporaryFile(suffix='.png')
        self.image.write(self.file.name)
        self.pimage = pygame.image.load(self.file.name)
        self.sections = None
    
    def size(self):
        return self.w, self.h

    def getPct(self, x, y, dn = pow(2,16)-1):
        return self.image.pixelColor(x,y).intensity()/dn

    def get_row_pattern(self, white_limit=WHITE_LIMIT, jump=JUMP):
        mode = None
        streak = 0
        start = 0
        sections = []

        for y in range(0, self.image.rows(), jump):
            white = True

            for x in range(0, self.image.columns(), jump):
                p = self.getPct(x, y)
                #if y==0:
                #    print p,
                if p < 1.0:
                    white = False
                    break
            #if y==0:
            #    print

            if mode is None:
                if white:
                    mode = 0
                else:
                    mode = 1
                streak = 1
            elif mode == 0:
                if white:
                    streak += jump
                else:
                    mode = 1
                    streak = jump
                    start = y - jump
            elif mode > 0:
                if white:
                    mode = -streak
                    streak = 0
                else:
                    streak += jump
            else:
                if white:
                    streak += jump
                    if streak > white_limit:
                        sections.append((start, -mode+jump*2))
                        mode = 0
                else:
                    streak = (-mode) + streak + jump * 2
                    mode = 1

            #print y, mode, streak, white
        if mode!=0:
            sections.append((start, y- start))
        return sections

    def has_columns(self, start, height, centersize = 10, jump=5):
        w = self.image.columns()
        mid = w/2
        for y in range(start, start+height, jump):
            for x in range(mid-centersize/2, mid+centersize/2+1, jump):
                if self.getPct(x, y) != 1:
                    return False
        return True

    def get_section(self, x, y, w, h):
        ratio = w/float(h)
        n = 1
        while n * ratio < .75:
            n += 1
        all_sections = []
        if SPLIT_BY_ASPECT and n>1:
            h0 = y+h/2
            split = None
            for hp in range(h/4):
                for m in [1, -1]:
                    split = h0 + m * hp

                    for x0 in range(x, x+w):
                        if self.getPct(x0, split) <= .9:
                            split = None
                            break
                    if split is not None:
                        break
                if split is not None:
                    break
            if split is None:
                all_sections.append((x,y,w,h))
                return
            rel = split - y
            all_sections.append((x,y,w,rel))
            all_sections.append((x,split,w,h-rel))
        else:
            all_sections.append((x,y,w,h))
        return all_sections

    def get_sections(self):
        if self.sections:
            return self.sections
        self.sections = []
        for (start, height) in self.get_row_pattern():
            cols = self.image.columns()
            if self.has_columns(start, height):
                self.sections += self.get_section(0, start, cols/2, height)
                self.sections += self.get_section(cols/2, start, cols/2, height)
            else:
                self.sections += self.get_section(0, start, cols, height)

        return self.sections

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
        mypages = range(n)
        if PAGES is not None:
            mypages = PAGES
        for i in mypages:
            im = Image()
            im.density('%d'%density)
            im.read('%s[%d]'%(filename, i))
            self.pages.append(Page(im))

    def save(self, filename):
        temps = []
        for (i,page) in enumerate(self.pages):
            for section in page.get_sections():
                sectionfile = tempfile.NamedTemporaryFile(suffix='.png')
                temps.append(sectionfile)

                (x,y,w,h) = section
                pagefn = "%s[%d]"%(self.original, i)
                density = 300
                x = int(x*density / 72)
                y = int(y*density / 72)
                w = int(w*density / 72)
                h = int(h*density / 72)
                call(["convert", "-density", str(density), pagefn, "-crop", '%dx%d%+d%+d'%(w,h,x,y), '-trim',  '+repage', '-trim', sectionfile.name])

        sections = []
        for temp in temps:
            image = Image(temp.name)
            if image.size().height()>MIN_SIZE:
                sections.append(temp)
            else:
                temp.close()

        midfile = 'x.pdf'
        call(["convert"] + [f.name for f in sections] + [midfile])
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
        call(['rm', midfile])

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
        self.reload_page()

    def reload_page(self):
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

    mark('Start')
    d = Document(infile)
    mark('Read in')
    d.preprocess()
    mark("Initial Sections Done")
    if GUI:
        v = Viewer(d)
        v.spin()
    mark("Done Editing")
    d.save(outfile)
    mark("Saved")
    d.close()
