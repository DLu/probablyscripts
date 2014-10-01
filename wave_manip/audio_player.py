import pyaudio
import numpy as np
import struct
import thread

CHUNK = 1024


class AudioPlayer:

    def __init__(self, wave):
        self.player = pyaudio.PyAudio()

        self.stream = self.player.open(format=self.player.get_format_from_width(wave.get_width()),
                                       channels=wave.spf.getnchannels(),
                                       rate=wave.spf.getframerate(),
                                       output=True)

        self.signal = None
        self.inc = None

    def close(self):
        self.stream.close()
        self.player.terminate()

    def play(self):
        data = 0

        while data != '':
            sig = self.signal[self.inc:self.inc + CHUNK]
            data = struct.pack("%dh" % (len(sig)), *list(sig))
            self.stream.write(data)
            self.inc += CHUNK

    def start(self, signal):
        self.signal = signal
        self.inc = 0

        thread.start_new_thread(self.play, ())


if __name__ == '__main__':
    import sys
    import audio_clip
    try:
        clip = audio_clip.AudioClip(sys.argv[1])
        a = AudioPlayer(clip)
        a.start(clip.signal)
    finally:
        a.close()
