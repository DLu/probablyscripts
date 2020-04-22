#!/usr/bin/python3

import argparse
import pathlib

LOCUS_COPYRIGHT = """/*******************************************************
 * Copyright (C) 2020 Locus Robotics
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

TEST_TEMPLATE = """%(copyright)s
#include <gtest/gtest.h>

TEST(%(class)s, firstTest)
{
  EXPECT_TRUE(true);
}

int main(int argc, char **argv)
{
  testing::InitGoogleTest(&argc, argv);
  return RUN_ALL_TESTS();
}

"""

parser = argparse.ArgumentParser()
parser.add_argument('name')
parser.add_argument('-i', '--include', action='store_true')
parser.add_argument('-c', '--cpp', action='store_true')
parser.add_argument('-t', '--test', action='store_true')

args = parser.parse_args()
if not args.include and not args.cpp and not args.test:
    args.include = True
    args.cpp = True

root = pathlib.Path('.').resolve()
folder = root.stem
class_name = ''.join(map(str.title, args.name.split('_')))

if args.include:
    inc_path = root / 'include' / folder
    inc_path.mkdir(parents=True, exist_ok=True)
    new_path = inc_path / (args.name + '.h')
    if not new_path.exists():
        print(new_path)
        guard = folder.upper() + '_' + args.name.upper() + '_H'
        with open(new_path, 'w') as f:
            f.write(HEADER_TEMPLATE % {'copyright': LOCUS_COPYRIGHT, 'guard': guard, 'ns': folder, 'class': class_name})

if args.cpp:
    src_path = root / 'src'
    src_path.mkdir(parents=True, exist_ok=True)
    new_path = src_path / (args.name + '.cpp')
    if not new_path.exists():
        print(new_path)
        if args.include:
            header = '#include <%s/%s.h>' % (folder, args.name)
        else:
            header = ''

        with open(new_path, 'w') as f:
            f.write(CPP_TEMPLATE % {'copyright': LOCUS_COPYRIGHT, 'ns': folder, 'header': header})

if args.test:
    test_path = root / 'test'
    test_path.mkdir(parents=True, exist_ok=True)
    new_path = test_path / (args.name + '.cpp')
    if not new_path.exists():
        print(new_path)

        with open(new_path, 'w') as f:
            f.write(TEST_TEMPLATE % {'copyright': LOCUS_COPYRIGHT, 'class': class_name})
