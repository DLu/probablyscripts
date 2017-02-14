import os, os.path
import collections
D = collections.defaultdict(int)

for fn in os.listdir('.'):
    if 'bag' not in fn or '2016' in fn:
        continue
    cat, _, topic = fn.partition('_')
    print cat, topic
    D[cat] += os.path.getsize(fn)

for cat in D:
    print cat, D[cat]
