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


ACTIONS_KEYBOARD = {
    0: 'UNDEFINED',
    4: 'KEY_A',
    5: 'KEY_B',
    6: 'KEY_C',
    7: 'KEY_D',
    8: 'KEY_E',
    9: 'KEY_F',
    10: 'KEY_G',
    11: 'KEY_H',
    12: 'KEY_I',
    13: 'KEY_J',
    14: 'KEY_K',
    15: 'KEY_L',
    16: 'KEY_M',
    17: 'KEY_N',
    18: 'KEY_O',
    19: 'KEY_P',
    20: 'KEY_Q',
    21: 'KEY_R',
    22: 'KEY_S',
    23: 'KEY_T',
    24: 'KEY_U',
    25: 'KEY_V',
    26: 'KEY_W',
    27: 'KEY_X',
    28: 'KEY_Y',
    29: 'KEY_Z',
    30: 'KEY_1',
    31: 'KEY_2',
    32: 'KEY_3',
    33: 'KEY_4',
    34: 'KEY_5',
    35: 'KEY_6',
    36: 'KEY_7',
    37: 'KEY_8',
    38: 'KEY_9',
    39: 'KEY_0',
    40: 'KEY_ENTER',
    41: 'KEY_ESC',
    42: 'KEY_BACKSPACE',
    43: 'KEY_TAB',
    44: 'KEY_SPACE',
    45: 'KEY_MINUS',
    46: 'KEY_KPPLUS',
    53: 'KEY_GRAVE',
    54: 'KEY_EQUAL',
    56: 'KEY_SLASH',
    58: 'KEY_F1',
    59: 'KEY_F2',
    60: 'KEY_F3',
    61: 'KEY_F4',
    62: 'KEY_F5',
    63: 'KEY_F6',
    64: 'KEY_F7',
    65: 'KEY_F8',
    66: 'KEY_F9',
    67: 'KEY_F10',
    68: 'KEY_F11',
    69: 'KEY_F12',
    74: 'KEY_HOME',
    75: 'KEY_PAGEUP',
    76: 'KEY_DELETE',
    78: 'KEY_PAGEDOWN',
    79: 'KEY_RIGHT',
    80: 'KEY_LEFT',
    81: 'KEY_DOWN',
    82: 'KEY_UP',
    89: 'KEY_KP1',
    90: 'KEY_KP2',
    91: 'KEY_KP3',
    92: 'KEY_KP4',
    93: 'KEY_KP5',
    94: 'KEY_KP6',
    95: 'KEY_KP7',
    96: 'KEY_KP8',
    97: 'KEY_KP9',
}

ACTIONS_MOUSE = {
    0xF0: 'MOUSE_LEFT',
    0xF1: 'MOUSE_RIGHT',
    0xF2: 'MOUSE_MIDDLE',
    0xE4: 'MOUSE_BACKWARD',
    0xE5: 'MOUSE_FORWARD',
    0xE6: 'MOUSE_DPI',
    0xE7: 'MOUSE_DPI_TARGET',
    0xE8: 'MOUSE_SCROLL_UP',
    0xE9: 'MOUSE_SCROLL_DOWN',
    0xFF: 'MOUSE_DISABLED',
    0xE1: 'MOUSE_BACKWARD_ALT',
    0xE2: 'MOUSE_FORWARD_ALT',
}

ACTIONS_MOUSE_NAMES = {v: k for k, v in ACTIONS_MOUSE.items()}

ACTION_TYPE_KEYBOARD = 0
ACTION_TYPE_MOUSE = 1

EVDEV_PRESS = 1
EVDEV_RELEASE = 0

LED_NAMES = (
    'logo',
    'wheel',
    'bottom',
    'all',
)

LED_MODES = (
    'default',
    'breath',
    'rainbow',
    'wave',
    'reactive',
    'flasher',
    'battery',
)

DPI_PRESET_COLORS = {
    1: 'red',
    2: 'purple',
    3: 'blue',
    4: 'green',
}

POLLING_RATES = {
    0: 125,
    1: 250,
    2: 500,
    3: 1000,
}

BUTTON_SLOTS = {
    1: ACTIONS_MOUSE_NAMES['MOUSE_LEFT'],
    2: ACTIONS_MOUSE_NAMES['MOUSE_RIGHT'],
    3: ACTIONS_MOUSE_NAMES['MOUSE_MIDDLE'],
    4: ACTIONS_MOUSE_NAMES['MOUSE_SCROLL_UP'],
    5: ACTIONS_MOUSE_NAMES['MOUSE_SCROLL_DOWN'],
    6: ACTIONS_MOUSE_NAMES['MOUSE_DPI'],
    7: ACTIONS_MOUSE_NAMES['MOUSE_BACKWARD'],
    8: ACTIONS_MOUSE_NAMES['MOUSE_FORWARD'],
    9: 0xE1,  # right backward
    10: 0xE2,  # right forward
    11: ACTIONS_MOUSE_NAMES['MOUSE_DPI_TARGET'],
}

SLEEP_TIME = {
    0x00: 1,  # 1 minute
    0x01: 2,  # 2 minutes
    0x02: 3,  # 3 minutes
    0x03: 5,  # 5 minutes
    0x04: 10,  # 10 minutes
    0xff: 0,  # don't sleep
}
