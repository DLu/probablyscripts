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

def swf_to_video(infile, outfile=None, rate=30):
    properties = subprocess.check_output(['swfbbox', infile])
    m = PROPS_PATTERN.match(properties)
    if not m:
        return "Cannot parse properties: " + properties

    w,h = map(int, map(float, m.groups()))

    gnash = ['dump-gnash', '-1', '-D', VIDEO_FILE + '@' + str(rate)]
    gnash += ['-A', AUDIO_FILE, infile]

    print gnash
    subprocess.call(gnash)

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

    print ffmpeg
    subprocess.call(ffmpeg)

    os.remove(AUDIO_FILE)
    os.remove(VIDEO_FILE)

if __name__=='__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('infile')
    parser.add_argument('outfile', nargs='?')
    parser.add_argument('-r', '--rate', default=30)
    args = parser.parse_args()
    swf_to_video(args.infile, args.outfile, args.rate)
