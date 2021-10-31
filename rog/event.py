from evdev import uinput, ecodes, _ecodes
from inspect import getmembers
from . import defs

class DeviceEventHandler(object):
    """
    Mouse event handler.
    Converts mouse events to evdev/uinput events.
    """
    def __init__(self):
        # TODO: change codes[val] = val to something correct in Python...
        codes = {}
        for code, val in getmembers(_ecodes):
            if code.startswith("KEY"):
                if (val >= ecodes.ecodes['KEY_ESC'] and val <= ecodes.ecodes['KEY_MEDIA']) or val == ecodes.ecodes['KEY_FN']:
                    codes[val] = val
            elif code.startswith("BTN"):
                if (val >= ecodes.ecodes['BTN_LEFT'] and val <= ecodes.ecodes['BTN_TASK']):
                    codes[val] = val

        event = {ecodes.EV_KEY: codes.keys()}
        self._uinput = uinput.UInput(events=event)
        self._last_pressed = set()

    def handle_event(self, pressed: set):
        """
        Handle mouse event. Generates regular evdev/uinput events.

        :param pressed: set of pressed keys
        :type pressed: set
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
