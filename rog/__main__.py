# Copyright (C) 2023 Kyoken, kyoken@kyoken.ninja

# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 3
# of the License, or (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.

import argparse
import logging
import sys

from gi.repository import GLib

try:
    import ratbag
except ImportError:
    sys.path.append('ratbag-python')
    import ratbag


logger = logging.getLogger('rogdrv')


class ROGDRVConfig(object):
    """
    Mouse configuration tool
    """
    def _get_device(self, callback):
        mainloop = GLib.MainLoop()
        ratbagd = ratbag.Ratbag.create()

        ratbagd.connect('device-added', callback)
        ratbagd.start()

        GLib.timeout_add(1000, mainloop.quit)
        mainloop.run()

    def run(self):
        if len(sys.argv) < 2 or sys.argv[1] in ('-h', '--help'):
            self._help()
            return

        cmd = sys.argv.pop(1)

        # if cmd != 'actions':
        #     self._device = get_device()
        #     if not self._device:
        #         print('Device not found')
        #         return

        if not cmd.startswith('_'):
            if hasattr(self, cmd):
                sys.argv[0] += ' ' + cmd
                method = getattr(self, cmd)
                method()
                return

        self._help()

    def _help(self):
        print('''Usage:
  rogdrv-config <command> --help - display help for a command
  rogdrv-config <command> [--debug] [args] - run a command

Available commands:''')

        for cmd in dir(self):
            if cmd.startswith('_'):
                continue

            if cmd == 'run':
                continue

            method = getattr(self, cmd)
            doc = (
                method.__doc__
                .strip('\n')
                .strip())

            print('  rogdrv-config {} - {}'.format(cmd, doc))

    def actions(self):
        """
        display list of available action codes
        """
        from ratbag.hid import Key

        keys = []
        for name in dir(Key):
            if name.startswith('KEY_'):
                key = getattr(Key, name)
                if 4 < key.value <= 99:
                    keys.append(key)
        keys.sort(key=lambda x: x.value)

        specials = []
        for name in dir(ratbag.ActionSpecial.Special):
            special = getattr(ratbag.ActionSpecial.Special, name)
            if hasattr(special, 'value'):
                specials.append(special)
        specials.sort(key=lambda x: x.value)

        print('Keyboard actions:')
        for key in keys:
            print('  {action} (0x{action:02X}): {name}'.format(**{
                'action': key.value,
                'name': key.name,
            }))

        print('')
        print('Mouse actions:')
        for i in range(0, 5):
            action = i + 0xF0
            print('  {action} (0x{action:02X}): {name}'.format(**{
                'action': action,
                'name': f'Button {i + 1}',
            }))
        for special in specials:
            print('  {action} (0x{action:02X}): {name}'.format(**{
                'action': special.value,
                'name': special.name,
            }))

    def profile(self):
        """
        get/set profile
        """
        parser = argparse.ArgumentParser()
        parser.add_argument(
            '-p', '--profile', type=int, default=-1, required=False,
            help='Profile no. to set, starting from 0')
        args = parser.parse_args()

        def read(r, device):
            if args.profile >= 0:
                for profile in device.profiles:
                    if profile.index == args.profile:
                        profile.set_active()

            for profile in device.profiles:
                if profile.active:
                    print('Profile: {}'.format(profile.index))

        self._get_device(read)

    def bind(self):
        """
        bind a button or display current bindings
        """
        parser = argparse.ArgumentParser()
        parser.add_argument(
            '-b', '--button', type=int, default=-1, required=False,
            help='Button no. to bind, starting from 0')
        parser.add_argument(
            '-a', '--action', type=str, required=False, help='Action code')
        args = parser.parse_args()

        def read(r, device):
            from ratbag.drivers.asus import asus_get_linux_key_code

            if args.button >= 0 and args.action:
                action = args.action.lower()
                if action.startswith('0x'):
                    action_code = int(action, 16)
                else:
                    action_code = int(action)

                for profile in device.profiles:
                    if not profile.active:
                        continue

                    for button in profile.buttons:
                        if button.index == args.button:
                            if action_code >= ratbag.ActionSpecial.Special.UNKNOWN.value:
                                for name in dir(ratbag.ActionSpecial.Special):
                                    special = getattr(ratbag.ActionSpecial.Special, name)
                                    if hasattr(special, 'value') and special.value == action_code:
                                        button.set_action(ratbag.ActionSpecial.create(special))
                            elif action_code >= 0xF0:
                                button.set_action(ratbag.ActionButton.create(action_code - 0xF0 + 1))
                            else:

                                button.set_action(ratbag.ActionKey.create(asus_get_linux_key_code(action_code)))

                device.emit('commit', None)

            for profile in device.profiles:
                if not profile.active:
                    continue

                for button in profile.buttons:
                    print(f'{button.index}: {button.action}')

        self._get_device(read)

    def led(self):
        """
        get/set LED colors
        """
        parser = argparse.ArgumentParser()
        parser.add_argument(
            '-l', '--led', type=int, required=False, default=-1,
            help='LED no. to set, starting from 0')
        parser.add_argument(
            '-c', '--color', type=str, required=False, default=None,
            help='Color in hex. HTML format, ex.: aabbcc')
        parser.add_argument(
            '-b', '--brightness', type=int, required=False, default=255,
            help='Brightness: 0 - 255')
        parser.add_argument(
            '-m', '--mode', type=str, required=False, default='ON',
            help='LED mode: ON (default), CYCLE, BREATHING')
        args = parser.parse_args()

        def read(r, device):
            if args.led >= 0 and args.color:
                # convert color from HTML
                r = 0
                g = 0
                b = 0
                if args.color:
                    color = args.color.lstrip('#')
                    r = int(color[0:2], 16)
                    g = int(color[2:4], 16)
                    b = int(color[4:6], 16)

                for profile in device.profiles:
                    if not profile.active:
                        continue

                    for led in profile.leds:
                        if led.index == args.led:
                            mode = getattr(ratbag.Led.Mode, args.mode)
                            led.set_mode(mode)
                            led.set_color((r, g, b))
                            led.set_brightness(max(args.brightness, 0))

                device.emit('commit', None)

            for profile in device.profiles:
                if not profile.active:
                    continue

                for led in profile.leds:
                    # convert color to HTML
                    color = '#{:02x}{:02x}{:02x}'.format(*led.color)
                    print(f'{led.index}: {led.mode.name} {color} brightness={led.brightness}')

        self._get_device(read)

    def dpi(self):
        """
        get/set DPI
        """
        parser = argparse.ArgumentParser()
        parser.add_argument(
            '-d', '--dpi', type=int, default=-1, required=False,
            help='DPI rate')
        parser.add_argument(
            '-p', '--preset', type=int, default=0, required=False,
            help='Preset no. to set, starting from 0')
        args = parser.parse_args()

        def read(r, device):
            if args.dpi >= 0:
                for profile in device.profiles:
                    if not profile.active:
                        continue

                    for resolution in profile.resolutions:
                        if resolution.index == args.preset:
                            resolution.set_dpi((args.dpi, args.dpi))

                device.emit('commit', None)

            for profile in device.profiles:
                if not profile.active:
                    continue

                for resolution in profile.resolutions:
                    print(f'DPI Preset {resolution.index}: {resolution.dpi[0]}')

        self._get_device(read)

    def rate(self):
        """
        get/set polling rate
        """
        parser = argparse.ArgumentParser()
        parser.add_argument(
            '-r', '--rate', type=int, default=-1, required=False,
            help='Polling rate in Hz: 125, 250, 500, 1000')
        args = parser.parse_args()

        def read(r, device):
            if args.rate >= 0:
                for profile in device.profiles:
                    if not profile.active:
                        continue

                    profile.set_report_rate(args.rate)

                device.emit('commit', None)

            for profile in device.profiles:
                if not profile.active:
                    continue

                print(f'Polling rate: {profile.report_rate} Hz')

        self._get_device(read)

    def _sleep(self):
        """
        get/set sleep timeout, battery charge and alert level
        """
        parser = argparse.ArgumentParser()
        parser.add_argument(
            '-t', '--timeout', type=int, required=False, default=-1,
            help="Timeout in minutes: 0 (don't sleep), 1 (default), 2, 3, 5, 10")
        parser.add_argument(
            '-l', '--level', type=int, required=False, default=-1,
            help='Battery alert level in %%: 0%% (disabled), 25%% (default), 50%%')
        args = parser.parse_args()

        if not self._device.wireless:
            print('Device is not wireless')
            return

        timeout = 1
        level = 25

        if args.timeout >= 0:
            timeout = args.timeout

        if args.level >= 0:
            level = args.level

        if args.timeout >= 0 or args.level >= 0:
            self._device.set_sleep_alert(timeout, level)
            self._device.save()

        sleep, charge, alert = self._device.get_sleep_charge_alert()
        print('Sleep: {}'.format('{} min.'.format(sleep) if sleep else 'disabled'))
        print('Charge: {}%'.format(charge))
        print('Alert: {}'.format('{}%'.format(alert) if alert else 'disabled'))

    def snapping(self):
        """
        enable/disable snapping
        """
        parser = argparse.ArgumentParser()
        parser.add_argument(
            '-s', '--snapping', type=int, required=False, default=-1,
            help='Angle snapping: 0 - disabled, 1 - enabled')
        args = parser.parse_args()

        def read(r, device):
            if args.snapping >= 0:
                for profile in device.profiles:
                    if not profile.active:
                        continue

                    profile.set_angle_snapping(args.snapping)

                device.emit('commit', None)

            for profile in device.profiles:
                if not profile.active:
                    continue

                print('Angle snapping: {}'.format(
                    'enabled' if profile.angle_snapping else 'disabled'))

        self._get_device(read)

    def response(self):
        """
        get/set button response
        """
        parser = argparse.ArgumentParser()
        parser.add_argument(
            '-r', '--response', type=int, required=False, default=0,
            help='Response in ms: 4, 8, 12, 16, 20, 24, 28, 32')
        args = parser.parse_args()

        def read(r, device):
            if args.response > 0:
                for profile in device.profiles:
                    if not profile.active:
                        continue

                    profile.set_debounce(args.response)

                device.emit('commit', None)

            for profile in device.profiles:
                if not profile.active:
                    continue

                print(f'Debounce time: {profile.debounce} ms')

        self._get_device(read)


def logging_init():
    if '--debug' in sys.argv:
        sys.argv.pop(sys.argv.index('--debug'))
        logging.basicConfig(
            level=logging.DEBUG,
            format='[%(asctime)s] [%(levelname)s] %(message)s')
        logger.setLevel(logging.DEBUG)


def rogdrv():
    logging_init()
    from .ui import gtk3_main
    gtk3_main()


def rogdrv_config():
    logging_init()
    app = ROGDRVConfig()
    app.run()
