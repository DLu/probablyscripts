#!/usr/bin/python

import subprocess
import argparse


def remote_command(cmd, machine, wdir=None, password=None):
    remote_cmd = ''
    if wdir:
        remote_cmd = 'cd ' + wdir + '&& '
    if password:
        remote_cmd += 'echo ' + password + ' | sudo -S '
    remote_cmd += cmd
    cmd = ['ssh', '-t', machine, remote_cmd]
    subprocess.call(cmd)


DIR = '/usr/share/sounds/ubuntu/stereo'
FN = 'system-ready.ogg'
parser = argparse.ArgumentParser()
parser.add_argument('ip')
parser.add_argument('soundfile', nargs='?')
parser.add_argument('-u', '--user', default='dlu')
parser.add_argument('-p', '--password')

args = parser.parse_args()

REMOTE = args.user + '@' + args.ip

if args.soundfile:
    cmd = ['scp', args.soundfile, REMOTE + ':startup.ogg']
    subprocess.call(cmd)
    target = '/home/%s/startup.ogg' % args.user
    remote_command('mv ' + target + ' .', wdir=DIR, password=args.password)
    target = 'startup.ogg'
else:
    target = 'dialog-question.ogg'

remote_command('rm ' + FN, wdir=DIR, password=args.password)
remote_command('ln -s ' + target + ' ' + FN, wdir=DIR, password=args.password)
