import asyncio
import click
from dbus_next import Variant, DBusError
from dbus_next.aio import MessageBus

# https://specifications.freedesktop.org/notification-spec/notification-spec-latest.html


class NotificationWhiz:
    @classmethod
    async def create(cls, app_name):
        self = NotificationWhiz()
        self.app_name = app_name
        self.bus = await MessageBus().connect()
        introspection = await self.bus.introspect(
            'org.freedesktop.Notifications', '/org/freedesktop/Notifications'
        )
        self.proxy_object = self.bus.get_proxy_object(
            'org.freedesktop.Notifications',
            '/org/freedesktop/Notifications',
            introspection,
        )
        self.interface = self.proxy_object.get_interface(
            'org.freedesktop.Notifications'
        )

        return self

    async def send_notification(self, title, contents, replaces_id=0, icon='', timeout=-1):
        actions = ['default', 'default']
        hints = {'urgency': Variant('y', 1)}
        try:
            return await self.interface.call_notify(self.app_name, replaces_id, icon,
                                                    title, contents,
                                                    actions, hints, timeout)
        except DBusError as e:
            click.secho(f'Notification Failure: {e}', fg='black', bg='red')
            return 0


async def main():
    whiz = await NotificationWhiz.create('TestAppName')
    await asyncio.sleep(2)
    await whiz.send_notification('Hello', 'World!')


if __name__ == '__main__':
    try:
        asyncio.get_event_loop().run_until_complete(main())
    except KeyboardInterrupt:
        pass
