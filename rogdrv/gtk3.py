# Copyright (C) 2018 Kyoken, kyoken@kyoken.ninja

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

APPID = 'rogdrv'


def find_icons():
    for location in (
            os.path.abspath(os.path.dirname(__file__)),
            '/usr/share/pixmaps',
            '/usr/local/share/pixmaps'):
        for icon in ('rog-symbolic.symbolic.png', 'rog.png'):
            path = os.path.join(location, icon)
            if os.path.exists(path):
                yield path

    icon_theme = Gtk.IconTheme.get_default()
    for icon_name in ('input-mouse-symbolic', 'input-mouse'):
        for res in (16, 24, 32):
            icon = icon_theme.lookup_icon(icon_name, res, 0)
            if icon is not None:
                yield icon.get_filename()


def get_autostart_path():
    xdg_home = os.environ.get('XDG_CONFIG_HOME')
    if xdg_home and os.path.isdir(xdg_home):
        home = xdg_home
    else:
        home = os.path.expanduser('~')

    return os.path.join(home, '.config', 'autostart', 'rogdrv.desktop')


class TrayIcon(object):
    def __init__(self, icon_path, menu):
        self._menu = menu

        APPIND_SUPPORT = True
        try:
            from gi.repository import AppIndicator3
        except:
            APPIND_SUPPORT = False

        if APPIND_SUPPORT:
            self._icon = AppIndicator3.Indicator.new(
                APPID, icon_path,
                AppIndicator3.IndicatorCategory.APPLICATION_STATUS)
            self._icon.set_status(AppIndicator3.IndicatorStatus.ACTIVE)
            self._icon.set_menu(self._menu)
        else:
            self._icon = Gtk.StatusIcon()
            self._icon.set_from_file(icon_path)
            self._icon.connect('popup-menu', self.on_popup_menu)

    def on_popup_menu(self, icon, button, time):
        self._menu.popup(
            None, None, Gtk.StatusIcon.position_menu,
            icon, button, time)


class EventHandler(object):
    def __init__(self, builder, device):
        self._builder = builder
        self._device = device

    def on_quit(self, *args, **kwargs):
        Notify.uninit()
        Gtk.main_quit()

    def on_autostart(self, *args, **kwargs):
        enable = self._builder.get_object('menu_autostart_enable')
        disable = self._builder.get_object('menu_autostart_disable')
        if os.path.exists(get_autostart_path()):  # enabled
            disable.set_active(True)
            enable.set_active(False)
        else:
            enable.set_active(True)
            disable.set_active(False)

    def on_autostart_enable(self, *args, **kwargs):
        with open(get_autostart_path(), 'w') as f:
            f.write('''
[Desktop Entry]
Name=ROGDRV
GenericName=ASUS ROG userspace driver
Comment=ASUS ROG userspace driver
Exec=rogdrv
Terminal=false
Type=Application
Icon=input-mouse
StartupNotify=false''')

    def on_autostart_disable(self, *args, **kwargs):
        if os.path.exists(get_autostart_path()):
            os.remove(get_autostart_path())

    def on_profile(self, *args, **kwargs):
        profile = self._device.get_profile()
        for i in range(1, 3 + 1):
            menu_item = self._builder.get_object('menu_profile_{}'.format(i))
            menu_item.set_active(i == profile)

    def on_profile_1(self, *args, **kwargs):
        self._device.set_profile(1)

    def on_profile_2(self, *args, **kwargs):
        self._device.set_profile(2)

    def on_profile_3(self, *args, **kwargs):
        self._device.set_profile(3)


def gtk3_main(device):
    # Handle pressing Ctr+C properly, ignored by default
    signal.signal(signal.SIGINT, signal.SIG_DFL)

    builder = Gtk.Builder()
    builder.add_from_file(os.path.join(
        os.path.abspath(os.path.dirname(__file__)),
        'gtk3.glade'))
    builder.connect_signals(EventHandler(builder, device))

    trayicon = TrayIcon(next(find_icons()), builder.get_object('menu'))
    Notify.init(APPID)
    Gtk.main()
