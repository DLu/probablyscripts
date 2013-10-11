from pyPdf import PdfFileWriter, PdfFileReader #python-pypdf
from pyPdf.generic import NameObject, createStringObject
from PythonMagick import * # python-pythonmagick
from kindle import execute
import pygame
import tempfile
import sys

PAGES = None
RES1 = 72
RES2 = 300

class Page:
    def __init__(self, filename, density):

        self.base_filename = filename

        self.image = Image()
        self.image.density('%d'%density)
        self.image.read(self.base_filename)
        self.density = density

        self.w = self.image.size().width()
        self.h = self.image.size().height()

        temp = tempfile.NamedTemporaryFile(suffix='.png')
        self.image.write(temp.name)
        self.pimage = pygame.image.load(temp.name)
        temp.close()

    def subimage_to_file(self, x, y, w, h, new_density=RES2):
        subimage = tempfile.NamedTemporaryFile(suffix='.png')
        factor = float(new_density) / self.density
        x = int(x*factor)
        y = int(y*factor)
        w = int(w*factor)
        h = int(h*factor)
        execute(["convert", "-density", str(new_density), self.base_filename, "-crop", '%dx%d%+d%+d'%(w,h,x,y), '-trim', '+repage', '-trim', subimage.name])
        return subimage

class Document:
    def __init__(self, filename, density=RES1):
        self.original = filename
        self.read(filename, density)

    def read(self, filename, density):
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
            self.pages.append(Page('%s[%d]'%(filename, i), density))
        sys.stdout.write("\n")
        sys.stdout.flush()

