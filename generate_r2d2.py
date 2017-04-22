#!/usr/bin/python
import scipy.io.wavfile
import pylab
import numpy
from math import pi, sin
import random
import argparse

class BeepGenerator:
    def __init__(self, rate=22050):
        self.rate = rate
        self.data = []

    def add_beep(self, freq, length, amplitude=30000,
                    attack=.2, decay=.1, silence=.1):
        N = self.rate * length
        wave = self.rate / freq
        att = N * attack
        dec = N - N * decay

        for i in range(int(N)):
            x = i * 2 * pi / wave
            if i < N * attack:
                amp = amplitude * i / (N * attack)
            elif i > dec:
                amp = amplitude * (N - i) / (N * decay)
            else:
                amp = amplitude
            self.data.append(amp * sin(x))
        self.data += [0] * int(silence * N)

    def add_sweep(self, freq1, freq2, length, amplitude=30000,
              attack=.2, decay=.1, silence=.1, transition=.2):
        N = self.rate * length
        wave1 = self.rate / freq1
        wave2 = self.rate / freq2
        att = N * attack
        dec = N - N * decay
        for i in range(int(N)):
            if i < N / 2 - transition * N / 2:
                x = i * 2 * pi / wave1
            elif i > N / 2 + transition / 2 * N:
                x = i * 2 * pi / wave2
            else:
                i2 = i - (N / 2 - transition / 2 * N)
                p = i2 / (transition * N)
                freq3 = (freq2 * p + freq1 * (1 - p)) / 1
                wave3 = rate / freq3
                x = i * 2 * pi / wave3

            if i < att:
                amp = amplitude * i / (N * attack)
            elif i > dec:
                amp = amplitude * (N - i) / (N * decay)
            else:
                amp = amplitude

            self.data.append(amp * sin(x))
        self.data += [0] * int(silence * N)

    def finish(self, filename=None, plot=False):
        if plot:
            pylab.plot(self.data)
            pylab.grid(True)
            pylab.show()

        if filename:
            data = numpy.array([numpy.int16(x) for x in self.data])
            scipy.io.wavfile.write(filename, self.rate, data)

r2 = BeepGenerator()
t = 1.5
for l in [.1, .1, .1, .2, .1, .3, .1, .1, .05, .1, 0.1, .05]:
#for l in [.2, .3, .5]:
    f= random.randint(200, 500)
    r2.add_beep(f, l)

#data = beep(570, .2) + beep(590, .5) + beep(540, .3)
#data = sweep(10, 200, 0.5)

r2.finish('r2.wav', True)
