import asyncio

from pynput.keyboard import Key, KeyCode, Listener

import vlc


MEDIA_RIGHT = 269025047
UNKNOWN_SKIP = 269025048


class VlcPlayer:
    def __init__(self):
        self.instance = vlc.Instance()
        self.player = self.instance.media_player_new()

        self.done_playing_condition = asyncio.Condition()
        self.loop = asyncio.get_event_loop()

        self.eventManager = self.player.event_manager()
        self.eventManager.event_attach(vlc.EventType.MediaPlayerEndReached, self.over_callback)
        self.full_play = False

        self.keyboard = Listener(on_press=self.on_press)
        self.keyboard.start()

    async def play(self, wait=True):
        if not self.player.is_playing():
            if self.player.get_state() == vlc.State.Ended:
                self.player.stop()  # Restart it
            self.player.play()
        self.full_play = False

        if wait:
            async with self.done_playing_condition:
                await self.done_playing_condition.wait()

        return wait and self.full_play

    async def stop_it(self):
        self.full_play = True
        async with self.done_playing_condition:
            self.done_playing_condition.notify_all()

    def over_callback(self, event):
        asyncio.run_coroutine_threadsafe(self.stop_it(), self.loop)

    async def stop(self):
        self.player.stop()

        async with self.done_playing_condition:
            self.done_playing_condition.notify_all()

    async def stream(self, url):
        self.player.set_mrl(url)
        return await self.play()

    async def play_pause(self):
        self.player.pause()

    async def skip(self):
        self.player.stop()
        self.full_play = False
        async with self.done_playing_condition:
            self.done_playing_condition.notify_all()

    def on_press(self, key):
        if key == Key.pause:
            self.play_pause()
        elif isinstance(key, KeyCode) and key.vk in [UNKNOWN_SKIP]:
            self.skip()
