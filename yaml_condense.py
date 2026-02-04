#!/usr/bin/python3

import argparse
import pathlib
import yaml


def condense(common, dicts):
    keys = set(dicts[0].keys())
    for d in dicts[1:]:
        keys = keys.intersection(set(d.keys()))

    for key in sorted(keys):
        if isinstance(dicts[0][key], dict):
            new_common = {}
            new_dicts = [d[key] for d in dicts]

            condense(new_common, new_dicts)

            common[key] = new_common
            for d in dicts:
                if not d[key]:
                    del d[key]
        else:
            first_value = dicts[0][key]
            if isinstance(first_value, list):
                values = {tuple(d[key]) for d in dicts}
            else:
                values = {d[key] for d in dicts}
            if len(values) == 1:
                for d in dicts:
                    del d[key]
                common[key] = first_value


parser = argparse.ArgumentParser()
parser.add_argument('filepaths', metavar='filepath', type=pathlib.Path, nargs='+')
parser.add_argument('-w', '--write', action='store_true')
args = parser.parse_args()

common = {}
dicts = []
for filepath in args.filepaths:
    dicts.append(yaml.safe_load(open(filepath)))

condense(common, dicts)

yaml.dump(common, open('common.yaml', 'w'))
if args.write:
    for filepath, d in zip(args.filepaths, dicts):
        yaml.dump(d, open(filepath, 'w'))
