#!/usr/bin/python

import sys
from wave_manip.audio_clip import AudioClip
from wave_manip.wave_gui import WaveGUI

if __name__=='__main__':
    w = None
    try:
        clip = AudioClip(sys.argv[1])
        w = WaveGUI(clip)
        
        while w.ok():            
            w.update()
    finally:
        if w is not None:
            w.player.close()
