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
from .bindings import Bindings, get_button_type
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
        for key in data[3:]:
            if key in defs.KEY_TO_ECODE:
                pressed.add(defs.KEY_TO_ECODE[key])

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
        return self._ctl.read(64, blocking=True)

    def write(self, data):
        self._ctl.write(data)

    def query(self, data):
        self.write(data)
        return self.read()

    def noop(self):
        '''
        Is it noop?
        '''
        request = [0] * 64
        request[0] = 0x50
        request[1] = 0x03
        self.query(bytes(request))

    def get_bindings(self):
        request = [0] * 64
        request[0] = 0x12
        request[1] = 0x05
        response = self.query(bytes(request))
        bindings = Bindings()
        bindings.load(response)
        return bindings

    def bind(self, slot, button):
        request = [0] * 64
        request[0] = 0x51
        request[1] = 0x21
        # mouse button
        request[4] = defs.BUTTON_SLOTS[slot]
        request[5] = defs.BUTTON_TYPE_MOUSE
        # key
        request[6] = button
        request[7] = get_button_type(button)
        self.query(bytes(request))

    def get_colors(self):
        request = [0] * 64
        request[0] = 0x12
        request[1] = 0x03
        response = self.query(bytes(request))

        colors = Colors()
        colors.load(response)
        return colors

    def set_color(self, slot, color):
        '''
        Set LED color.

        :param color: color in format (r, g, b)
        :type color: tuple
        '''
        request = [0] * 64
        request[0] = 0x51
        request[1] = 0x28
        request[2] = 0x03  # mode or slot?
        request[5] = 0x04  # brightness?
        request[6] = color[0]  # r
        request[7] = color[1]  # g
        request[8] = color[2]  # b
        self.query(bytes(request))


class Pugio(Device):
    PRODUCT_ID = 0x1846
