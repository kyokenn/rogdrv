# Copyright (C) 2021 Kyoken, kyoken@kyoken.ninja

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

from .base import Device
from .mixins import DoubleDPIMixin, BitmaskMixin, StrixProfileMixin, BatteryV2Mixin

from .. import defs, hid, logger


class Gladius2(Device):
    """
    ROG Gladius II.
    """
    product_id = 0x1845
    profiles = 3
    buttons = 8  # could be 9 buttons? does the "DPI Target Button" counts?
    buttons_mapping = {
        1: 1,
        2: 2,
        3: 3,
        4: 8,
        5: 9,
        6: 6,
        7: 4,
        8: 5,
    }
    leds = 3


class Gladius2Origin(DoubleDPIMixin, Gladius2):
    """
    ROG Gladius II Origin (8 buttons) - wired version, 12k DPI.
    Gladius II without DPI Dedicated Target Button.
    """
    product_id = 0x1877
    buttons = 8


class Gladius2OriginPink(Gladius2Origin):
    """
    ROG Gladius II Origin PNK LTD (8 buttons) - wired version, 12k DPI.
    """
    product_id = 0x18CD


class Gladius3(DoubleDPIMixin, Gladius2):
    """
    ROG Gladius III.
    """
    product_id = 0x197B
    profiles = 5


class Pugio(Device):
    """
    Gladius II based 10 buttons device.
    """
    product_id = 0x1846
    profiles = 3
    buttons = 10
    buttons_mapping = {
        1: 1,
        2: 2,
        3: 3,
        4: 8,
        5: 9,
        6: 6,
        7: 4,
        8: 5,
        9: 10,
        10: 11,
    }
    leds = 3


class PugioGladiusII(Pugio):
    """
    Pugio booted as Gladius II during firmware upgrade.
    Can be rebooted back by replugging USB cable.
    """
    product_id = 0x1851


class StrixCarry(StrixProfileMixin, Device):
    """
    Wireless only device without any LEDs.
    """
    product_id = 0x18B4
    profiles = 3
    buttons = 8
    wireless = True
    keyboard_interface = 2
    control_interface = 1


class StrixImpact(Device):
    product_id = 0x1847
    buttons = 6
    leds = 1
    profiles = 0


class StrixImpactIIWireless(Device):
    """
    Strix Impact II Wireless in wireless mode
    """
    product_id = 0x1949
    wireless = True
    keyboard_interface = 2
    control_interface = 0
    profiles = 3
    buttons = 8
    dpis = 4
    leds = 3


class StrixImpactIIWirelessWired(StrixImpactIIWireless):
    """
    Strix Impact II WIreless with wire connected
    """
    product_id = 0x1947


class StrixImpactIIElectroPunk(Device):
    """
    Strix Impact II Wireless in wireless mode
    """
    product_id = 0x1956
    keyboard_interface = 2
    control_interface = 0
    profiles = 3
    buttons = 8
    dpis = 4
    leds = 3


class Buzzard(Device):
    product_id = 0x1816
    profiles = 3
    buttons = 10


class KerisWireless(BatteryV2Mixin, DoubleDPIMixin, BitmaskMixin, Device):
    """
    Keris Wireless in wireless mode.
    """
    product_id = 0x1960
    profiles = 3
    buttons = 8
    leds = 2
    keyboard_interface = 2
    control_interface = 0
    wireless = True
    dpis = 4


class KerisWirelessWired(KerisWireless):
    """
    Keris Wireless in wired mode.
    """
    product_id = 0x195E


class ChakramWireless(StrixProfileMixin, BatteryV2Mixin, DoubleDPIMixin, BitmaskMixin, Device):
    """
    Chakram Wireless in wireless mode.
    """
    product_id = 0x18E5
    profiles = 3
    buttons = 5
    leds = 3
    keyboard_interface = 2
    control_interface = 0
    wireless = True
    dpis = 4


class ChakramWirelessWired(ChakramWireless):
    """
    Chakram Wireless in wired mode.
    """
    product_id = 0x18E3


class ChakramX(StrixProfileMixin, BatteryV2Mixin, DoubleDPIMixin, BitmaskMixin, Device):
    """
    Chakram Wireless in wireless mode.
    """
    product_id = 0x1A1A
    profiles = 3
    buttons = 5
    leds = 3
    keyboard_interface = 2
    control_interface = 0
    wireless = True
    dpis = 4


class Pugio2(BatteryV2Mixin, Pugio):
    product_id = 0x1906
    profiles = 3
    buttons = 9
    leds = 3
    wireless = True
    control_interface = 0
    keyboard_interface = 2
    dpis = 4


class Pugio2Wired(Pugio2):
    product_id = 0x1908
