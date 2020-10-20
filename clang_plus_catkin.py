#!/usr/bin/python3

import argparse
import cson
import pathlib
import rospkg
import subprocess


def my_sort_fne(path):
    path_s = str(path)
    if '/opt/ros' in path_s:
        return 2, path_s
    elif '/devel/include' in path_s:
        return 1, path_s
    return 0, path_s


rp = rospkg.RosPack()

def get_package_path(name):
    pkg_path = rp.get_path(name)
    return pathlib.Path(pkg_path)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('packages', metavar='package', nargs='*')
    parser.add_argument('-t', '--test', action='store_true')
    args = parser.parse_args()

    filepath = pathlib.Path('~/.atom/config.cson').expanduser()
    config = cson.load(open(filepath))

    linter_clang = config['*']['linter-clang']
    includes = list(map(pathlib.Path, linter_clang.get('clangIncludePaths', [])))

    for package in args.packages:
        i_path = get_package_path(package) / 'include'
        if i_path.exists() and i_path not in includes:
            print(f'Adding {i_path}...')
            includes.append(i_path)

    try:
        DEVEL = subprocess.check_output(['catkin', 'locate', '-d']).decode().strip()
        d_path = pathlib.Path(DEVEL) / 'include'
        if d_path.exists() and d_path not in includes:
            print(f'Adding {d_path}...')
            includes.append(d_path)
    except Exception:
        raise

    for build in pathlib.Path('/opt/ros/').glob('*'):
        binary_path = build / 'include'
        if binary_path.exists() and binary_path not in includes:
            print(f'Adding {binary_path}...')
            includes.append(binary_path)

    linter_clang['clangIncludePaths'] = list(map(str, sorted(includes, key=my_sort_fne)))

    if args.test:
        print(config)
        exit(0)

    cson.dump(config, open(filepath, 'w'), indent=2)
