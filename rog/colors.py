import copy


DEFAULT_COLORS = {
    1: (255, 0, 0),
    2: (0, 255, 0),
    3: (0, 0, 255),
}

DEFAULT_BRIGHTNESS = {
    1: 4,
    2: 4,
    3: 4,
}


class Colors(object):
    def __init__(self, count):
        self._colors = {}
        self._brightness = {}

        for i in range(1, count + 1):
            self._colors[i] = DEFAULT_COLORS[i]
            self._brightness[i] = DEFAULT_BRIGHTNESS[i]

    @property
    def count(self):
        return len(tuple(self._colors.keys()))

    def load(self, data):
        if type(data) == dict:
            for i in range(1, self.count + 1):
                self._brightness[i] = data['b{}'.format(i)]
                self._colors[i] = data['c{}'.format(i)]

        else:
            self._brightness[1] = data[5]
            self._colors[1] = data[6], data[7], data[8]
            self._brightness[2] = data[10]
            self._colors[2] = data[11], data[12], data[13]
            self._brightness[3] = data[15]
            self._colors[3] = data[16], data[17], data[18]

    def export(self):
        data = {}
        for k, v in self._colors.items():
            data['c{}'.format(k)] = v
        for k, v in self._brightness.items():
            data['b{}'.format(k)] = v
        return data

    def __iter__(self):
        for color, (r, g, b) in self._colors.items():
            yield color, r, g, b, self._brightness[color]

    def __str__(self):
        template = '''1 (logo):\t[brightness:{b1}] {c1}
2 (wheel):\t[brightness:{b2}] {c2}
3 (bottom):\t[brightness:{b3}] {c3}'''
        lines = template.split('\n')[:self.count - 1]
        template2 = '\n'.join(lines)

        return template2.format(**self.export())
