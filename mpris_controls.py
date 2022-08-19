import asyncio
import enum

from dbus_next import Variant
from dbus_next.aio import MessageBus
from dbus_next.constants import PropertyAccess
from dbus_next.service import ServiceInterface, dbus_property, method


class PlaybackStatus(enum.Enum):
    PLAYING = 'Playing'
    PAUSED = 'Paused'
    STOPPED = 'Stopped'


class MprisMediaPlayer2Interface(ServiceInterface):
    def __init__(self, nice_name, desktop_name=''):
        super().__init__('org.mpris.MediaPlayer2')
        self.nice_name = nice_name
        self.desktop_name = desktop_name

    @method()
    def Raise(self):
        pass

    @method()
    def Quit(self):
        pass

    @dbus_property(PropertyAccess.READ)
    def CanQuit(self) -> 'b':
        return False

    @dbus_property()
    def Fullscreen(self) -> 'b':
        return False

    @Fullscreen.setter
    def Fullscreen(self, val: 's'):
        pass

    @dbus_property(PropertyAccess.READ)
    def CanRaise(self) -> 'b':
        return False

    @dbus_property(PropertyAccess.READ)
    def HasTrackList(self) -> 'b':
        return False

    @dbus_property(PropertyAccess.READ)
    def Identity(self) -> 's':
        return self.nice_name

    @dbus_property(PropertyAccess.READ)
    def DesktopEntry(self) -> 's':
        return self.desktop_name

    @dbus_property(PropertyAccess.READ)
    def SupportedUriSchemes(self) -> 'as':
        return []

    @dbus_property(PropertyAccess.READ)
    def SupportedMimeTypes(self) -> 'as':
        return []


class MprisPlayerInterface(ServiceInterface):
    def __init__(self, control_callback):
        super().__init__('org.mpris.MediaPlayer2.Player')
        self.control_callback = control_callback
        self.status = PlaybackStatus.STOPPED
        self.metadata = {}

    @method()
    async def Next(self):
        await self.control_callback('next')

    @method()
    async def Previous(self):
        await self.control_callback('prev')

    @method()
    async def Pause(self):
        await self.control_callback('pause')

    @method()
    async def PlayPause(self):
        await self.control_callback('playpause')

    @method()
    async def Stop(self):
        await self.control_callback('stop')

    @method()
    async def Play(self):
        await self.control_callback('play')

    @method()
    def Seek(self, Offset: 'x'):
        pass

    @method()
    def SetPosition(self, TrackId: 'o', Position: 'x'):
        pass

    @method()
    def OpenUri(self, Uri: 's'):
        raise RuntimeError('cannot open uri')

    def set_playback_status(self, status):
        if status != self.status:
            self.status = status
            self.emit_properties_changed({'PlaybackStatus': self.PlaybackStatus})

    def set_metadata(self, title, trackid, artist=None, album=None, art_url=None):
        metadata = {'xesam:title': Variant('s', title),
                    'mpris:trackid': Variant('o', f'/com/probablydavid/subso/{trackid}')}
        if artist:
            metadata['xesam:artist'] = Variant('s', artist)
        if album:
            metadata['xesam:album'] = Variant('s', album)
        if art_url:
            metadata['mpris:artUrl'] = Variant('s', art_url)

        if metadata != self.metadata:
            self.metadata = metadata
            self.emit_properties_changed({'Metadata': self.metadata})

    @dbus_property(PropertyAccess.READ)
    def PlaybackStatus(self) -> 's':
        return self.status.value

    @dbus_property()
    def LoopStatus(self) -> 's':
        return 'None'

    @LoopStatus.setter
    def LoopStatus(self, val: 's'):
        pass

    @dbus_property()
    def Rate(self) -> 'd':
        return 1.0

    @Rate.setter
    def Rate(self, val: 'd'):
        pass

    @dbus_property()
    def Shuffle(self) -> 'b':
        return False

    @Shuffle.setter
    def Shuffle(self, val: 'b'):
        pass

    @dbus_property(PropertyAccess.READ)
    def Metadata(self) -> 'a{sv}':
        return self.metadata

    @dbus_property(PropertyAccess.READ)
    def Position(self) -> 'x':
        return 0

    @dbus_property(PropertyAccess.READ)
    def MinimumRate(self) -> 'd':
        return 1.0

    @dbus_property(PropertyAccess.READ)
    def MaximumRate(self) -> 'd':
        return 1.0

    @dbus_property(PropertyAccess.READ)
    def CanGoNext(self) -> 'b':
        return True

    @dbus_property(PropertyAccess.READ)
    def CanGoPrevious(self) -> 'b':
        return False

    @dbus_property(PropertyAccess.READ)
    def CanPlay(self) -> 'b':
        return True

    @dbus_property(PropertyAccess.READ)
    def CanPause(self) -> 'b':
        return True

    @dbus_property(PropertyAccess.READ)
    def CanSeek(self) -> 'b':
        return False

    @dbus_property(PropertyAccess.READ)
    def CanControl(self) -> 'b':
        return True


class MprisPlaylistInterface(ServiceInterface):
    def __init__(self):
        super().__init__('org.mpris.MediaPlayer2.Playlists')

    @dbus_property(PropertyAccess.READ)
    def PlaylistCount(self) -> 'u':
        return 0


class MprisControls:
    @classmethod
    async def create(cls, nice_name, identifier, callback):
        self = MprisControls()
        self.bus = await MessageBus().connect()
        self.mp = MprisMediaPlayer2Interface(nice_name, identifier)
        self.player = MprisPlayerInterface(callback)
        self.playlist = MprisPlaylistInterface()

        self.bus.export('/org/mpris/MediaPlayer2', self.mp)
        self.bus.export('/org/mpris/MediaPlayer2', self.player)
        self.bus.export('/org/mpris/MediaPlayer2', self.playlist)
        await self.bus.request_name(f'org.mpris.MediaPlayer2.{identifier}')
        return self

    def set_playback_status(self, status):
        self.player.set_playback_status(status)

    def set_metadata(self, title, trackid, artist=None, album=None, art_url=None):
        self.player.set_metadata(title, trackid, artist, album, art_url)


async def control_button(s):
    print(f'---> {s}')


async def main():
    controls = await MprisControls.create('Empress', 'subso', control_button)
    await asyncio.sleep(2)

    controls.set_playback_status(PlaybackStatus.PLAYING)
    controls.set_metadata('Everything is fine.', 9999)

    await controls.bus.wait_for_disconnect()


if __name__ == '__main__':
    try:
        asyncio.get_event_loop().run_until_complete(main())
    except KeyboardInterrupt:
        pass
