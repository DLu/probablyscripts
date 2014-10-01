from pyPdf import PdfFileWriter, PdfFileReader  # python-pypdf
from pyPdf.generic import NameObject, createStringObject
from PythonMagick import *  # python-pythonmagick
from kindle import execute
import pygame
import tempfile
import sys

RES1 = 72
RES2 = 300


class Page:

    def __init__(self, filename, density):

        self.base_filename = filename

        self.image = Image()
        self.image.density('%d' % density)
        self.image.read(self.base_filename)
        self.density = density

        self.w = self.image.size().width()
        self.h = self.image.size().height()

        temp = tempfile.NamedTemporaryFile(suffix='.png')
        self.image.write(temp.name)
        self.pimage = pygame.image.load(temp.name)
        temp.close()

        self.calculate_addition_matrix()

    def get_intensity(self, x, y, dn=pow(2, 16) - 1):
        return self.image.pixelColor(x, y).intensity() / dn

    def subimage_to_file(self, x, y, w, h, new_density=RES2):
        subimage = tempfile.NamedTemporaryFile(suffix='.png')

        if '.png' in self.base_filename:
            factor = 1.0
            density = []
        else:
            factor = float(new_density) / self.density
            density = ["-density", str(new_density)]

        x = int(x * factor)
        y = int(y * factor)
        w = int(w * factor)
        h = int(h * factor)
        execute(["convert"] +
                density +
                [self.base_filename, "-crop", '%dx%d%+d%+d' %
                 (w, h, x, y), '-trim', '+repage', '-trim', subimage.name])
        return subimage

    def calculate_addition_matrix(self):
        self.matrix = []
        for x in range(self.w):
            col = []
            for y in range(self.h):
                if x > 0:
                    if y > 0:
                        a = self.matrix[x - 1][y - 1]
                    else:
                        a = 0
                    b = self.matrix[x - 1][y]
                else:
                    a = 0
                    b = 0

                if y > 0:
                    c = col[-1]
                else:
                    c = 0

                d = round(1 - self.get_intensity(x, y), 2)

                value = b + c - a + d
                col.append(value)

            self.matrix.append(col)

    def quick_sum(self, x0, y0, x1, y1):
        A = self.matrix[x0 - 1][y1] if x0 > 0 else 0
        B = self.matrix[x1][y1]
        C = self.matrix[x1][y0 - 1] if y0 > 0 else 0
        D = self.matrix[x0 - 1][y0 - 1] if y0 > 0 and x0 > 0 else 0
        return D + B - A - C

    def get_average_intensity(self, x0, y0, x1, y1):
        w = x1 - x0 + 1
        h = y1 - y0 + 1
        total = self.quick_sum(x0, y0, x1, y1)
        return round(total / (w * h), 2)


class Document:

    def __init__(self, filename, pages=None, density=RES1):
        self.original = filename

        if 'pdf' in filename:
            self.read(filename, pages, density)
        else:
            self.read_image(filename, density)

    def read(self, filename, pages, density):
        input1 = PdfFileReader(file(filename))
        self.info = input1.getDocumentInfo()
        n = input1.getNumPages()
        self.pages = []
        if pages is None:
            self.mypages = range(n)
        else:
            self.mypages = pages
        for i in self.mypages:
            sys.stdout.write("\rReading page %d of %d" % (i + 1, n))
            sys.stdout.flush()
            self.pages.append(Page('%s[%d]' % (filename, i), density))
        sys.stdout.write("\n")
        sys.stdout.flush()

    def read_image(self, filename, density):
        self.info = {}
        self.pages = []
        self.mypages = [0]
        self.pages.append(Page(filename, density))
