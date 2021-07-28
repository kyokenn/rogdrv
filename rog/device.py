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

import json
import logging
import struct

from evdev import uinput, ecodes

from . import defs, hid, logger
from .bindings import Bindings, get_action_type
from .colors import Colors


class EventHandler(object):
    def __init__(self):
        self._uinput = uinput.UInput()
        self._last_pressed = set()

    def handle_event(self, pressed):
        """
        Handle event. Generates regular evdev/uinput events.
        """
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

    def close(self):
        self._uinput.close()


class DeviceNotFound(Exception):
    pass


class DeviceError(Exception):
    pass


class DeviceMeta(type):
    device_classes = []

    def __new__(cls, classname, superclasses, attributedict):
        c = type.__new__(cls, classname, superclasses, attributedict)
        if classname != 'Device':
            cls.device_classes.append(c)
        return c


def get_device():
    for device_class in DeviceMeta.device_classes:
        try:
            return device_class()
        except DeviceNotFound:
            pass


class Device(object, metaclass=DeviceMeta):
    vendor_id = 0x0B05
    profiles = 0
    buttons = 0
    buttons_mapping = {
        1: 1,
        2: 2,
        3: 3,
        4: 7,
        5: 8,
        6: 6,
        7: 4,
        8: 5,
    }
    leds = 0
    wireless = False
    keyboard_interface = 1
    control_interface = 2
    dpis = 2

    def __init__(self):
        logger.debug('searching for device {}'.format(self.__class__.info()))

        subdevices = hid.list_devices(self.vendor_id, self.product_id)
        self._kbd = None
        self._ctl = None

        if len(subdevices):
            logger.debug('found {} subdevices:'.format(len(subdevices)))
            for subdevice in subdevices:
                # print(device)
                # print(dir(device))

                info = ''
                if subdevice['interface_number'] == self.keyboard_interface:
                    info += ' [using as keyboard]'
                    self._kbd = subdevice
                elif subdevice['interface_number'] == self.control_interface:
                    info += ' [using as control]'
                    self._ctl = subdevice

                logger.debug(
                    '{}: {} {} interface {}{}'
                    .format(subdevice['path'].decode(),
                            subdevice['manufacturer_string'],
                            subdevice['product_string'],
                            subdevice['interface_number'],
                            info))
        else:
            logger.debug('0 devices found')

        if not subdevices:
            raise DeviceNotFound()

        if self._ctl is None:
            logger.debug('control subdevice not found')
            raise DeviceNotFound()
        else:
            logger.debug('opening control subdevice')
            self._ctl.open()

        if self._kbd is None:
            logger.debug('keyboard subdevice not found')
        else:
            logger.debug('opening keyboard subdevice')
            self._kbd.open()

    @classmethod
    def info(cls):
        return '{} (VendorID: 0x{:04X}, ProductID: 0x{:04X})'.format(
            cls.__name__, cls.vendor_id, cls.product_id)

    def close(self):
        logger.debug('closing keyboard subdevice')
        self._kbd.close()
        logger.debug('closing control subdevice')
        self._ctl.close()

    def next_event(self):
        """
        Get virtual keyboard event.

        :returns: pressed keys
        :rtype: set
        """
        pressed = set()

        try:
            data = self._kbd.read(256)
        except (OSError, IOError) as e:
            logger.debug(e)
            return pressed

        logger.debug('< ' + ' '.join('{:02X}'.format(i) for i in data))

        # TODO: implement modifiers
        mod = data[1]
        if mod == 1:  # Ctrl
            pass
        elif mod == 2:  # Shift
            pass
        elif mod == 8:  # Win
            pass

        # collect current pressed buttons
        for action in data[3:]:
            evdev_name = defs.ACTIONS_KEYBOARD.get(action)
            if evdev_name and evdev_name != 'UNDEFINED':
                pressed.add(getattr(ecodes, evdev_name))

        return pressed

    def read(self):
        """
        Read data from control subdevice.

        :returns: response data
        :rtype: bytes
        """
        data = self._ctl.read(64)
        logger.debug('< ' + ' '.join('{:02X}'.format(i) for i in data))
        return data

    def write(self, data):
        """
        Write data into control subdevice.

        :param request: request data
        :type request: bytes
        """
        logger.debug('> ' + ' '.join('{:02X}'.format(i) for i in data))
        self._ctl.write(data)

    def query(self, request, strict=True):
        """
        Query the control subdevice.
        Write request to control subdevice then read response from it.

        :param request: request data
        :type request: bytes

        :returns: response data
        :rtype: bytes
        """
        tries = 0
        tries_max = 10

        while tries < tries_max:
            self.write(request)
            response = self.read()

            if response[0] == 0xff and response[1] == 0xaa:
                raise DeviceError()

            if strict and (response[0] != request[0] or response[1] != request[1]):
                tries += 1
                logger.debug('device is in invalid state, retrying ({}/{})'.format(tries, tries_max))
                continue

            break

        else:
            raise DeviceError()

        return response

    def save(self):
        """
        Saves the current changes.
        """
        logger.debug('saving setting')
        request = [0] * 64
        request[0] = 0x50
        request[1] = 0x03
        self.query(bytes(request))

    def fw_write(self, addr: int, block):
        """
        Write firmware block to device.
        Looks like device should be rebooted into boot-mode before the firmware update.
        Reference implementation, dangerous and never tested.
        """
        logger.debug('writing block {:04X}'.format(addr))
        assert len(block) == 16
        request = [0] * 64
        request[0] = 0x50
        request[4] = 0x10
        request[5], request[6] = struct.pack('>H', addr)
        for i, c in enumerate(block):
            request[i + 8] = c
        # request[24] = checksum?
        self.query(bytes(request))

    def get_bindings(self):
        """
        Get buttons binding.

        :returns: bindings object
        :rtype: `class`:rog.bindings.Bindings:
        """
        request = [0] * 64
        request[0] = 0x12
        request[1] = 0x05
        response = self.query(bytes(request))

        bindings = Bindings(self.buttons)
        for btn, idx in self.buttons_mapping.items():
            if btn <= self.buttons:
                bindings.bind(
                    btn,
                    response[idx * 2 + 2],
                    response[idx * 2 + 2 + 1])

        return bindings

    def set_bindings(self, bindings: Bindings):
        """
        Set buttons binding.

        :param bindings: bindings object
        :type bindings: `class`:rog.bindings.Bindings:
        """
        for button, action, type_ in iter(bindings):
            self.bind(button, action)

    def bind(self, button: int, action: int):
        """
        Bind mouse button to an action.

        :param button: button to bind (1-10)
        :type button: int

        :param action: action code
        :type action: int
        """
        request = [0] * 64
        request[0] = 0x51
        request[1] = 0x21

        # mouse button
        request[4] = defs.BUTTON_SLOTS[button]
        request[5] = defs.ACTION_TYPE_MOUSE

        # action
        request[6] = action
        request[7] = get_action_type(action)

        self.query(bytes(request))

    def get_colors(self):
        """
        Get LED colors.

        :returns: colors object
        :rtype: `class`:rog.colors.Colors:
        """
        logger.debug('getting LED colors')

        request = [0] * 64
        request[0] = 0x12
        request[1] = 0x03
        response = self.query(bytes(request))

        colors = Colors(self.leds)
        colors.load(response)
        return colors

    def set_colors(self, colors: Colors):
        """
        Set LED colors.

        :param colors: colors object
        :type colors: `class`:rog.colors.Colors:
        """
        logger.debug('setting LED colors')

        for i, color in enumerate(iter(colors)):
            self.set_color(defs.LEDS[i], color.rgb, color.mode, color.brightness)

    def set_color(self, led: str, color: tuple, mode: str = 'default', brightness: int = 4):
        """
        Set LED color.

        :param led: led name (logo, wheel, bottom, all)
        :type: str

        :param color: color as tuple (r, g, b)
        :type color: tuple

        :param mode: mode (default, breath, rainbow, wave, reactive, flasher)
        :type brightness: str

        :param brightness: brightness level (0-4)
        :type brightness: int
        """
        if brightness not in list(range(5)):
            brightness = 4

        logger.debug(
            'setting LED {} color to rgb({},{},{}) with mode {} and brightness {}'
            .format(name, color[0], color[1], color[2], mode, brightness))

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

    def get_profile_version(self):
        """
        Get profile and firmware version

        :returns: profile number (1-3), primary version, secondary version
        :rtype: tuple
        """
        logger.debug('getting profile and firmware versions')
        request = [0] * 64
        request[0] = 0x12
        response = self.query(bytes(request))
        ver1 = tuple(reversed((response[13], response[14], response[15])))
        ver2 = tuple(reversed((response[4], response[5], response[6])))
        return response[10] + 1, ver1, ver2

    def set_profile(self, profile: int):
        """
        Set profile.

        :param profile: profile number (1-3)
        :type prifile: int
        """
        if profile < 1:
            profile = 1

        if profile > self.profiles:
            profile = 1

        logger.debug('setting profile to {}'.format(profile))

        request = [0] * 64
        request[0] = 0x50
        request[1] = 0x02
        request[2] = profile - 1
        # request[2] = 0x01
        self.query(bytes(request))

    # def get_dpi_preset(self):
    #     """
    #     Get DPI preset.

    #     :returns: preset number (1-4)
    #     :rtype: int
    #     """
    #     logger.debug('getting DPI preset')
    #     request = [0] * 64
    #     request[0] = 0x12
    #     request[1] = 0x01
    #     response = self.query(bytes(request))
    #     return response[4]

    def get_dpi_rate_response_snapping(self):
        """
        Get current DPI, rate and cursor snapping.
        """
        logger.debug('getting DPI and polling rate')
        logger.debug('number of dpi presets: {}'.format(self.dpis))
        request = [0] * 64
        request[0] = 0x12
        request[1] = 0x04
        response = self.query(bytes(request))

        i = 4
        dpis = []
        for _ in range(self.dpis):
            dpis.append(response[i] * 50 + 50)
            i += 2

        rate = defs.POLLING_RATES[response[i]]
        i += 2

        bresponse = (response[i] + 1) * 4
        i += 2

        snapping = bool(response[i])
        i += 2

        return dpis, rate, bresponse, snapping

    def set_dpi(self, dpi: int, preset=1):
        """
        Set DPI.

        :param dpi: DPI
        :type dpi: int

        :param preset: DPI preset (Start from 1)
        :type preset: int
        """
        if preset not in range(1, self.dpis + 1):
            preset = 1

        logger.debug('setting DPI to {} for preset {}'.format(dpi, preset))

        request = [0] * 64
        request[0] = 0x51
        request[1] = 0x31
        request[2] = preset - 1
        request[4] = int((dpi - 50) / 50)
        self.query(bytes(request))

    def set_rate(self, rate: int):
        """
        Set polling rate.

        :param dpi: rate in Hz
        :type dpi: int
        """
        rates = {v: k for k, v in defs.POLLING_RATES.items()}

        logger.debug('setting polling rate to {}'.format(rate))

        request = [0] * 64
        request[0] = 0x51
        request[1] = 0x31
        request[2] = self.dpis + 0x00 # The first entry after dpi settings
        request[4] = rates.get(rate, 0)
        self.query(bytes(request))

    def set_response(self, response: int):
        """
        Set button response.

        :param dpi: response in ms (4, 8, 12, 16, 20, 24, 28, 32)
        :type dpi: int
        """
        rtype = int(round(response / 4))

        logger.debug('setting button response to {} ms'.format(rtype * 4))

        request = [0] * 64
        request[0] = 0x51
        request[1] = 0x31
        request[2] = self.dpis + 0x01
        request[4] = rtype - 1
        self.query(bytes(request))

    def set_snapping(self, enabled: bool):
        """
        Enable/disable angle snapping.

        :param enabled: is enabled?
        :type enabled: bool
        """
        logger.debug('{} angle snapping'.format('enabling' if enabled else 'disabling'))

        request = [0] * 64
        request[0] = 0x51
        request[1] = 0x31
        request[2] = self.dpis + 0x02
        request[4] = 1 if enabled else 0
        self.query(bytes(request))

    def get_sleep_alert(self):
        """
        Get current sleep timeout and battery alert level.

        :returns: sleep timeout in minutes, battery alert level in %
        :rtype: tuple
        """
        logger.debug('getting sleep timeout and battery alert level')
        request = [0] * 64
        request[0] = 0x12
        request[1] = 0x07
        response = self.query(bytes(request))

        # alert level is untested
        defs.SLEEP_TIME[response[4]], response[6] * 25

    def set_sleep_alert(self, t=0, l=0):
        """
        Set sleep timeout in minutes and battery alert level.

        :param t: time in minutes: 0 (don't sleep), 1, 2, 3, 5, 10
        :type t: int

        :param l: battery level: 0% (disabled), 25%, 50%
        :type l: int
        """
        times = {v: k for k, v in defs.SLEEP_TIME.items()}

        logger.debug('setting sleep timeout to {} and alert level to {}'.format(t, l))

        request = [0] * 64
        request[0] = 0x51
        request[1] = 0x37
        request[4] = times.get(t, times[0])
        request[6] = l // 25
        self.query(bytes(request))

    def dump(self, f=None):
        data = {
            'profiles': {},
        }
        saved_profile, _, _ = self.get_profile_version()

        for profile in range(1, self.profiles + 1):
            self.set_profile(profile)

            dpi, rate, response, snapping = self.get_dpi_rate_response_snapping()

            profile_data = {
                'bindings': self.get_bindings().export(),
                'dpi': dpi,
                'rate': rate,
                'response': response,
                'snapping': snapping,
            }

            if self.leds:
                profile_data['colors'] = self.get_colors().export()

            if self.wireless:
                profile_data['sleep'], profile_data['alert'] = self.get_sleep_alert()

            data['profiles'][str(profile)] = profile_data

        self.set_profile(saved_profile)

        if f is not None:
            json.dump(data, f, indent=4)
        else:
            return json.dumps(data, indent=4)

    def load(self, f):
        data = json.load(f)
        saved_profile, _, _ = self.get_profile_version()

        for profile, profile_data in data['profiles'].items():
            self.set_profile(int(profile))

            if 'binding' in profile_data:
                bindings = Bindings(self.buttons)
                bindings.load(profile_data['bindings'])
                self.set_bindings(bindings)

            if 'dpi' in profile_data:
                for i in self.dpis:
                    self.set_dpi(profile_data['dpi'][i], i + 1)

            if 'rate' in profile_data:
                self.set_rate(profile_data['rate'])

            if 'response' in profile_data:
                self.set_response(profile_data['response'])

            if 'snapping' in profile_data:
                self.set_snapping(profile_data['snapping'])

            if 'colors' in profile_data:
                colors = Colors(self.leds)
                colors.load(profile_data['colors'])
                self.set_colors(colors)

            if 'sleep' in profile_data:
                self.set_sleep(profile_data['sleep'])

            self.save()

        self.set_profile(saved_profile)


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

        # python's struct doesn't have 16-byte numbers,
        # so we have to use two 8-byte unsigned long long numbers
        # also we have to add zero padding from 15 to 16 bytes length
        low, high = struct.unpack('<QQ', bytes(data[2:2+15] + [0]))
        bitmask = low | (high << (8 * 8))
        bitmask_s = '{:0128b}'.format(bitmask)
        logger.debug('got bitmask {}'.format(bitmask_s))

        if bitmask:
            for i, c in enumerate(reversed(bitmask_s)):  # from low bit to high
                if c == '1':
                    evdev_name = defs.ACTIONS_KEYBOARD.get(i)
                    if evdev_name and evdev_name != 'UNDEFINED':
                        pressed.add(getattr(ecodes, evdev_name))

        return pressed


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
        logger.debug('getting profile')
        request = [0] * 64
        request[0] = 0x12
        response = self.query(bytes(request))
        ver1 = tuple(reversed((response[12], response[13], response[14])))
        ver2 = tuple(reversed((response[4], response[5], response[6])))
        return response[9] + 1, ver1, ver2


class StrixImpact(Device):
    product_id = 0x1847
    buttons = 6
    leds = 1
    profiles = 0


class StrixImpactII(Device):
    product_id = 0x1947
    keyboard_interface = 2
    control_interface = 0
    profiles = 3
    buttons = 8
    dpis = 4
    leds = 3


class StrixImpactIIWireless(StrixImpactII):
    product_id = 0x1949
    wireless = True


class StrixEvolve(Device):
    product_id = 0x185B
    profiles = 3
    buttons = 8
    leds = 1


class Spatha(Device):
    """
    Spatha on cord.
    """
    product_id = 0x181C
    profiles = 3
    # profiles = 6  # unsupported
    buttons = 10
    # buttons = 14  # unsupported
    leds = 3


class SpathaWireless(Spatha):
    """
    Spatha in wireless mode.
    """
    product_id = 0x1824
    wireless = True


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

    def get_sleep_alert(self):
        logger.debug('getting sleep timeout')
        request = [0] * 64
        request[0] = 0x12
        request[1] = 0x07
        response = self.query(bytes(request))

        return defs.SLEEP_TIME[response[5]], response[6] * 25


class KerisWirelessWired(KerisWireless):
    """
    Keris Wireless in wired mode.
    """
    product_id = 0x195E
