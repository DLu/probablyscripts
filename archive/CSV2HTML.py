#!/usr/bin/python
import collections


def get_color(r, g, b):
    p = '%02x'
    return '#' + p % r + p % g + p % b


def scale(pct):
    bottom = [0xff, 0xff, 0xff]
    top = [0x33, 0x33, 0xff]

    a = []
    for t, b in zip(top, bottom):
        s = t - b
        a.append(s * pct + b)

    return get_color(a[0], a[1], a[2])


def to_row(row, hdata, tag='td'):
    s = '<tr>'
    for x in row:
        s += '<%s>%s' % (tag, str(x))
    return s + '</tr>\n'


def to_data_row(headers, row, hdata):
    s = '<tr>'
    for h in headers:
        x = row[h]
        if hdata[h]['max'] == hdata[h]['min']:
            v = 0.0
        else:
            v = (float(x) - hdata[h]['min'])/(hdata[h]['max'] - hdata[h]['min'])
        if hdata[h].get('reverse', False):
            v = 1 - v
        color = ' style="background-color:%s;"' % scale(v)
        s += '<td%s>%s' % (color, str(x))
    return s + '</tr>\n'


def to_html(headers, data, hdata):
    s = '<table class="sortable">' + to_row([hdata[h].get('preferred', h) for h in headers], 'th')
    for row in data:
        s += to_data_row(headers, row, hdata)
    return s + '</table>'

import fileinput
import csv
print '<head><script src="/home/dlu/sorttable.js"></script>'
print '<style>table { border-collapse:collapse; } table, th, td { border: 1px solid black; text-align: center} </style></head>'
reader = csv.reader(fileinput.input(), delimiter='\t')
headers = None
hdata = collections.defaultdict(dict)
data = []

for row in reader:
    if headers is None:
        headers = row
        for h in headers:
            hdata[h]['min'] = 1e10
            hdata[h]['max'] = -1e10
            if 'knockout' in h:
                hdata[h]['preferred'] = h[9:]
            if h == 'completed':
                hdata[h]['reverse'] = True
    else:
        arr = [eval(a) for a in row]
        m = {}
        for h, a in zip(headers, arr):
            hdata[h]['min'] = min(hdata[h]['min'], a)
            hdata[h]['max'] = max(hdata[h]['max'], a)
            m[h] = a
        data.append(m)

import sys
if 'knockout_occ' in headers:
    headers = ['knockout_occ',
               'knockout_goal',
               'knockout_path',
               'knockout_gor',
               'knockout_por'] + headers[5:]

print to_html(headers, data, hdata)
