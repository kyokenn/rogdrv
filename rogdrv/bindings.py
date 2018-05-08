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

import collections

from . import defs


def get_action_type(action):
    if action in defs.ACTIONS_MOUSE:
        return defs.ACTION_TYPE_MOUSE
    else:
        return defs.ACTION_TYPE_KEYBOARD


def get_action_name(action):
    type_ = get_action_type(action)
    if type_ == defs.ACTION_TYPE_MOUSE:
        return defs.ACTIONS_MOUSE[action]
    elif type_ == defs.ACTION_TYPE_KEYBOARD:
        return defs.ACTIONS_KEYBOARD[action]


class Bindings(object):
    def __init__(self):
        self._actions = collections.OrderedDict((
            (1, defs.ACTIONS_MOUSE_NAMES['MOUSE_LEFT']),
            (2, defs.ACTIONS_MOUSE_NAMES['MOUSE_RIGHT']),
            (3, defs.ACTIONS_MOUSE_NAMES['MOUSE_MIDDLE']),
            (4, defs.ACTIONS_MOUSE_NAMES['MOUSE_SCROLL_UP']),
            (5, defs.ACTIONS_MOUSE_NAMES['MOUSE_SCROLL_DOWN']),
            (6, defs.ACTIONS_MOUSE_NAMES['MOUSE_DPI']),
            (7, defs.ACTIONS_MOUSE_NAMES['MOUSE_BACKWARD']),
            (8, defs.ACTIONS_MOUSE_NAMES['MOUSE_FORWARD']),
            (9, defs.ACTIONS_MOUSE_NAMES['MOUSE_BACKWARD']),
            (10, defs.ACTIONS_MOUSE_NAMES['MOUSE_FORWARD']),
        ))

        self._types = collections.OrderedDict()
        for i in range(1, 10+1):
            self._types[i] = defs.ACTION_TYPE_MOUSE

    def bind(self, button, action, type_=None):
        self._actions[button] = action
        self._types[button] = type_ or get_action_type(action)

    def load(self, data):
        if type(data) == dict:
            for i in range(1, 10 + 1):
                action_type = data['action_type_{}'.format(i)]
                if action_type == 'MOUSE':
                    self.bind(
                        i, data['action_code_{}'.format(i)],
                        defs.ACTION_TYPE_MOUSE)
                elif action_type == 'KEYB.':
                    self.bind(
                        i, data['action_code_{}'.format(i)],
                        defs.ACTION_TYPE_KEYBOARD)

        else:
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

    def export(self):
        data = {}
        for k, v in self._actions.items():
            data['action_code_{}'.format(k)] = v
            data['action_name_{}'.format(k)] = get_action_name(v)
        for k, v in self._types.items():
            if v == defs.ACTION_TYPE_MOUSE:
                type_ = 'MOUSE'
            elif v == defs.ACTION_TYPE_KEYBOARD:
                type_ = 'KEYB.'
            else:
                type_ = 'UNKN.'
            data['action_type_{}'.format(k)] = type_
        return data

    def __iter__(self):
        for button, action in self._actions.items():
            yield button, action, self._types[button]

    def __str__(self):
        return '''1 (LEFT):\t[{action_type_1}] {action_name_1} (0x{action_code_1:02X})
2 (RIGHT):\t[{action_type_2}] {action_name_2} (0x{action_code_2:02X})
3 (MIDDLE):\t[{action_type_3}] {action_name_3} (0x{action_code_3:02X})
4 (SCR.UP):\t[{action_type_4}] {action_name_4} (0x{action_code_4:02X})
5 (SCR.DOWN):\t[{action_type_5}] {action_name_5} (0x{action_code_5:02X})
6 (DPI):\t[{action_type_6}] {action_name_6} (0x{action_code_6:02X})
7 (L.BACKWARD):\t[{action_type_7}] {action_name_7} (0x{action_code_7:02X})
8 (L.FORWARD):\t[{action_type_8}] {action_name_8} (0x{action_code_8:02X})
9 (R.BACKWARD):\t[{action_type_9}] {action_name_9} (0x{action_code_9:02X})
10 (R.FORWARD):\t[{action_type_10}] {action_name_10} (0x{action_code_10:02X})
'''.format(**self.export())
