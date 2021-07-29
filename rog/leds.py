import copy

from . import defs


DEFAULT_COLORS = {
    1: (255, 0, 0),
    2: (0, 255, 0),
    3: (0, 0, 255),
}


class LED(object):
    def __init__(self, r: int, g: int, b: int, brightness: int, mode: str):
        self.r = r
        self.g = g
        self.b = b
        self.brightness = brightness
        self.mode = mode

    @property
    def rgb(self):
        return (self.r, self.g, self.b)

    @property
    def hex(self):
        return '{:02X}{:02X}{:02X}'.format(*self.rgb)


class LEDs(object):
    def __init__(self, count):
        self._leds = [None] * count
        for i in range(self.count):
            r, g, b = DEFAULT_COLORS[i + 1]
            self._leds[i] = LED(r, g, b, 4, 'default')

    @property
    def count(self):
        return len(self._leds)

    def load(self, data):
        if isinstance(data, dict):  # load from json settings backup
            self._leds = [None] * len(tuple(data.keys()))
            for led, item in data.items():
                self._leds[defs.LED_NAMES.index(led)] = Color(
                    item['r'], item['g'], item['b'],
                    item['brightness'],
                    item['mode'])

        else:  # load from device
            off = 4
            for i in range(self.count):
                mode = defs.LED_MODES[data[off]]
                off += 1
                brightness = data[off]
                off += 1
                r = data[off]
                off += 1
                g = data[off]
                off += 1
                b = data[off]
                off += 1
                self._leds[i] = LED(r, g, b, brightness, mode)

    def export(self):
        data = {}

        for i in range(self.count):
            data[defs.LED_NAMES[i]] = {
                'r': self._leds[i].r,
                'g': self._leds[i].g,
                'b': self._leds[i].b,
                'brightness': self._leds[i].brightness,
                'mode': self._leds[i].mode,
            }

        return data

    def __iter__(self):
        for led in self._leds:
            yield led

    def __str__(self):
        lines = [
            ' LED       | MODE    | COLOR  | BRIGHTNESS',
            '-----------|---------|--------|-----------'
        ]

        for i, led in enumerate(self._leds):
            lines.append('{i} {name} | {mode} | {color} | {brightness}'.format(**{
                'i': str(i + 1).rjust(2),
                'name': defs.LED_NAMES[i].ljust(7),
                'mode': led.mode.ljust(7),
                'color': led.hex,
                'brightness': led.brightness,
            }))

        return '\n'.join(lines)
