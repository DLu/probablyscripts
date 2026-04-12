import click
from pdfminer.pdfparser import PDFParser
from pdfminer.pdfdocument import PDFDocument
from pdfminer.pdfpage import PDFPage, PDFTextExtractionNotAllowed
from pdfminer.pdfinterp import PDFResourceManager
from pdfminer.pdfinterp import PDFPageInterpreter
from pdfminer.layout import LAParams, LTTextBoxHorizontal, LTFigure, LTChar
from pdfminer.converter import PDFPageAggregator


def get_chars(obj):
    if isinstance(obj, LTChar):
        yield obj
        return

    for sub_obj in obj:
        if isinstance(sub_obj, LTChar):
            yield sub_obj
        elif isinstance(sub_obj, LTFigure):
            yield from get_chars(sub_obj)


def get_texts(obj, laparams, recursive=False):
    for piece in obj:
        if isinstance(piece, LTTextBoxHorizontal):
            yield piece
        elif recursive and isinstance(piece, LTFigure):
            chars = list(get_chars(piece))

            yield from piece.group_objects(laparams, chars)


class MyPDFPage:
    def __init__(self, texts):
        self.texts = texts
        self.pairs = None

    def get_pairs(self):
        if not self.pairs:
            self.pairs = []
            for piece in self.texts:
                s = piece.get_text().strip()
                self.pairs.append((piece, s))
        return self.pairs

    def _get_one(self, method, parameter):
        hits = method(parameter)
        if len(hits) == 1:
            return hits[0]
        elif len(hits) == 0:
            return None
        else:
            click.secho(f'ERROR Multiple hits for "{parameter}", using first.', fg='yellow')
            return hits[0]

    def find(self, text):
        return self._get_one(self.find_all, text)

    def find_all(self, text):
        hits = []
        for el, s in self.get_pairs():
            if s == text:
                hits.append(el)
        return hits

    def find_with_pattern(self, pattern):
        return self._get_one(self.find_all_with_pattern, pattern)

    def find_all_with_pattern(self, pattern):
        hits = []
        for el, s in self.get_pairs():
            m = pattern.search(s)
            if m:
                hits.append((el, m))
        return hits

    def get_things_below(self, heading, tolerance=1e-2):
        things = []
        for piece in self.texts:
            if abs(piece.x0 - heading.x0) < tolerance and piece.y0 < heading.y0:
                things.append(piece)
        return things

    def get_things_right(self, box):
        things = []
        for piece in self.texts:
            if piece == box:
                continue
            if (piece.y0 <= box.y0 and box.y0 <= piece.y1) or (piece.y0 <= box.y1 and box.y1 <= piece.y1):
                if piece.x1 > box.x0:
                    things.append(piece)
        return sorted(things, key=lambda piece: piece.x0)


def get_pages(filename, line_margin=0.1, recursive=False):
    pages = []
    with open(filename, 'rb') as fp:
        parser = PDFParser(fp)
        document = PDFDocument(parser)

        if not document.is_extractable:
            raise PDFTextExtractionNotAllowed
        rsrcmgr = PDFResourceManager()

        # Set parameters for analysis.
        laparams = LAParams()
        laparams.line_margin = line_margin

        # Create a PDF page aggregator object.
        device = PDFPageAggregator(rsrcmgr, laparams=laparams)
        interpreter = PDFPageInterpreter(rsrcmgr, device)

        for page in PDFPage.create_pages(document):
            interpreter.process_page(page)
            # receive the LTPage object for the page.
            layout = device.get_result()

            my_page = MyPDFPage(list(get_texts(layout, laparams, recursive)))
            pages.append(my_page)

        return pages
