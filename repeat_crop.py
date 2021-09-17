#!/usr/bin/python3

import argparse
import click
import pathlib
import subprocess

parser = argparse.ArgumentParser()
parser.add_argument('filenames', metavar='filename', nargs='+', type=pathlib.Path)
parser.add_argument('-x', type=int)
parser.add_argument('-y', type=int)
parser.add_argument('-w', '--width', type=int)
parser.add_argument('-v', '--height', type=int)
parser.add_argument('-n', '--name')
args = parser.parse_args()

if args.x is None:
    args.x = click.prompt('X coordinate?', type=int)
if args.y is None:
    args.y = click.prompt('Y coordinate?', type=int)
if args.width is None:
    args.width = click.prompt('width?', type=int)
if args.height is None:
    args.height = click.prompt('height?', type=int)
if args.name is None:
    args.name = click.prompt('name?')

index = 0
for filename in args.filenames:
    while True:
        output = pathlib.Path(str(filename).replace(filename.stem, args.name + f'{index:02}'))
        if not output.exists():
            break
        index += 1

    cmd = ['convert', str(filename), '-crop', f'{args.width}x{args.height}+{args.x}+{args.y}', '+repage', str(output)]
    subprocess.call(cmd)
