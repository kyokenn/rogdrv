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

import os
import signal
import sys
import threading
import logging

from . import defs
from .device import EventHandler, get_device

logger = logging.getLogger('rogdrv')


def rogdrv():
    '''
    Virtual uinput device driver which converts mouse events
    into uinput events.
    '''
    if '--help' in sys.argv:
        print('''Usage: rogdrv [--console]
  --help       - display help
  --console    - starts in pure console mode, disables tray icon
''')
        return

    device = get_device()
    handler = EventHandler()

    def loop():
        while True:
            e = device.next_event()
            handler.handle_event(e)

    if '--console' in sys.argv:
        loop()
    else:
        from .gtk3 import gtk3_main
        thread = threading.Thread(target=loop)
        thread.start()
        gtk3_main(device)
        device.close()
        handler.close()
        os.kill(os.getpid(), signal.SIGTERM)


def rogdrv_config():
    """
    Mouse configuration tool.
    """
    args = list(sys.argv)

    if '--debug' in args:
        args.pop(args.index('--debug'))
        # logging.basicConfig(
        #     level=logging.DEBUG,
        #     format='[%(asctime)s] [%(levelname)s] %(message)s')
        formatter = logging.Formatter('[%(asctime)s] [%(levelname)s] %(message)s')
        handler = logging.StreamHandler(sys.stdout)
        handler.setFormatter(formatter)
        handler.setLevel(logging.DEBUG)
        logger.addHandler(handler)
        logger.setLevel(logging.DEBUG)

    # from .device import StrixCarry
    # device = StrixCarry()
    # request = [0] * 64
    # request[0] = 0x12
    # # request[1] = 0x00
    # request[1] = 0x07
    # print(list(device.query(bytes(request))))
    # print(''.join(
    #     '{:02x}'.format(i)
    #     for i in device.query(bytes(request))))
    # return

    if len(args) >= 2:
        if args[1] == 'actions':
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

            return

        elif args[1] == 'bind':
            device = get_device()
            if not device:
                print('Device not found')
                return

            if len(args) >= 4:
                button = int(args[2].lstrip('0'))
                action = args[3].lower()
                if action.startswith('0x'):
                    action = int(action, 16)
                else:
                    action = int(action)
                device.bind(button, action)
                device.save()

            # print('Bindings:')
            print(device.get_bindings())
            return

        elif args[1] == 'color':
            device = get_device()
            if not device:
                print('Device not found')
                return

            if not device.leds:
                print("Device does'n have any LEDs")
                return

            if len(args) >= 6:
                name = args[2]

                r = int(args[3])
                g = int(args[4])
                b = int(args[5])

                if len(args) >= 7:
                    mode = args[6]
                else:
                    mode = 'default'

                if len(args) >= 8:
                    brightness = int(args[7])
                else:
                    brightness = 4

                device.set_color(
                    name, (r, g, b), mode=mode, brightness=brightness)
                device.save()

            print(device.get_colors())
            return

        elif args[1] == 'profile':
            device = get_device()
            if not device:
                print('Device not found')
                return

            if not device.profiles:
                print('Profiles not supported')
                return

            if len(args) >= 3:
                device.set_profile(int(args[2]))

            profile = device.get_profile()
            print('Profile: {}'.format(profile))
            return

        elif args[1] == 'sleep':
            device = get_device()
            if not device:
                print('Device not found')
                return

            if not device.wireless:
                print('Device is not wireless')
                return

            if len(args) >= 3:
                device.set_sleep(int(args[2]))

            t = device.get_sleep()
            if t:
                print('Sleep: {} min.'.format(t))
            else:
                print('Sleep: disabled')
            return

        elif args[1] == 'dpi':
            device = get_device()
            if not device:
                print('Device not found')
                return

            if len(args) >= 3:
                if len(args) >= 4:
                    preset = int(args[3])
                else:
                    preset = 1

                device.set_dpi(int(args[2]), preset=preset)
                device.save()

            dpi1, dpi2, rate, response, snapping = device.get_dpi_rate_response_snapping()
            print('DPI Preset 1: {}'.format(dpi1))
            print('DPI Preset 2: {}'.format(dpi2))
            return

        elif args[1] == 'rate':
            device = get_device()
            if not device:
                print('Device not found')
                return

            if len(args) >= 3:
                device.set_rate(int(args[2]))
                device.save()

            dpi1, dpi2, rate, response, snapping = device.get_dpi_rate_response_snapping()
            print('Polling rate: {} Hz'.format(rate))
            return

        elif args[1] == 'response':
            device = get_device()
            if not device:
                print('Device not found')
                return

            if len(args) >= 3:
                device.set_response(int(args[2]))
                device.save()

            dpi1, dpi2, rate, response, snapping = device.get_dpi_rate_response_snapping()
            print('Button response: {} ms'.format(response))
            return

        elif args[1] == 'snapping':
            device = get_device()
            if not device:
                print('Device not found')
                return

            if len(args) >= 3:
                device.set_snapping(int(args[2]))
                device.save()

            dpi1, dpi2, rate, response, snapping = device.get_dpi_rate_response_snapping()
            print('Snapping angle: type {}'.format(snapping))
            return

        elif args[1] == 'dump':
            device = get_device()
            if not device:
                print('Device not found')
                return

            if len(args) >= 3:
                with open(args[2], 'w') as f:
                    device.dump(f)
                print('Settings saved into: {}'.format(args[2]))
            else:
                print(device.dump())

            return

        elif args[1] == 'load':
            device = get_device()
            if not device:
                print('Device not found')
                return

            if len(args) >= 3:
                with open(args[2], 'r') as f:
                    device.load(f)

            print('Settings loaded from: {}'.format(args[2]))
            return

        elif args[1] == '--help':
            print('''Usage:
  rogdrv-config --help                            - displays help
  rogdrv-config --debug                           - enables debug mode

  rogdrv-config actions                           - display list of available actions

  rogdrv-config profile [value]                   - get/set profile
    value: profile no. (1-3)

  rogdrv-config bind [button action]              - bind a button or display bindings
    button: button no. (1-99)
    action: action code (241 or 0xF1 or 0xf1)

  rogdrv-config dpi [value [preset]]              - get/set DPI
    value: DPI (50-7200)
    preset: 1 (default) or 2

  rogdrv-config rate [hz]                         - get/set polling rate
    hz: rate in Hz (125, 250, 500, 1000)

  rogdrv-config response [ms]                     - get/set buttons response
    ms: response in ms (4, 8, 12, 16, 20, 24, 28, 32)

  rogdrv-config snapping [type]                   - get/set angle snapping type
    type: angle snapping type (1 or 2)

  rogdrv-config color [name r g b [mode] [brght]] - get/set LED colors
    name: logo, wheel, bottom, all
    r: red (0-255)
    g: green (0-255)
    b: blue (0-255)
    mode: default, breath, rainbow, wave, reactive, flasher
    brght: brightness 0-4 (default-4)

  rogdrv-config sleep [value]                     - get/set sleep timeout
    value: timeout in minutes (0-disabled, 1, 2, 3, 5, 10)

  rogdrv-config dump [file]                       - save settings into file
    file: path to json file

  rogdrv-config load file                         - load settings from file
    file: path to json file
''')
            return

    print('Got nothing to do.')
    print("Try 'rogdrv-config --help' for more information.")
