#!/usr/bin/python

import sys

BEGIN = "\\begin{figure"
END = '\\end{figure'


def parse(s, verbose=False):
    m = []
    state = 0
    tag = ''
    current = []
    counter = 0
    for c in s:
        if verbose:
            print c, state
        if state == 0:
            if c in '\n \t':
                continue
            elif c == '\\':
                tag = ''
                current = []
                state = 1
            else:
                print 'unknown', c, state
        elif state == 1:
            if c == '{':
                current.append(['{', ''])
                counter = 1
                state = 3
            elif c == '[':
                current.append(['[', ''])
                state = 2
            elif c in '\n \t':
                if tag == 'subfloat':
                    m2 = parse(current[-1][1])
                    current[-1][1] = m2
                m.append((tag, current))
                state = 0
            else:
                tag += c
        elif state == 2:
            if c != ']':
                current[-1][1] += c
            else:
                state = 1
        elif state == 3:
            if c == '\\':
                current[-1][1] += c
                state = 4
            elif c == '{':
                counter += 1
                current[-1][1] += c
            elif c != '}':
                current[-1][1] += c
            else:
                counter -= 1
                if counter == 0:
                    state = 1
                else:
                    current[-1][1] += c
        elif state == 4:
            current[-1][1] += c
            state = 3
    if verbose:
        print state, tag, current
    if state > 0:
        m.append((tag, current))
    return m


def output(m, indent=0):
    s = '\n'
    for name, fields in m:
        s += ' ' * indent
        s += '\\%s' % name
        for b, data in fields:
            s += b
            if b == '{':
                c = '}'
            else:
                c = ']'
            if isinstance(data, str):
                s += data
            else:
                s += output(data, indent + 2)
            s += c
        s += '\n'
    return s


def fix(s):
    m = parse(s)

    subfloats = [b for a, b in m if a == 'subfloat']
    caption = [b for a, b in m if a == 'caption'][0]

    for data in subfloats:
        while len(data) < 3:
            data.insert(0, ['[', ''])
        data[0][0] = '['
        data[1][0] = '['
        if len(data[0][1]) == 0:
            print 'Old caption: ', data[1][1]
            s = raw_input('New caption:')
            data[0][1] = s

    if len(caption) == 1:
        print 'Original Caption: %s' % caption[-1][1]
        s = raw_input('New Caption:')
        if len(s) > 0:
            if s == 'None':
                s = ''
            caption.insert(0, ('[', s))

        # caption[-1][1]='xxx'
    return output(m)

for arg in sys.argv[1:]:
    if arg[0] == '-':
        continue

    s = open(arg, 'r').read()
    i = 0
    while s.find(BEGIN, i) >= 0:
        i = s.find(BEGIN, i)

        ci = s.rfind('\n', 0, i)
        if s[ci + 1] == '%':
            i = i + 1
            continue

        i1 = s.find('}', i)
        if s[i1 + 1] == '[':
            i1 = s.find(']', i1)

        i2 = s.find(END, i)
        i3 = s.find('}', i2)
        contents = s[i1 + 1:i2]
        fixed = fix(contents)
        s = s.replace(contents, fixed)
        i = i3

    if '-w' in sys.argv:
        suffix = ''
    else:
        suffix = '.alter'
    f = open(arg + suffix, 'w')
    f.write(s)
    f.close()
