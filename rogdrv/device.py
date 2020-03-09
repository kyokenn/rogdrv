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
import hidapi
import logging

from evdev import uinput, ecodes

from . import defs
from .bindings import Bindings, get_action_type
from .colors import Colors

logger = logging.getLogger('rogdrv')


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

    def __init__(self):
        logger.debug('searching for device {}'.format(self.__class__.info()))

        devices = tuple(hidapi.enumerate(
            vendor_id=self.vendor_id,
            product_id=self.product_id))

        if len(devices):
            logger.debug('found {} subdevices:'.format(len(devices)))
            for device in devices:
                # print(device)
                # print(dir(device))
                # x = 'interface_number', 'manufacturer_string', 'path', 'product_id', 'product_string', 'release_number', 'serial_number', 'usage', 'usage_page', 'vendor_id'
                # for i in x:
                #     print(i, getattr(device, i))

                interface = ''
                if device.interface_number == self.keyboard_interface:
                    interface = ' [using as keyboard]'
                elif device.interface_number == self.control_interface:
                    interface = ' [using as control]'

                logger.debug(
                    '{}: {} {} interface {}{}'
                    .format(device.path.decode(), device.manufacturer_string,
                            device.product_string, device.interface_number,
                            interface))
        else:
            logger.debug('0 devices found')

        if not devices:
            raise DeviceNotFound()

        # keyboard subdevice
        kbd_info = next(filter(
            lambda x: x.interface_number == self.keyboard_interface, devices), None)

        # control subdevice
        ctl_info = next(filter(
            lambda x: x.interface_number == self.control_interface, devices), None)

        logger.debug('opening keyboard subdevice')
        self._kbd = hidapi.Device(kbd_info)
        logger.debug('opening control subdevice')
        self._ctl = hidapi.Device(ctl_info)

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
        data = self._kbd.read(256, blocking=True)

        # TODO: implement modifiers
        mod = data[1]
        if mod == 1:  # Ctrl
            pass
        elif mod == 2:  # Shift
            pass
        elif mod == 8:  # Win
            pass

        # collect current pressed buttons
        pressed = set()
        for action in data[3:]:
            if action in defs.ACTIONS_KEYBOARD:
                evdev_name = defs.ACTIONS_KEYBOARD[action]
                pressed.add(getattr(ecodes, evdev_name))

        return pressed

    def read(self):
        """
        Read data from control subdevice.

        :returns: response data
        :rtype: bytes
        """
        data = self._ctl.read(64, blocking=True)
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

    def query(self, request):
        """
        Query the control subdevice.
        Write request to control subdevice then read response from it.

        :param request: request data
        :type request: bytes

        :returns: response data
        :rtype: bytes
        """
        self.write(request)
        response = self.read()

        if response[0] == 0xff and response[1] == 0xaa:
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

        colors = Colors()
        colors.load(response)
        return colors

    def set_colors(self, colors: Colors):
        """
        Set LED colors.

        :param colors: colors object
        :type colors: `class`:rog.colors.Colors:
        """
        logger.debug('setting LED colors')

        for color, r, g, b, brightness in iter(colors):
            for led_name, led_id in defs.LED_NAMES.items():
                if led_id == color + 1:
                    self.set_color(led_name, (r, g, b), brightness=brightness)

    def set_color(self, name, color, mode='default', brightness=4):
        """
        Set LED color.

        :param name: led name (logo, wheel, bottom, all)
        :type: str

        :param color: color in format (r, g, b)
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

    def get_profile(self):
        """
        Get profile.

        :returns: profile number (1-3)
        :rtype: int
        """
        logger.debug('getting profile')
        request = [0] * 64
        request[0] = 0x12
        response = self.query(bytes(request))
        return response[10] + 1

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

    def get_dpi_rate_response_snapping(self):
        """
        Get current DPI and rate.
        """
        logger.debug('getting DPI and polling rate')
        request = [0] * 64
        request[0] = 0x12
        request[1] = 0x04
        response = self.query(bytes(request))

        dpi1 = response[4] * 50 + 50  # DPI preset 1
        dpi2 = response[6] * 50 + 50  # DPI preset 2
        rate = defs.POLLING_RATES[response[8]]
        bresponse = (response[10] + 1) * 4
        snapping = response[12] + 1
        return dpi1, dpi2, rate, bresponse, snapping

    def set_dpi(self, dpi: int, preset=1):
        """
        Set DPI.

        :param dpi: DPI
        :type dpi: int

        :param preset: DPI preset (1 or 2)
        :type preset: int
        """
        if preset not in (1, 2):
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
        request[2] = 0x02
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
        request[2] = 0x03
        request[4] = rtype - 1
        self.query(bytes(request))

    def set_snapping(self, stype: int):
        """
        Set angle snapping type.

        :param stype: snapping type (1 or 2)
        :type stype: int
        """
        if stype not in (1, 2):
            stype = 1

        logger.debug('setting angle snapping type to {}'.format(stype))

        request = [0] * 64
        request[0] = 0x51
        request[1] = 0x31
        request[2] = 0x04
        request[4] = stype - 1
        self.query(bytes(request))

    def get_sleep(self):
        """
        Get current sleep timeout.
        """
        logger.debug('getting sleep timeout')
        request = [0] * 64
        request[0] = 0x12
        request[1] = 0x07
        response = self.query(bytes(request))

        return defs.SLEEP_TIME[response[4]]

    def set_sleep(self, t=0):
        """
        Set sleep timeout in minutes.

        :param t: time in minutes: 0 (don't sleep), 1, 2, 3, 5, 10
        :type t: int
        """
        times = {v: k for k, v in defs.SLEEP_TIME.items()}

        logger.debug('setting sleep timeout to {}'.format(t))

        request = [0] * 64
        request[0] = 0x51
        request[1] = 0x37
        request[4] = times.get(t, times[0])
        self.query(bytes(request))

    def dump(self, f=None):
        data = {}
        saved_profile = self.get_profile()

        for profile in range(1, self.profiles + 1):
            self.set_profile(profile)

            dpi1, dpi2, rate, response, snapping = self.get_dpi_rate_response_snapping()

            profile_data = {
                'bindings': self.get_bindings().export(),
                'dpi': [dpi1, dpi2],
                'rate': rate,
                'response': response,
                'snapping': snapping,
            }

            if self.leds:
                profile_data['colors'] = self.get_colors().export()

            if self.wireless:
                profile_data['sleep'] = self.get_sleep()

            data[str(profile)] = profile_data

        self.set_profile(saved_profile)

        if f is not None:
            json.dump(data, f, indent=4)
        else:
            return json.dumps(data, indent=4)

    def load(self, f):
        data = json.load(f)
        saved_profile = self.get_profile()

        for profile, profile_data in data.items():
            self.set_profile(int(profile))

            if 'binding' in profile_data:
                bindings = Bindings(self.buttons)
                bindings.load(profile_data['bindings'])
                self.set_bindings(bindings)

            if 'dpi' in profile_data:
                self.set_dpi(profile_data['dpi'][0], 1)
                self.set_dpi(profile_data['dpi'][1], 2)

            if 'rate' in profile_data:
                self.set_rate(profile_data['rate'])

            if 'response' in profile_data:
                self.set_response(profile_data['response'])

            if 'snapping' in profile_data:
                self.set_snapping(profile_data['snapping'])

            if 'colors' in profile_data:
                colors = Colors()
                colors.load(profile_data['colors'])
                self.set_colors(colors)

            if 'sleep' in profile_data:
                self.set_sleep(profile_data['sleep'])

            self.save()

        self.set_profile(saved_profile)


class Gladius2(Device):
    """
    ROG Gladius II Origin
    """
    product_id = 0x1877
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


class Pugio(Device):
    """
    Gladius (8 buttons) based device with extra 2 buttons (10 buttons total).
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

    def get_profile(self):
        # logger.debug('getting profile')
        request = [0] * 64
        request[0] = 0x12
        response = self.query(bytes(request))
        return response[9] + 1


class StrixImpact(Device):
    product_id = 0x1847
    buttons = 6
    leds = 1


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
    wireless = True


class SpathaWireless(Spatha):
    """
    Spatha in wireless mode.
    """
    product_id = 0x1824


class Buzzard(Device):
    product_id = 0x1816
    profiles = 3
    buttons = 10
