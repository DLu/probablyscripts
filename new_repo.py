#!/usr/bin/python3
import argparse
import pathlib
import subprocess


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('name')
    args = parser.parse_args()

    folder = pathlib.Path('/opt/git/') / (args.name + '.git')

    subprocess.call(['sudo', 'mkdir', str(folder)])

    subprocess.call(['sudo', 'git', '--bare', 'init'], cwd=str(folder))

    subprocess.call(['sudo', 'chown', '-R', 'git', str(folder)])

    subprocess.call(['sudo', 'git', 'update-server-info'])
