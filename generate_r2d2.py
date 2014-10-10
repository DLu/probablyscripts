#!/usr/bin/python
import scipy.io.wavfile
from pylab import *
import numpy
from math import pi

rate = 22050


def beep(freq, length, amplitude=30000, attack=.2, decay=.1, silence=.1):
    data = []
    N = rate * length
    wave = rate / freq
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
        data.append(amp * sin(x))
    data += [0] * int(silence * N)
    return data


def sweep(freq1, freq2, length, amplitude=30000,
          attack=.2, decay=.1, silence=.1, transition=.2):
    data = []
    N = rate * length
    wave1 = rate / freq1
    wave2 = rate / freq2
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
            print p, freq1, freq3, freq2
            x = i * 2 * pi / wave3

        if i < att:
            amp = amplitude * i / (N * attack)
        elif i > dec:
            amp = amplitude * (N - i) / (N * decay)
        else:
            amp = amplitude

        data.append(amp * sin(x))
    data += [0] * int(silence * N)
    return data

t = 1.5
data = []
import random
# for l in [.1, .1, .1, .2, .1, .3, .1, .1, .05, .1, 0.1, .05]:
# for l in [.2, .3, .5]:
#f= random.randint(200, 500)
#data  += beep(f, l)

#data = beep(570, .2) + beep(590, .5) + beep(540, .3)
data = sweep(10, 200, 0.5)

data = numpy.array([numpy.int16(x) for x in data])

plot(data)
# plot(data2[:N])
grid(True)
show()


scipy.io.wavfile.write('r2_sound_4.wav', rate, data)
