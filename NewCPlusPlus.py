#!/usr/bin/python3

import argparse
import datetime
import pathlib

PROPRIETARY_BLOCK = """/*******************************************************
 * Copyright (C) {year} {company}
 *
 * This file can not be copied and/or distributed without the express
 * permission of {company}.
 *******************************************************/
"""

BSD_BLOCK = """/*********************************************************************
 * Software License Agreement (BSD License)
 *
 *  Copyright (c) {year}, {company}
 *  All rights reserved.
 *
 *  Redistribution and use in source and binary forms, with or without
 *  modification, are permitted provided that the following conditions
 *  are met:
 *
 *   * Redistributions of source code must retain the above copyright
 *     notice, this list of conditions and the following disclaimer.
 *   * Redistributions in binary form must reproduce the above
 *     copyright notice, this list of conditions and the following
 *     disclaimer in the documentation and/or other materials provided
 *     with the distribution.
 *   * Neither the name of {company} nor the names of its
 *     contributors may be used to endorse or promote products derived
 *     from this software without specific prior written permission.
 *
 *  THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
 *  "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
 *  LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS
 *  FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE
 *  COPYRIGHT OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT,
 *  INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING,
 *  BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
 *  LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
 *  CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT
 *  LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN
 *  ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
 *  POSSIBILITY OF SUCH DAMAGE.
 *********************************************************************/

/* Author: David V. Lu!! */
"""

HEADER_TEMPLATE = """%(copyright)s
#pragma once

namespace %(ns)s
{
class %(class)s
{
};
}  // namespace %(ns)s
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
parser.add_argument('company', nargs='?', default='Metro Robots')
parser.add_argument('-i', '--include', action='store_true')
parser.add_argument('-c', '--cpp', action='store_true')
parser.add_argument('-t', '--test', action='store_true')
parser.add_argument('-p', '--hpp', action='store_true')
parser.add_argument('-l', '--license', choices=['bsd', 'BSD', 'proprietary', 'PROPRIETARY'], default='proprietary')

args = parser.parse_args()
if not args.include and not args.cpp and not args.test:
    args.include = True
    args.cpp = True

if args.license.lower() == 'bsd':
    copyright_template = BSD_BLOCK
else:
    copyright_template = PROPRIETARY_BLOCK

copyright_block = copyright_template.format(company=args.company, year=datetime.datetime.now().year)

root = pathlib.Path('.').resolve()
folder = root.stem
class_name = ''.join(map(str.title, args.name.split('_')))

ext = 'hpp' if args.hpp else 'h'
if args.include:
    inc_path = root / 'include' / folder
    inc_path.mkdir(parents=True, exist_ok=True)
    new_path = inc_path / (args.name + '.' + ext)
    if not new_path.exists():
        print(new_path)
        guard = folder.upper() + '_' + args.name.upper() + '_' + ext.upper()
        with open(new_path, 'w') as f:
            f.write(HEADER_TEMPLATE % {'copyright': copyright_block, 'guard': guard, 'ns': folder, 'class': class_name})

if args.cpp:
    src_path = root / 'src'
    src_path.mkdir(parents=True, exist_ok=True)
    new_path = src_path / (args.name + '.cpp')
    if not new_path.exists():
        print(new_path)
        if args.include:
            header = '#include <%s/%s.%s>' % (folder, args.name, ext)
        else:
            header = ''

        with open(new_path, 'w') as f:
            f.write(CPP_TEMPLATE % {'copyright': copyright_block, 'ns': folder, 'header': header})

if args.test:
    test_path = root / 'test'
    test_path.mkdir(parents=True, exist_ok=True)
    new_path = test_path / (args.name + '.cpp')
    if not new_path.exists():
        print(new_path)

        with open(new_path, 'w') as f:
            f.write(TEST_TEMPLATE % {'copyright': copyright_block, 'class': class_name})
