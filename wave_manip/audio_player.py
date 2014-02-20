import pyaudio
import numpy as np
import struct

CHUNK = 1024

class AudioPlayer:

    def __init__(self, wave):
        self.player = pyaudio.PyAudio()
        
        self.stream = self.player.open(format=self.player.get_format_from_width(wave.get_width()),
                                channels = wave.spf.getnchannels(),
                                rate = wave.spf.getframerate(),
                                output = True)
        
    def close(self):
        self.stream.close()
        self.player.terminate()

    def play(self, clip):
        
        sig= clip[1:CHUNK]

        inc = 0
        data = 0

        #play 
        while data != '' and inc < 300000:
            data = struct.pack("%dh"%(len(sig)), *list(sig))    
            self.stream.write(data)
            inc=inc+CHUNK
            sig=clip[inc:inc+CHUNK]
            
if __name__=='__main__':
    import sys, audio_clip
    try:
        clip = audio_clip.AudioClip(sys.argv[1])
        a = AudioPlayer(clip)
        a.play(clip.signal)
    finally:
        a.close()



