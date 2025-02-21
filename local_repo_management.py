import argparse
import pathlib
import subprocess
import click

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('repo_name')
    args = parser.parse_args()

    root = pathlib.Path('/opt/git') / f'{args.repo_name}.git'

    if root.exists():
        click.secho(f'{root} already exists!', fg='red')
        exit(-1)
    root.mkdir()

    subprocess.call(['git', '--bare', 'init', '-b', 'devel'], cwd=root)
    subprocess.call(['git', 'update-server-info'], cwd=root)
    subprocess.call(['chown', '-R', 'git', str(root)], cwd=root)

    click.secho()
    click.secho(f'git remote add origin git@gonzo.probablydavid.com:/opt/git/{root.name}', bg='blue', fg='bright_white')
