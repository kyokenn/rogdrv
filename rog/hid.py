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

HID_INTERFACE = None
HIDDevice = None


import hid


if hasattr(hid, 'Device'):
    from hid import Device as HIDDevice
    HID_INTERFACE = 'hid'

else:
    HID_INTERFACE = 'hidapi'


def get_property(obj, name):
    if HID_INTERFACE == 'hid':
        return obj[name]
    elif HID_INTERFACE == 'hidapi':
        return obj[name]


def open_device(info):
    if HID_INTERFACE == 'hid':
        return HIDDevice(path=info['path'])
    elif HID_INTERFACE == 'hidapi':
        device = hid.device()
        device.open_path(info['path'])
        return device


def read_device(device, count):
    if HID_INTERFACE == 'hid':
        return device.read(count)
    elif HID_INTERFACE == 'hidapi':
        return device.read(count)


def list_devices(vendor_id, product_id):
    return tuple(hid.enumerate(vendor_id, product_id))
