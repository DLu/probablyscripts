from PyPDF2 import PdfFileReader
from PythonMagick import Image  # python3-pythonmagick
import subprocess
import tempfile
from tqdm import tqdm


class Page:
    def __init__(self, filename, density):
        self.base_filename = filename

        self.image = Image()
        self.image.density('%d' % density)
        self.image.read(self.base_filename)
        self.density = density

        self.w = self.image.size().width()
        self.h = self.image.size().height()

        self.calculate_addition_matrix()

    def get_intensity(self, x, y, dn=pow(2, 16) - 1):
        return self.image.pixelColor(x, y).intensity() / dn

    def subimage_to_file(self, x, y, w, h, new_density=300):
        subimage = tempfile.NamedTemporaryFile(suffix='.png')

        if '.png' in self.base_filename:
            factor = 1.0
            density = []
        else:
            factor = float(new_density) / self.density
            density = ['-density', str(new_density)]

        x = int(x * factor)
        y = int(y * factor)
        w = int(w * factor)
        h = int(h * factor)
        subprocess.call(['convert'] +
                        density +
                        [self.base_filename, '-crop', '%dx%d%+d%+d' %
                        (w, h, x, y), '-trim', '+repage', '-trim', subimage.name])
        return subimage

    def calculate_addition_matrix(self):
        self.matrix = []
        for x in tqdm(range(self.w)):
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
    def __init__(self, filename, pages=None, density=72):
        self.original = filename

        if filename.suffix == '.pdf':
            self.read(filename, pages, density)
        else:
            self.read_image(filename, density)

    def read(self, filename, pages, density):
        input1 = PdfFileReader(str(filename))
        self.info = input1.getDocumentInfo()
        n = input1.getNumPages()
        self.pages = []
        if pages is None:
            self.mypages = range(n)
        else:
            self.mypages = pages

        bar = tqdm(self.mypages)
        for i in bar:
            bar.set_description('Reading page %d of %d' % (i + 1, n))
            self.pages.append(Page('%s[%d]' % (filename, i), density))

    def read_image(self, filename, density):
        self.info = {}
        self.pages = []
        self.mypages = [0]
        self.pages.append(Page(filename, density))
