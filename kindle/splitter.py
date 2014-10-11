from kindle.document import *
import collections

JUMP = 2
WHITE_LIMIT = 8
SPLIT_BY_ASPECT = True
RATIO = 0.75


class SplitPage:

    def __init__(self, page, manual=False):
        self.page = page
        self.manual = manual
        self.reset()

    def reset(self):
        self.left = 0
        self.data = {}
        self.break_points = collections.defaultdict(list)
        if not self.manual:
            self.analyze_rows()

    def size(self):
        return self.page.w, self.page.h

    def is_row_white(self, y, start=None, end=None):
        if start is None:
            start = self.left
        if end is None:
            end = self.page.w
        intensity = self.page.get_average_intensity(start, y, end - 1, y)

        return (1-intensity) < .01

    def get_row_pattern(self, white_limit=WHITE_LIMIT, vjump=JUMP):
        mode = None
        streak = 0
        start = 0
        sections = []

        for y in range(0, self.page.h, vjump):
            white = self.is_row_white(y)

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
                        sections.append((start, -mode + vjump * 2))
                        mode = 0
                else:
                    streak = (-mode) + streak + vjump * 2
                    mode = 1

            # print y, mode, streak, white
        if mode != 0:
            sections.append((start, y - start))
        return sections

    def has_columns(self, start, height, centersize=10, jump=5):
        w = self.page.w - self.left
        mid = w / 2
        # TODO Remove summing here
        for y in range(start, start + height, jump):
            for x in range(
                    self.left + mid - centersize / 2, self.left + mid + centersize / 2 + 1, jump):
                if abs(self.page.get_intensity(x, y) - 1.0) > .001:
                    return False
        return True

    def get_sections(self):
        sections = []
        for (start, height), J in sorted(self.data.iteritems()):
            for (left, width), chunks in sorted(J.iteritems()):
                for (top, short_height) in chunks:
                    sections.append((left, top, width, short_height))
        return sections

    def analyze_rows(self):
        for (start, height) in self.get_row_pattern():
            self.analyze_row(start, height)

    def add_region(self, (x0,y0), (x1,y1)):
        M = {(x0, x1 - x0): [(y0, y1 - y0)]}
        self.data[(y0, y1 - y0)] = M

    def delete_white_row(self, y):
        rows = []
        found = False
        for (start, height) in sorted(self.data.keys()):
            if y < start and not found:
                found = True
                if len(rows) == 0:
                    continue
                (ls, lh) = rows[-1]
                rows = rows[:-1]
                nb = start + height
                rows.append((ls, nb - ls))
            else:
                rows.append((start, height))
        self.data = {}
        for (start, height) in rows:
            self.analyze_row(start, height)

    def insert_white_row(self, y):
        rows = []
        for (start, height) in sorted(self.data.keys()):
            if y >= start and y <= start + height:
                rows.append((start, y - start))
                rows.append((y, start + height - y))
            else:
                rows.append((start, height))
        self.data = {}
        for (start, height) in rows:
            self.analyze_row(start, height)

    def kill_row(self, y):
        rows = []
        for (start, height) in sorted(self.data.keys()):
            if y >= start and y < start + height:
                continue
            else:
                rows.append((start, height))
        self.data = {}
        for (start, height) in rows:
            self.analyze_row(start, height)

    def analyze_row(self, start, height, mincol=15):
        cols = self.page.w - self.left
        xstart = -1
        col_list = []
        for x in range(self.left, self.page.w, mincol):
            r = min(self.page.w - 1, x + mincol - 1)
            i = self.page.get_average_intensity(x, start, r, start + height)
            if i > 0.0:
                if xstart < 0:
                    xstart = x
            elif xstart >= 0:
                col_list.append((xstart, x - xstart))
                xstart = -1

        J = {}
        for col in col_list:
            J[col] = self.get_chunks(col[0], start, col[1], height)
        self.data[(start, height)] = J

    def should_split(self, w, h):
        ratio = w / float(h)
        return ratio < RATIO

    def get_chunks(self, x, y, w, h):
        if not SPLIT_BY_ASPECT or not self.should_split(w, h):
            return [(y, h)]

        center_height = y + h / 2
        chosen_split_y = None

        for delta_y in range(h / 4):
            for sign in [1, -1]:
                split_y = center_height + sign * delta_y
                is_white = self.is_row_white(split_y, start=x, end=x + w)
                if is_white:
                    chosen_split_y = split_y
                    break

            if chosen_split_y is not None:
                break

        if chosen_split_y is None:
            return [(y, h)]

        first_h = chosen_split_y - y
        return self.get_chunks(x, y, w, first_h) + self.get_chunks(x, chosen_split_y, w, h - first_h)

    def insert_break_point(self, cx, cy):
        for y, h in self.data:
            if cy >= y and cy < y + h:
                for x, w in self.data[(y, h)]:
                    if cx >= x and cx < x + w:
                        break_points = self.break_points[(x, y, w, h)]
                        break_points.append(cy)
                        start_y = y
                        chunks = []
                        for by in sorted(break_points):
                            chunks += self.get_chunks(x,
                                                      start_y,
                                                      w,
                                                      by - start_y)
                            start_y = by
                        chunks += self.get_chunks(x,
                                                  start_y,
                                                  w,
                                                  y + h - start_y)
                        self.data[(y, h)][(x, w)] = chunks

    def insert_column_break(self, cx, cy):
        for y, h in self.data:
            if cy >= y and cy < y + h:
                cols = []
                for x, w in self.data[(y, h)]:
                    if cx >= x and cx < x + w:
                        cols.append((x, cx - x))
                        cols.append((cx, x + w - cx))
                    else:
                        cols.append((x, w))
                J = {}
                for col in cols:
                    J[col] = self.get_chunks(col[0], y, col[1], h)
                self.data[(y, h)] = J

    def set_left(self, x):
        self.data = {}
        self.left = x
        self.analyze_rows()


class Splitter:

    def __init__(self, document, manual=False):
        self.document = document
        self.pages = []
        for page in self.document.pages:
            sp = SplitPage(page, manual)
            self.pages.append(sp)

    def save(self, outfile):
        temps = []
        for (i, page) in enumerate(self.pages):
            for j, section in enumerate(page.get_sections()):
                sys.stdout.write("\rWriting Image for page %d/%d, section %d/%d     " %
                                 (i + 1, len(self.pages), j + 1, len(page.get_sections())))
                sys.stdout.flush()
                (x, y, w, h) = section
                sectionfile = page.page.subimage_to_file(x, y, w, h)
                temps.append(sectionfile)

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
            NameObject('/Title'): createStringObject(self.document.info.get('title', "david")),
            NameObject('/Author'): createStringObject(self.document.info.get('author', ""))
        })

        input1 = PdfFileReader(file(midfile, "rb"))
        for pn in range(input1.getNumPages()):
            output.addPage(input1.getPage(pn))
        outputStream = file(outfile, "wb")
        output.write(outputStream)
        outputStream.close()
        execute(['rm', midfile])
