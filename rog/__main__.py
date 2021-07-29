# Copyright (C) 2018 Kyoken, kyoken@kyoken.ninja

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
import os
import signal
import sys
import threading
import logging

from . import defs
from .device import EventHandler, get_device

logger = logging.getLogger('rogdrv')


class ROGDRV(threading.Thread):
    """
    Virtual uinput device driver which converts mouse events
    into uinput events.
    """
    def __init__(self):
        super().__init__()
        parser = argparse.ArgumentParser()
        parser.add_argument(
            '-c', '--console', action='store_true', required=False,
            help='Starts in pure console mode, disables tray icon')
        self._args = parser.parse_args()

        self._device = get_device()
        self._handler = EventHandler()
        self._is_running = True

    @property
    def device(self):
        return self._device

    @property
    def handler(self):
        return self._handler

    @property
    def is_console(self):
        return self._args.console

    def stop(self):
        self._is_running = False

    def run(self):
        while self._is_running:
            e = self._device.next_event()
            self._handler.handle_event(e)


class ROGDRVConfig(object):
    """
    Mouse configuration tool
    """
    def __init__(self):
        self._device = None

    def run(self):
        if len(sys.argv) < 2:
            self._help()
            return

        cmd = sys.argv.pop(1)

        if cmd != 'actions':
            self._device = get_device()
            if not self._device:
                print('Device not found')
                return

        if not cmd.startswith('_'):
            if hasattr(self, cmd):
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
        print('Keyboard actions:')
        for action, name in defs.ACTIONS_KEYBOARD.items():
            print('  {action} (0x{action:02X}): {name}'.format(**{
                'action': action,
                'name': name,
            }))

        print('')
        print('Mouse actions:')
        for action, name in defs.ACTIONS_MOUSE.items():
            print('  {action} (0x{action:02X}): {name}'.format(**{
                'action': action,
                'name': name,
            }))

    def version(self):
        """
        get device firmware version
        """
        profile, ver1, ver2 = self._device.get_profile_version()
        print('Primary version: {:X}.{:02X}.{:02X}'.format(*ver1))
        print('Secondary version: {:X}.{:02X}.{:02X}'.format(*ver2))

    def profile(self):
        """
        get/set profile
        """
        parser = argparse.ArgumentParser()
        parser.add_argument(
            '-p', '--profile', type=int, default=0, required=False,
            help='Profile no. to set, starting from 1')
        args = parser.parse_args()

        if not self._device.profiles:
            print('Profiles are not supported')
            return

        if args.profile:
            self._device.set_profile(args.profile)

        profile, ver1, ver2 = self._device.get_profile_version()
        print('Profile: {}'.format(profile))

    def bind(self):
        """
        bind a button or display current bindings
        """
        parser = argparse.ArgumentParser()
        parser.add_argument(
            '-b', '--button', type=int, required=False, help='Button no. to bind, starting from 1')
        parser.add_argument(
            '-a', '--action', type=str, required=False, help='Action code')
        args = parser.parse_args()

        if args.button and args.action:
            action = args.action.lower()
            if action.startswith('0x'):
                action = int(action, 16)
            else:
                action = int(action)

            self._device.bind(args.button, action)
            self._device.save()

        print(self._device.get_bindings())

    def color(self):
        """
        get/set LED colors
        """
        parser = argparse.ArgumentParser()
        parser.add_argument(
            '-l', '--led', type=str, required=False, default=None,
            help='LED to set: all (default), logo, wheel, bottom')
        parser.add_argument(
            '-c', '--color', type=str, required=False, default=None,
            help='Color in hex. HTML format, ex.: aabbcc')
        parser.add_argument(
            '-b', '--brightness', type=int, required=False, default=0,
            help='Brightness: 0 - 4, default is 0')
        parser.add_argument(
            '-m', '--mode', type=str, required=False, default=None,
            help='LED mode: default, breath, rainbow, wave, reactive, flasher, battery')
        args = parser.parse_args()

        if not self._device.leds:
            print("Device does'n have any LEDs")
            return

        if args.led or args.color or args.brightness or args.mode:
            r = 0
            g = 0
            b = 0
            if args.color:
                color = args.color.lstrip('#')
                r = int(args.color[0:2], 16)
                g = int(args.color[2:4], 16)
                b = int(args.color[4:6], 16)

            self._device.set_color(
                args.led or 'all', (r, g, b),
                mode=args.mode or 'default',
                brightness=args.brightness)
            self._device.save()

        print(self._device.get_colors())

    def dpi(self):
        """
        get/set DPI
        """
        parser = argparse.ArgumentParser()
        parser.add_argument(
            '-d', '--dpi', type=int, default=0, required=False,
            help='DPI rate')
        parser.add_argument(
            '-p', '--preset', type=int, default=0, required=False,
            help='Preset no. to set, starting from 1 (default)')
        args = parser.parse_args()

        if not self._device.dpis:
            print('DPI presets are not supported')
            return

        if args.dpi:
            self._device.set_dpi(args.dpi, preset=args.preset or 1)
            self._device.save()

        dpis, rate, response, snapping = self._device.get_dpi_rate_response_snapping()
        for i, dpi in enumerate(dpis, start=1):
            print('DPI Preset {} ({}): {}'.format(i, defs.DPI_PRESET_COLORS[i], dpi))

    def rate(self):
        """
        get/set polling rate
        """
        parser = argparse.ArgumentParser()
        parser.add_argument(
            '-r', '--rate', type=int, default=0, required=False,
            help='Polling rate in Hz: 125, 250, 500, 1000 (default)')
        args = parser.parse_args()

        if args.rate:
            self._device.set_rate(args.rate or 1000)
            self._device.save()

        dpi, rate, response, snapping = self._device.get_dpi_rate_response_snapping()
        print('Polling rate: {} Hz'.format(rate))

    def sleep(self):
        """
        get/set sleep timeout and battery alert level
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

        t, l = self._device.get_sleep_alert()
        print('Sleep: {}'.format('{} min.'.format(t) if t else 'disabled'))
        print('Alert: {}'.format('{}%'.format(l) if l else 'disabled'))

    def snapping(self):
        """
        enable/disable snapping
        """
        parser = argparse.ArgumentParser()
        parser.add_argument(
            '-s', '--snapping', type=int, required=False, default=-1,
            help='Angle snapping: 0 - disabled, 1 - enabled')
        args = parser.parse_args()

        if args.snapping >= 0:
            self._device.set_snapping(bool(args.snapping))
            self._device.save()

        dpis, rate, response, snapping = self._device.get_dpi_rate_response_snapping()
        print('Angle snapping: {}'.format('enabled' if snapping else 'disabled'))

    def response(self):
        """
        get/set button response
        """
        parser = argparse.ArgumentParser()
        parser.add_argument(
            '-r', '--response', type=int, required=False, default=0,
            help='Response in ms: 4, 8, 12, 16, 20, 24, 28, 32')
        args = parser.parse_args()

        if args.response >= 0:
            self._device.set_snapping(bool(args.response))
            self._device.save()

        dpis, rate, response, snapping = self._device.get_dpi_rate_response_snapping()
        print('Button response: {} ms'.format(response))

    def dump(self):
        """
        dump settings to stdout or .json file
        """
        parser = argparse.ArgumentParser()
        parser.add_argument(
            '-o', '--output', type=str, required=False,
            help='Path to .json file for saving to')
        args = parser.parse_args()

        if args.output:
            with open(args.output, 'w') as f:
                self._device.dump(f)
            print('Settings saved into: {}'.format(args.output))
        else:
            print(self._device.dump())

    def load(self):
        """
        load settings from .json file
        """
        parser = argparse.ArgumentParser()
        parser.add_argument(
            'input', type=str, required=True,
            help='Path to .json file for loading from')
        args = parser.parse_args()

        with open(args.input, 'r') as f:
            device.load(f)
        print('Settings loaded from: {}'.format(args.input))


def logging_init():
    if '--debug' in sys.argv:
        sys.argv.pop(sys.argv.index('--debug'))
        logging.basicConfig(
            level=logging.DEBUG,
            format='[%(asctime)s] [%(levelname)s] %(message)s')
        logger.setLevel(logging.DEBUG)


def rogdrv():
    logging_init()
    app = ROGDRV()

    if app.is_console:
        app.run()
    else:
        app.start()

        from .gtk3 import gtk3_main
        gtk3_main(app.device)
        app.device.close()
        app.handler.close()
        app.stop()


def rogdrv_config():
    logging_init()
    app = ROGDRVConfig()
    app.run()
