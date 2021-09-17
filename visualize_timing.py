#!/usr/bin/python
import yaml
import sys
import re
import argparse
import matplotlib.pyplot as plt

DECIMAL_PATTERN = re.compile(r'(\s\d+)e')

S = """
-Outline:
|   -computeVelocityCommandsOrca:  total: 1.24717,  self: 0.00979495,  children: 1.23738,  iterations: 495,  min: 0.001665,  max: 0.005756
|   |   -prepare:  total: 0.925796,  self: 0.108895,  children: 0.816901,  iterations: 495,  min: 0.001279,  max: 0.004071
|   |   |   -RotatePrepare:  total: 3.8e-05,  self: 3.8e-05,  children: 0,  iterations: 495,  min: 0,  max: 4e-06
|   |   |   -CombinedPrepare:  total: 0.816863,  self: 0.816863,  children: 0,  iterations: 495,  min: 0.001217,  max: 0.003354
|   |   -coreScore:  total: 0.18762,  self: 0.18762,  children: 0,  iterations: 495,  min: 0.000152,  max: 0.001568
|   |   -orca:  total: 0.122163,  self: 0.122163,  children: 0,  iterations: 495,  min: 3.4e-05,  max: 0.001026
|   |   -end:  total: 0.001796,  self: 0.001796,  children: 0,  iterations: 495,  min: 1e-06,  max: 0.00015
"""


def draw_bars(ax, data, full_sum=None):
    bars = []
    running = 0.0
    for total in [d['total'] for key, d in data]:
        ta = [total]
        bars.append(plt.bar([0], ta, bottom=[running]))
        running += total
    if full_sum is not None:
        remaining = [full_sum - running]
        bars.append(plt.bar([0], remaining, bottom=[running]))
        ax.legend(bars, [key for key, d in data] + ['other'])
    else:
        ax.legend(bars, [key for key, d in data])


def create_figures(fig, data, n_plots, index=1, title=None, full_sum=None):
    plots_drawn = 1
    ax = fig.add_subplot(1, n_plots, index)
    if title is None:
        ax.set_title('Total')
    else:
        ax.set_title(title)
    draw_bars(ax, data, full_sum=full_sum)

    for key, d in data:
        if d['children'] == 0:
            continue
        plots_drawn += create_figures(fig, d['children'], n_plots, index + plots_drawn, key, full_sum=d['total'])
    return plots_drawn


levels = [[]]
timing = levels[0]
plots = 1

parser = argparse.ArgumentParser()
parser.add_argument('-d', '--debug', action='store_true')
args = parser.parse_args()

if args.debug:
    src = S.split('\n')
else:
    src = sys.stdin

for line in src:
    print(line[:-1])
    indent = len([c for c in line if c == '|'])
    if indent == 0:
        continue
    core = line[line.index('-') + 1:]
    name, _, rest = core.partition(':')
    m = DECIMAL_PATTERN.search(rest)
    while m:
        rest = rest.replace(m.group(0), m.group(1) + '.0e')
        m = DECIMAL_PATTERN.search(rest)
    D = yaml.load('{' + rest[1:] + '}')
    if D['children'] > 0:
        while len(levels) <= indent:
            levels.append([])
        D['children'] = []
        levels[indent] = D['children']
        plots += 1
    levels[indent - 1].append((name, D))

fig = plt.figure()
create_figures(fig, timing, plots)
plt.show()
