#!/usr/bin/python

import os
import argparse

LOCUS_COPYRIGHT = """/*******************************************************
 * Copyright (C) 2019 Locus Robotics
 *
 * This file can not be copied and/or distributed without the express
 * permission of Locus Robotics.
 *******************************************************/
"""

HEADER_TEMPLATE = """%(copyright)s
#ifndef %(guard)s
#define %(guard)s

namespace %(ns)s
{
class %(class)s
{
};
}  // namespace %(ns)s

#endif  // %(guard)s
"""

CPP_TEMPLATE = """%(copyright)s
%(header)s

namespace %(ns)s
{
}  // namespace %(ns)s
"""

parser = argparse.ArgumentParser()
parser.add_argument('name')
parser.add_argument('-i', '--include', action='store_true')
parser.add_argument('-c', '--cpp', action='store_true')

args = parser.parse_args()
if not args.include and not args.cpp:
    args.include = True
    args.cpp = True

folder = os.path.split(os.getcwd())[-1]
class_name = ''.join(map(str.title, args.name.split('_')))

if args.include:
    inc_path = 'include'
    if not os.path.exists(inc_path):
        os.mkdir(inc_path)
    full_inc_path = os.path.join(inc_path, folder)
    if not os.path.exists(full_inc_path):
        os.mkdir(full_inc_path)
    new_path = os.path.join(full_inc_path, args.name + '.h')
    guard = folder.upper() + '_' + args.name.upper() + '_H'
    if not os.path.exists(new_path):
        print new_path
        with open(new_path, 'w') as f:
            f.write(HEADER_TEMPLATE % {'copyright': LOCUS_COPYRIGHT, 'guard': guard, 'ns': folder, 'class': class_name})

if args.cpp:
    src_path = 'src'
    if not os.path.exists(src_path):
        os.mkdir(src_path)
    new_path = os.path.join(src_path, args.name + '.cpp')
    if args.include:
        header = '#include <%s/%s.h>' % (folder, args.name)
    else:
        header = ''

    if not os.path.exists(new_path):
        print new_path
        with open(new_path, 'w') as f:
            f.write(CPP_TEMPLATE % {'copyright': LOCUS_COPYRIGHT, 'ns': folder, 'header': header})
