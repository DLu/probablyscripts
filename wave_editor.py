#!/usr/bin/python

import sys
from wave_manip.audio_clip import AudioClip
from wave_manip.wave_gui import WaveGUI

if __name__=='__main__':
    clip = AudioClip(sys.argv[1])
    w = WaveGUI()
    w.add_clip(clip)
    
    while w.ok():
        
        w.update()
