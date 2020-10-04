import click
from pdfminer.pdfparser import PDFParser
from pdfminer.pdfdocument import PDFDocument
from pdfminer.pdfpage import PDFPage, PDFTextExtractionNotAllowed
from pdfminer.pdfinterp import PDFResourceManager
from pdfminer.pdfinterp import PDFPageInterpreter
from pdfminer.layout import LAParams, LTTextBoxHorizontal
from pdfminer.converter import PDFPageAggregator


class MyPDFPage:
    def __init__(self, layout):
        self.texts = []
        for piece in layout:
            if isinstance(piece, LTTextBoxHorizontal):
                self.texts.append(piece)

    def find(self, text):
        hits = self.find_all(text)
        if len(hits) == 1:
            return hits[0]
        elif len(hits) == 0:
            return None
        else:
            click.secho(f'ERROR Multiple hits for "{text}", using first.', fg='yellow')
            return hits[0]

    def find_all(self, text):
        hits = []
        for piece in self.texts:
            if piece.get_text().strip() == text:
                hits.append(piece)
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


def get_pages(filename, line_margin=0.1):
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

            my_page = MyPDFPage(layout)
            pages.append(my_page)

        return pages
