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

import json
import struct

from evdev import ecodes
from .. import defs, hid, logger
from ..bindings import Bindings, get_action_type
from ..leds import LEDs


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
        if self._kbd is not None:
            logger.debug('closing keyboard subdevice')
            self._kbd.close()

        if self._ctl is not None:
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
        except (OSError, IOError, ValueError) as e:
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

    def get_leds(self):
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

        leds = LEDs(self.leds)
        leds.load(response)
        return leds

    def set_leds(self, leds: LEDs):
        """
        Set LED colors.

        :param colors: colors object
        :type colors: `class`:rog.colors.Colors:
        """
        logger.debug('setting LED colors')

        for i, led in enumerate(iter(leds)):
            self.set_color(defs.LED_NAMES[i], led.rgb, led.mode, led.brightness)

    def set_led(self, name: str, color: tuple, mode: str = 'default', brightness: int = 4):
        """
        Set LED color.

        :param name: led name (logo, wheel, bottom, all)
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
        request[2] = defs.LED_NAMES.index(name)
        request[4] = defs.LED_MODES.index(mode)
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
        profile = response[10] + 1
        ver1 = response[15], response[14], response[13]
        ver2 = response[6], response[5], response[4]
        return profile, ver1, ver2

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

    def get_sleep_charge_alert(self):
        """
        Get current sleep timeout, battery charge and alert level.

        :returns: sleep timeout in minutes, battery charge level in %, battery alert level in %
        :rtype: tuple
        """
        logger.debug('getting sleep timeout and battery alert level')
        request = [0] * 64
        request[0] = 0x12
        request[1] = 0x07
        response = self.query(bytes(request))

        sleep = defs.SLEEP_TIME[response[4]]
        alert = response[5] * 25  # alert level need mode testing
        charge = response[6] * 25
        if alert > 50:
            alert = 0
        return sleep, charge, alert

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
                profile_data['colors'] = self.get_leds().export()

            if self.wireless:
                profile_data['sleep'], _, profile_data['alert'] = self.get_sleep_charge_alert()

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

            if 'leds' in profile_data:
                leds = LEDs(self.leds)
                leds.load(profile_data['leds'])
                self.set_leds(leds)

            if 'sleep' in profile_data:
                self.set_sleep(profile_data['sleep'])

            self.save()

        self.set_profile(saved_profile)
