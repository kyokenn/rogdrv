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

        if bitmask:
            for i, bit in enumerate(reversed(bitmask_s)):  # from low bit to high
                if bit == '1':
                    evdev_name = defs.ACTIONS_KEYBOARD.get(i)
                    if evdev_name and evdev_name != 'UNDEFINED':
                        pressed.add(getattr(ecodes, evdev_name))

        return pressed
