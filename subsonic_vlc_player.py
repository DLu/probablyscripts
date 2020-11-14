import time

from pynput.keyboard import Key, KeyCode, Listener

import vlc


MEDIA_RIGHT = 269025047
UNKNOWN_SKIP = 269025048

class VlcPlayer:
    def __init__(self):
        self.instance = vlc.Instance()
        self.player = self.instance.media_player_new()

        self.eventManager = self.player.event_manager()
        self.eventManager.event_attach(vlc.EventType.MediaPlayerEndReached, self.over_callback)
        self.playing = False
        self.full_play = False

        self.keyboard = Listener(on_press=self.on_press)
        self.keyboard.start()

    def play(self, wait=True):
        if not self.player.is_playing():
            if self.player.get_state() == vlc.State.Ended:
                self.player.stop()  # Restart it
            self.player.play()
        self.playing = True
        self.full_play = False

        while wait and self.playing:
            time.sleep(0.5)

        return wait and self.full_play

    def over_callback(self, event):
        self.playing = False
        self.full_play = True

    def stop(self):
        self.player.stop()

    def stream(self, url):
        self.player.set_mrl(url)
        return self.play()

    def on_press(self, key):
        if key == Key.pause:
            self.player.pause()
        elif isinstance(key, KeyCode) and key.vk in [MEDIA_RIGHT, UNKNOWN_SKIP]:
            self.player.stop()
            self.full_play = False
            self.playing = False
