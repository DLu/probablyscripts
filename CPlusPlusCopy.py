#!/usr/bin/python3
import argparse
import pathlib

DESCRIPTION = """
CPlusPlusCopy is a utility for copying the contents of one C++ source code file to another while also doing the
appropriate renaming inside the file. For example, if you have a header file called glorious_widget.h, this utility
will assume that it defines a class called GloriousWidget, maybe has header guards of the style GLORIOUS_WIDGET_H and
maybe other references to glorious_widget. If you want to copy it to fantastic_doohickey.h, it will replace
GloriousWidget with FantasticDoohickey, GLORIOUS_WIDGET_H to FANTASTIC_DOOHICKEY_H and glorious_widget to
fantastic_doohickey.
"""


def get_camel_case(name):
    return ''.join(map(str.title, name.split('_')))


def cplusplus_copy(in_file, out_file):
    in_base = pathlib.Path(in_file).stem
    out_base = pathlib.Path(out_file).stem
    replacements = {
        get_camel_case(in_base): get_camel_case(out_base),
        in_base.upper(): out_base.upper(),
        in_base: out_base
    }

    with open(in_file, 'r') as f:
        contents = f.read()

    for old_s, new_s in replacements.items():
        contents = contents.replace(old_s, new_s)

    with open(out_file, 'w') as f:
        f.write(contents)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=DESCRIPTION)
    parser.add_argument('in_file')
    parser.add_argument('out_file')
    args = parser.parse_args()
    cplusplus_copy(args.in_file, args.out_file)
