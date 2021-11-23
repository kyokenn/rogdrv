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
from .mixins import DoubleDPIMixin, BitmaskMixin

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


class StrixCarry(Device):
    """
    Wireless only device without any LEDs.
    """
    product_id = 0x18B4
    profiles = 3
    buttons = 8
    wireless = True
    keyboard_interface = 2
    control_interface = 1

    def get_profile_version(self):
        logger.debug('getting profile and firmware versions')
        request = [0] * 64
        request[0] = 0x12
        response = self.query(bytes(request))
        profile = response[9] + 1
        ver1 = response[15], response[14], response[13]
        ver2 = response[6], response[5], response[4]
        return profile, ver1, ver2


class StrixImpact(Device):
    product_id = 0x1847
    buttons = 6
    leds = 1
    profiles = 0


class StrixImpactIIWirelessWired(Device):
    """
    Strix Impact II WIreless with wire connected
    """
    product_id = 0x1947
    wireless = True
    keyboard_interface = 2
    control_interface = 0
    profiles = 3
    buttons = 8
    dpis = 4
    leds = 3


class StrixImpactIIWireless(StrixImpactIIWirelessWired):
    """
    Strix Impact II Wireless in wireless mode
    """
    product_id = 0x1949


class Buzzard(Device):
    product_id = 0x1816
    profiles = 3
    buttons = 10


class KerisWireless(DoubleDPIMixin, BitmaskMixin, Device):
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

    def get_sleep_charge_alert(self):
        logger.debug('getting sleep timeout, battery charge and alert level')
        request = [0] * 64
        request[0] = 0x12
        request[1] = 0x07
        response = self.query(bytes(request))

        charge = response[4] * 25
        sleep = defs.SLEEP_TIME[response[5]]
        alert = response[6] * 25
        return sleep, charge, alert


class KerisWirelessWired(KerisWireless):
    """
    Keris Wireless in wired mode.
    """
    product_id = 0x195E
