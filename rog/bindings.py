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
    def __init__(self, buttons: int):
        """
        Creates a new Binding storage structure.

        :param buttons: number of buttons available
        :type buttons: int
        """
        # mouse button, action type, action
        DEFAULTS = (
            (1, defs.ACTION_TYPE_MOUSE, defs.ACTIONS_MOUSE_NAMES['MOUSE_LEFT']),
            (2, defs.ACTION_TYPE_MOUSE, defs.ACTIONS_MOUSE_NAMES['MOUSE_RIGHT']),
            (3, defs.ACTION_TYPE_MOUSE, defs.ACTIONS_MOUSE_NAMES['MOUSE_MIDDLE']),
            (4, defs.ACTION_TYPE_MOUSE, defs.ACTIONS_MOUSE_NAMES['MOUSE_SCROLL_UP']),
            (5, defs.ACTION_TYPE_MOUSE, defs.ACTIONS_MOUSE_NAMES['MOUSE_SCROLL_DOWN']),
            (6, defs.ACTION_TYPE_MOUSE, defs.ACTIONS_MOUSE_NAMES['MOUSE_DPI']),
            (7, defs.ACTION_TYPE_MOUSE, defs.ACTIONS_MOUSE_NAMES['MOUSE_BACKWARD']),
            (8, defs.ACTION_TYPE_MOUSE, defs.ACTIONS_MOUSE_NAMES['MOUSE_FORWARD']),
            (9, defs.ACTION_TYPE_MOUSE, defs.ACTIONS_MOUSE_NAMES['MOUSE_BACKWARD']),
            (10, defs.ACTION_TYPE_MOUSE, defs.ACTIONS_MOUSE_NAMES['MOUSE_FORWARD']),
        )

        self._buttons = buttons
        self._actions = collections.OrderedDict(
            (btn, (act, tp)) for (btn, tp, act) in DEFAULTS[:buttons])

    def bind(self, button, action, type_=None):
        """
        Bind mouse button to specified action and action type.

        :param button: button number to bind (1-10)
        :type button: int

        :param action: action to bind
        :type action: int

        :param type_: action type_, leave None to autodetect
        :type type_: int
        """
        self._actions[button] = action, type_ or get_action_type(action)

    def load(self, data):
        for i in range(1, self._buttons + 1):
            action_type = data['action_type_{}'.format(i)]
            if action_type == 'MOUSE':
                self.bind(
                    i, data['action_code_{}'.format(i)],
                    defs.ACTION_TYPE_MOUSE)
            elif action_type == 'KEYB.':
                self.bind(
                    i, data['action_code_{}'.format(i)],
                    defs.ACTION_TYPE_KEYBOARD)

    def export(self):
        data = []

        for btn, (act, tp) in self._actions.items():
            item = {}

            item['code'] = act
            item['name'] = get_action_name(act)

            if tp == defs.ACTION_TYPE_MOUSE:
                item['type'] = 'MOUSE'
            elif tp == defs.ACTION_TYPE_KEYBOARD:
                item['type'] = 'KEYB.'
            else:
                item['type'] = 'UNKN.'

            data.append((str(btn), item))

        return collections.OrderedDict(data)

    def __iter__(self):
        for btn, (act, tp) in self._actions.items():
            yield btn, act, tp

    def __str__(self):
        lines = [
            ' BUTTON               | TYPE  | CODE - ACTION',
            '----------------------|-------|--------------'
        ]

        for btn, item in self.export().items():
            code = defs.BUTTON_SLOTS.get(int(btn), None)

            lines.append('{} {} | {} | 0x{:02X} - {}'.format(
                str(btn).rjust(2),
                defs.ACTIONS_MOUSE.get(code, 'MOUSE_EXTRA').ljust(18),
                item['type'], item['code'], item['name']))

        return '\n'.join(lines)
