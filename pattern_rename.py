#!/usr/bin/python3

import argparse
import click
import pathlib
import re
import shutil
import subprocess

parser = argparse.ArgumentParser()
parser.add_argument('needle')
parser.add_argument('replacement', nargs='?')
parser.add_argument('-g', '--git', action='store_true')
parser.add_argument('-r', '--recursive', action='store_true')
parser.add_argument('-s', '--simulate', action='store_true')

args = parser.parse_args()

queue = sorted(pathlib.Path('.').iterdir())

for path in queue:
    if path.name == '.git':
        continue

    if args.recursive and path.is_dir():
        queue += sorted(path.iterdir())

    m = re.search(args.needle, path.name)
    if not m:
        continue

    click.secho('Pattern matched for ', fg='blue', nl=False)
    click.secho(repr(path.name), fg='bright_blue', nl=False)
    click.secho(' with groups: ', fg='blue', nl=False)
    click.secho(f'{m.groups()}', fg='bright_blue')

    if args.replacement is None:
        continue

    if m.groups():
        replacement = str(args.replacement)  # Make a copy
        for i, g in enumerate(m.groups()):
            search_s = f'${i + 1}'
            if search_s not in replacement:
                click.secho(f'No place to insert Group {search_s}', fg='red')
                replacement = None
                break
            replacement = replacement.replace(search_s, g)

        if not replacement:
            continue

        replacement_path = path.parent / replacement
    else:
        replacement_path = path.parent / path.name.replace(args.needle, args.replacement)

    click.secho(f'\tMove to {replacement_path}', fg='green')
    if args.simulate:
        continue

    full_path = path.resolve()
    if replacement_path.exists():
        click.secho(f"Can't move {full_path} to {replacement_path}", fg='red')
        continue
    if args.git:
        subprocess.call(['git', 'mv', full_path, replacement_path])
    else:
        shutil.move(full_path, replacement_path)
