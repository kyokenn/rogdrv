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

try:
    import hid
    HIDDevice = None
except ImportError:
    import hidapi as hid
    from hidapi import Device as HIDDevice


def get_property(obj, name):
    if type(obj) == dict:  # hid module
        return obj[name]
    else:  # hidapi module
        return getattr(obj, name)


def open_device(info):
    if HIDDevice is None:
        device = hid.device()
        device.open_path(info['path'])
        return device
    else:
        return HIDDevice(info)


def read_device(device, count):
    if HIDDevice is None:
        return device.read(count)
    else:
        return device.read(count, blocking=True)


def list_devices(vendor_id, product_id):
    return tuple(hid.enumerate(vendor_id=vendor_id, product_id=product_id))
