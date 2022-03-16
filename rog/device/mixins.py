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

import struct

from evdev import ecodes

from .. import defs, logger


class DoubleDPIMixin(object):
    """
    Mixin for devices which reports double DPI values.
    """
    def get_dpi_rate_response_snapping(self):
        dpis, rate, bresponse, snapping = super().get_dpi_rate_response_snapping()
        return ([dpi * 2 for dpi in dpis], rate, bresponse, snapping)

    def set_dpi(self, dpi: int, preset=1):
        super().set_dpi(dpi / 2, preset=preset)


class BitmaskMixin(object):
    """
    Mixin for devices with bitmask-encoded keyboard events.
    """
    def next_event(self):
        pressed = set()

        try:
            data = self._kbd.read(256)
        except (OSError, IOError) as e:
            logger.debug(e)
            return pressed

        logger.debug('< ' + ' '.join('{:02X}'.format(i) for i in data))

        # cut bitmask from packet and add zero padding to match 16 bytes length
        bitmask_b = bytes(data[2:2+15] + [0])

        # python's struct doesn't have 16-byte numbers,
        # so we have to use two 8-byte unsigned long long numbers
        low, high = struct.unpack('<QQ', bitmask_b)
        bitmask = low | (high << (8 * 8))

        bitmask_s = '{:0128b}'.format(bitmask)
        logger.debug('got bitmask {}'.format(bitmask_s))
        logger.debug('got bitmask {:032X}'.format(bitmask))

        if bitmask:
            for i, bit in enumerate(reversed(bitmask_s)):  # from low bit to high
                if bit == '1':
                    evdev_name = defs.ACTIONS_KEYBOARD.get(i)
                    if evdev_name and evdev_name != 'UNDEFINED':
                        pressed.add(getattr(ecodes, evdev_name))

        return pressed


class StrixProfileMixin(object):
    """
    Mixin for new profile API introduced in Strix mice.
    """
    def get_profile_version(self):
        logger.debug('getting profile and firmware versions')
        request = [0] * 64
        request[0] = 0x12
        response = self.query(bytes(request))
        profile = response[9] + 1
        ver1 = response[15], response[14], response[13]
        ver2 = response[6], response[5], response[4]
        return profile, ver1, ver2


class BatteryV2Mixin(object):
    """
    Mixin for battery API version 2.
    """
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
