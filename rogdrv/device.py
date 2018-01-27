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

import hidapi

from evdev import uinput, ecodes

from . import defs
from .bindings import Bindings, get_action_type
from .colors import Colors


class Device(object):
    VENDOR_ID = 0x0b05

    def __init__(self):
        devices = hidapi.enumerate(
            vendor_id=self.VENDOR_ID,
            product_id=self.PRODUCT_ID)

        # keyboard subdevice
        kbd_info = next(filter(
            lambda x: x.interface_number == 1, devices), None)
        # control subdevice
        ctl_info = next(filter(
            lambda x: x.interface_number == 2, devices), None)

        self._kbd = hidapi.Device(kbd_info)
        self._ctl = hidapi.Device(ctl_info)

        self._uinput = uinput.UInput()
        self._last_pressed = set()

    def next_event(self):
        '''
        Get virtual keyboard event.

        :returns: pressed keys
        :rtype: set
        '''
        data = self._kbd.read(256, blocking=True)
        # print(list(data))

        # TODO: implement modifiers
        mod = data[1]
        if mod == 1:  # Ctrl
            pass
        elif mod == 2:  # Shift
            pass
        elif mod == 8:  # Win
            pass

        # collect current pressed buttons
        pressed = set()
        for action in data[3:]:
            if action in defs.ACTIONS_KEYBOARD:
                evdev_name = defs.ACTIONS_KEYBOARD[action]
                pressed.add(getattr(ecodes, evdev_name))

        return pressed

    def handle_event(self, pressed):
        '''
        Handle event. Generates regular evdev/uinput events.
        '''
        # release buttons
        released = self._last_pressed - pressed
        for code in released:
            self._uinput.write(ecodes.EV_KEY, code, defs.EVDEV_RELEASE)
        self._last_pressed -= released

        # press buttons
        new_pressed = pressed - self._last_pressed
        for code in new_pressed:
            self._uinput.write(ecodes.EV_KEY, code, defs.EVDEV_PRESS)
        self._last_pressed |= new_pressed

        # sync
        if released or new_pressed:
            self._uinput.syn()

    def read(self):
        '''
        Read data from control subdevice.
        '''
        return self._ctl.read(64, blocking=True)

    def write(self, data):
        '''
        Read data into control subdevice.
        '''
        self._ctl.write(data)

    def query(self, data):
        '''
        Query (write then read) control subdevice.
        '''
        self.write(data)
        return self.read()

    def save(self):
        '''
        Saves the current changes.
        '''
        request = [0] * 64
        request[0] = 0x50
        request[1] = 0x03
        self.query(bytes(request))

    def get_bindings(self):
        '''
        Get button bindings.

        :returns: bindings object
        :rtype: `class`:rog.bindings.Bindings:
        '''
        request = [0] * 64
        request[0] = 0x12
        request[1] = 0x05
        response = self.query(bytes(request))
        bindings = Bindings()
        bindings.load(response)
        return bindings

    def bind(self, button, action):
        '''
        Bind button to an action.

        :param button: button to bind (1-10)
        :type button: int

        :param action: action code
        :type action: int
        '''
        request = [0] * 64
        request[0] = 0x51
        request[1] = 0x21
        # mouse button
        request[4] = defs.BUTTON_SLOTS[button]
        request[5] = defs.ACTION_TYPE_MOUSE
        # key
        request[6] = action
        request[7] = get_action_type(action)
        self.query(bytes(request))

    def get_colors(self):
        '''
        Get LED colors.

        :returns: colors object
        :rtype: `class`:rog.colors.Colors:
        '''
        request = [0] * 64
        request[0] = 0x12
        request[1] = 0x03
        response = self.query(bytes(request))

        colors = Colors()
        colors.load(response)
        return colors

    def set_color(self, name, color, mode='default', brightness=4):
        '''
        Set LED color.

        :param name: led name (logo, wheel, bottom, all)
        :type: str

        :param color: color in format (r, g, b)
        :type color: tuple

        :param mode: mode (default, breath, rainbow, wave, reactive, flasher)
        :type brightness: str

        :param brightness: brightness level (0-4)
        :type brightness: int
        '''
        if brightness not in list(range(5)):
            brightness = 0

        request = [0] * 64
        request[0] = 0x51
        request[1] = 0x28
        request[2] = defs.LED_NAMES[name]
        request[4] = defs.LED_MODES[mode]
        request[5] = brightness
        request[6] = color[0]  # r
        request[7] = color[1]  # g
        request[8] = color[2]  # b
        self.query(bytes(request))

    def switch_profile(self, profile):
        '''
        Switch profile.

        :param profile: profile number
        :type prifile: int
        '''
        if profile not in (1, 2, 3):
            profile = 1

        request = [0] * 64
        request[0] = 0x50
        request[1] = 0x02
        request[2] = profile - 1
        # request[2] = 0x01
        self.query(bytes(request))

    def get_dpi_rate(self):
        '''
        Get current DPI and rate.
        '''
        request = [0] * 64
        request[0] = 0x12
        request[1] = 0x04
        response = self.query(bytes(request))

        dpi1 = response[4] * 50 + 50
        dpi2 = response[6] * 50 + 50
        rate = defs.POLLING_RATES[response[8]]
        undef = response[10]
        return dpi1, dpi2, rate, undef

    def set_dpi(self, dpi, type_=1):
        '''
        Set DPI.

        :param dpi: DPI
        :type dpi: int

        :param type_: DPI type (1 or 2)
        :type type_: int
        '''
        if type_ not in (1, 2):
            type_ = 1

        request = [0] * 64
        request[0] = 0x51
        request[1] = 0x31
        request[2] = type_ - 1
        request[4] = int((dpi - 50) / 50)
        self.query(bytes(request))

    def set_rate(self, rate):
        '''
        Set polling rate.

        :param dpi: rate in Hz
        :type dpi: int
        '''
        rates = {v: k for k, v in defs.POLLING_RATES.items()}

        request = [0] * 64
        request[0] = 0x51
        request[1] = 0x31
        request[2] = 0x02
        request[4] = rates.get(rate, 0)
        self.query(bytes(request))


class Pugio(Device):
    PRODUCT_ID = 0x1846
