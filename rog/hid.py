# Copyright (C) 2020 Kyoken, kyoken@kyoken.ninja

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


from . import logger


class SubDevice(object):
    def __init__(self, info):
        self._info = info
        self._device = None

    def __getitem__(self, name):
        raise NotImplementedError()

    def read(self, count):
        return self._device.read(count)

    def write(self, data):
        self._device.write(data)

    def open(self):
        raise NotImplementedError()

    def close(self):
        self._device.close()
        self._device = None


class CythonSubDevice(SubDevice):
    """
    python3-hid (ubuntu) / cython-hidapi
    https://github.com/trezor/cython-hidapi
    """
    def open(self):
        import hid
        self._device = hid.device()
        self._device.open_path(self['path'])

    def __getitem__(self, name):
        return self._info[name]


class CFFISubDevice(SubDevice):
    """
    python3-hidapi (ubuntu) / hidapi-cffi
    https://github.com/jbaiter/hidapi-cffi
    """
    def open(self):
        import hidapi
        self._device = hidapi.Device(path=self['path'])

    def __getitem__(self, name):
        return getattr(self._info, name)


def list_devices(vendor_id, product_id):
    try:
        import hidapi
        logger.debug('getting list of devices using "hidapi-cffi"')
        subdevices = []
        for info in hidapi.enumerate(vendor_id, product_id):
            subdevices.append(CFFISubDevice(info))
        return subdevices
    except ImportError as e:
        pass

    try:
        import hid
        logger.debug('getting list of devices using "cython-hidapi"')
        subdevices = []
        for info in hid.enumerate(vendor_id, product_id):
            subdevices.append(CythonSubDevice(info))
        return subdevices
    except ImportError as e:
        pass

    return []
