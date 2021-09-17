#!/usr/bin/python
import subprocess
import argparse
import re
import os.path
import shutil

AUDIO_FILE = '/tmp/out.wav'
VIDEO_FILE = '/tmp/out.raw'

NUMBER = '([\d\.]+)'
PROPS_PATTERN = re.compile('Movie Size accordings to file header: ' + NUMBER + ' x ' + NUMBER + '.*')
CSI = '\x1B['

def color(s, color = '34m'):
    return CSI +color + s + CSI + '0m'

def command(cmd, output=False):
    print color(' '.join(cmd))
    if output:
        return subprocess.check_output(cmd)
    else:
        subprocess.call(cmd)

def swf_to_video(infile, outfile=None, width=None, rate=30):
    properties = command(['swfbbox', infile], True)
    m = PROPS_PATTERN.match(properties)
    if not m:
        return "Cannot parse properties: " + properties

    w,h = map(int, map(float, m.groups()))

    gnash = ['dump-gnash', '-1', '-D', VIDEO_FILE + '@' + str(rate)]
    gnash += ['-A', AUDIO_FILE, infile]
    if width:
        s = float(width) / w
        gnash += ['-s', str(s)]
        w*=s
        h*=s

    command(gnash)

    ffmpeg = ['ffmpeg', '-i', AUDIO_FILE]
    ffmpeg += ['-f', 'rawvideo', '-pix_fmt', 'rgb32']
    ffmpeg += ['-s:v', '%dx%d'%(w,h)]
    ffmpeg += ['-i', VIDEO_FILE]
    ffmpeg += ['-c:v', 'libx264']
    ffmpeg += ['-r', str(rate)]

    if outfile is None:
        a,b = os.path.splitext(infile)
        outfile = a + '.mp4'
    ffmpeg += [outfile]

    command(ffmpeg)

    os.remove(AUDIO_FILE)
    os.remove(VIDEO_FILE)

if __name__=='__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('infile')
    parser.add_argument('outfile', nargs='?')
    parser.add_argument('-w', '--width', type=int)
    args = parser.parse_args()
    swf_to_video(args.infile, args.outfile, args.width)
