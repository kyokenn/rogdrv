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
