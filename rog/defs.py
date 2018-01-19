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

from evdev import ecodes


EVDEV_PRESS = 1
EVDEV_RELEASE = 0

BUTTON_TYPE_MOUSE = 1
BUTTON_TYPE_KEYBOARD = 0

MOUSE_BUTTONS = {
    'MOUSE_LEFT': 0xF0,
    'MOUSE_RIGHT': 0xF1,
    'MOUSE_MIDDLE': 0xF2,
    'MOUSE_BACKWARD': 0xE4,
    'MOUSE_FORWARD': 0xE5,
    'MOUSE_DPI': 0xE6,
    'MOUSE_SCROLL_UP': 0xE8,
    'MOUSE_SCROLL_DOWN': 0xE9,
}

MOUSE_BUTTONS_NAMES = {v: k for k, v in MOUSE_BUTTONS.items()}

BUTTON_SLOTS = {
    1: MOUSE_BUTTONS['MOUSE_LEFT'],
    2: MOUSE_BUTTONS['MOUSE_RIGHT'],
    3: MOUSE_BUTTONS['MOUSE_MIDDLE'],
    4: MOUSE_BUTTONS['MOUSE_SCROLL_UP'],
    5: MOUSE_BUTTONS['MOUSE_SCROLL_DOWN'],
    6: MOUSE_BUTTONS['MOUSE_DPI'],
    7: MOUSE_BUTTONS['MOUSE_BACKWARD'],
    8: MOUSE_BUTTONS['MOUSE_FORWARD'],
    9: 0xE1,  # right backward
    10: 0xE2,  # right forward
}

KEY_TO_ECODE = {
    4: ecodes.KEY_A,
    5: ecodes.KEY_B,
    6: ecodes.KEY_C,
    7: ecodes.KEY_D,
    8: ecodes.KEY_E,
    9: ecodes.KEY_F,
    10: ecodes.KEY_G,
    11: ecodes.KEY_H,
    12: ecodes.KEY_I,
    13: ecodes.KEY_J,
    14: ecodes.KEY_K,
    15: ecodes.KEY_L,
    16: ecodes.KEY_M,
    17: ecodes.KEY_N,
    18: ecodes.KEY_O,
    19: ecodes.KEY_P,
    20: ecodes.KEY_Q,
    21: ecodes.KEY_R,
    22: ecodes.KEY_S,
    23: ecodes.KEY_T,
    24: ecodes.KEY_U,
    25: ecodes.KEY_V,
    26: ecodes.KEY_W,
    27: ecodes.KEY_X,
    28: ecodes.KEY_Y,
    29: ecodes.KEY_Z,
    30: ecodes.KEY_1,
    31: ecodes.KEY_2,
    32: ecodes.KEY_3,
    33: ecodes.KEY_4,
    34: ecodes.KEY_5,
    35: ecodes.KEY_6,
    36: ecodes.KEY_7,
    37: ecodes.KEY_8,
    38: ecodes.KEY_9,
    39: ecodes.KEY_0,
    40: ecodes.KEY_ENTER,
    41: ecodes.KEY_ESC,
    42: ecodes.KEY_BACKSPACE,
    43: ecodes.KEY_TAB,
    44: ecodes.KEY_SPACE,
    45: ecodes.KEY_MINUS,
    46: ecodes.KEY_KPPLUS,
    53: ecodes.KEY_GRAVE,
    54: ecodes.KEY_EQUAL,
    56: ecodes.KEY_SLASH,
    58: ecodes.KEY_F1,
    59: ecodes.KEY_F2,
    60: ecodes.KEY_F3,
    61: ecodes.KEY_F4,
    62: ecodes.KEY_F5,
    63: ecodes.KEY_F6,
    64: ecodes.KEY_F7,
    65: ecodes.KEY_F8,
    66: ecodes.KEY_F9,
    67: ecodes.KEY_F10,
    68: ecodes.KEY_F11,
    69: ecodes.KEY_F12,
    74: ecodes.KEY_HOME,
    75: ecodes.KEY_PAGEUP,
    76: ecodes.KEY_DELETE,
    78: ecodes.KEY_PAGEDOWN,
    79: ecodes.KEY_RIGHT,
    80: ecodes.KEY_LEFT,
    81: ecodes.KEY_DOWN,
    82: ecodes.KEY_UP,
    89: ecodes.KEY_KP1,
    90: ecodes.KEY_KP2,
    91: ecodes.KEY_KP3,
    92: ecodes.KEY_KP4,
    93: ecodes.KEY_KP5,
    94: ecodes.KEY_KP6,
    95: ecodes.KEY_KP7,
    96: ecodes.KEY_KP8,
    97: ecodes.KEY_KP9,
}

ECODE_TO_KEY = {ecode: key for key, ecode in KEY_TO_ECODE.items()}
