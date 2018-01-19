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

from . import defs


def get_button_type(button):
    if button in defs.MOUSE_BUTTONS_NAMES:
        return defs.BUTTON_TYPE_MOUSE
    else:
        return defs.BUTTON_TYPE_KEYBOARD


def get_button_name(button):
    type_ = get_button_type(button)
    if type_ == defs.BUTTON_TYPE_MOUSE:
        return defs.MOUSE_BUTTONS_NAMES[button]
    elif type_ == defs.BUTTON_TYPE_KEYBOARD:
        return defs.KEY_TO_ECODE[button]


class Bindings(object):
    def __init__(self):
        self._buttons = {
            1: defs.MOUSE_BUTTONS['MOUSE_LEFT'],
            2: defs.MOUSE_BUTTONS['MOUSE_RIGHT'],
            3: defs.MOUSE_BUTTONS['MOUSE_MIDDLE'],
            4: defs.MOUSE_BUTTONS['MOUSE_SCROLL_UP'],
            5: defs.MOUSE_BUTTONS['MOUSE_SCROLL_DOWN'],
            6: defs.MOUSE_BUTTONS['MOUSE_DPI'],
            7: defs.MOUSE_BUTTONS['MOUSE_BACKWARD'],
            8: defs.MOUSE_BUTTONS['MOUSE_FORWARD'],
            9: defs.MOUSE_BUTTONS['MOUSE_BACKWARD'],
            10: defs.MOUSE_BUTTONS['MOUSE_FORWARD'],
        }

        self._types = {
            i: defs.BUTTON_TYPE_MOUSE for i in range(1, 10+1)
        }

    def bind(self, slot, button, type_=None):
        self._buttons[slot] = button
        self._types[slot] = type_ or get_button_type(button)

    def load(self, data):
        self.bind(1, data[4], data[5])
        self.bind(2, data[6], data[7])
        self.bind(3, data[8], data[9])
        self.bind(7, data[10], data[11])
        self.bind(8, data[12], data[13])
        self.bind(6, data[14], data[15])
        self.bind(4, data[18], data[19])
        self.bind(5, data[20], data[21])
        self.bind(9, data[22], data[23])
        self.bind(10, data[24], data[25])

    def __str__(self):
        data = {}
        for k, v in self._buttons.items():
            data['b{}'.format(k)] = get_button_name(v)
            data['c{}'.format(k)] = v

        for k, v in self._types.items():
            if v == defs.BUTTON_TYPE_MOUSE:
                data['t{}'.format(k)] = 'MOUSE'
            elif v == defs.BUTTON_TYPE_KEYBOARD:
                data['t{}'.format(k)] = 'KEYBOARD'
            else:
                data['t{}'.format(k)] = 'UNKNOWN'

        return '''1 (LEFT):\t[{t1}]\t{b1} (0x{c1:02X})
2 (RIGHT):\t[{t2}]\t{b2} (0x{c2:02X})
3 (MIDDLE):\t[{t3}]\t{b3} (0x{c3:02X})
4 (SCR.up):\t[{t4}]\t{b4} (0x{c4:02X})
5 (SCR.down):\t[{t5}]\t{b5} (0x{c5:02X})
6 (DPI):\t[{t6}]\t{b6} (0x{c6:02X})
7 (L.BACKWARD):\t[{t7}]\t{b7} (0x{c7:02X})
8 (L.FORWARD):\t[{t8}]\t{b8} (0x{c8:02X})
9 (R.BACKWARD):\t[{t9}]\t{b9} (0x{c9:02X})
10 (R.FORWARD):\t[{t10}]\t{b10} (0x{c10:02X})
'''.format(**data)
