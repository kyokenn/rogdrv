import copy

from . import defs


DEFAULT_COLORS = {
    1: (255, 0, 0),
    2: (0, 255, 0),
    3: (0, 0, 255),
}


class Color(object):
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


class Colors(object):
    def __init__(self, count):
        self._colors = [None] * count
        for i in range(self.count):
            r, g, b = DEFAULT_COLORS[i + 1]
            self._colors[i] = Color(r, g, b, 4, 'default')

    @property
    def count(self):
        return len(self._colors)

    def load(self, data):
        if isinstance(data, dict):  # load from json settings backup
            self._colors = [None] * len(tuple(data.keys()))
            for led, item in data.items():
                self._colors[defs.LEDS.index(led)] = Color(
                    item['r'], item['g'], item['b'],
                    item['brightness'],
                    item['mode'])

        else:  # load from device
            off = 4
            for i in range(self.count):
                mode = 'default'
                for k, v in defs.LED_MODES.items():
                    if v == data[off]:
                        mode = k
                off += 1
                brightness = data[off]
                off += 1
                r = data[off]
                off += 1
                g = data[off]
                off += 1
                b = data[off]
                off += 1
                self._colors[i] = Color(r, g, b, brightness, mode)

    def export(self):
        data = {}

        for i in range(self.count):
            data[defs.LEDS[i]] = {
                'r': self._colors[i].r,
                'g': self._colors[i].g,
                'b': self._colors[i].b,
                'brightness': self._colors[i].brightness,
                'mode': self._colors[i].mode,
            }

        return data

    def __iter__(self):
        for color in self._colors:
            yield color

    def __str__(self):
        lines = [
            ' LED       | MODE    | COLOR  | BRIGHTNESS',
            '-----------|---------|--------|-----------'
        ]

        for i, color in enumerate(self._colors):
            lines.append('{i} {led} | {mode} | {color} | {brightness}'.format(**{
                'i': str(i + 1).rjust(2),
                'led': defs.LEDS[i].ljust(7),
                'mode': color.mode.ljust(7),
                'color': color.hex,
                'brightness': color.brightness,
            }))

        return '\n'.join(lines)
