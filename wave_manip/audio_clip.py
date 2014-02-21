import numpy as np
import wave
import math

class AudioClip:

    def __init__(self, filename):
        self.spf = wave.open(filename, 'rb')
        signal = self.spf.readframes(-1)
        self.signal = np.fromstring(signal, 'Int16')
        self.max = 32767

    def get_clip(self, start, length):
        rate = self.spf.getframerate()
        
        start_frame = start * rate
        num_frames =  length * rate

        signal = self.signal[ start_frame : start_frame + num_frames]
        return signal
        
    def partition(self, width):
        data = []
        n = len(self.signal)
        chunk = int(math.ceil(float(n)/width))
        
        for i in range(0, n, chunk):
            sub = self.signal[i:i+chunk]
            # max? abs?
            data.append( sum(map(abs,sub))/float(len(sub))/self.max )
        return chunk, data
        
    def get_width(self):
        return self.spf.getsampwidth()
