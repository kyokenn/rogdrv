# Copyright (C) 2021 Kyoken, kyoken@kyoken.ninja

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

import gi
import os
import signal

gi.require_version('Gtk', '3.0')
gi.require_version('Notify', '0.7')

from gi.repository import Gtk
from gi.repository import Notify

import ratbag

from .menu import TrayMenu
from .handler import TrayMenuEventHandler
from .utils import find_icons, get_autostart_path

APPID = 'rogdrv'


def gtk3_main():
    # Handle pressing Ctr+C properly, ignored by default
    signal.signal(signal.SIGINT, signal.SIG_DFL)

    # generate UI
    builder = Gtk.Builder()
    builder.add_from_file(os.path.join(
        os.path.abspath(os.path.dirname(__file__)),
        'gtk3.glade'))

    def f(r, device):
        print(device)

    # disable profiles if unsupported
    # if not device.profiles:
    #     profile = builder.get_object('menu_profile')
    #     profile.set_visible(False)

    # bind events
    handler = TrayMenuEventHandler(builder)
    builder.connect_signals(handler)
    ratbagd = ratbag.Ratbag.create()
    ratbagd.connect('device-added', handler.on_device_added)
    ratbagd.start()

    # create tray icon
    trayicon = TrayMenu(APPID, next(find_icons()), builder.get_object('menu'))
    Notify.init(APPID)
    Gtk.main()
