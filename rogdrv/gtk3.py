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
        self.menu = menu

        APPIND_SUPPORT = True
        try:
            from gi.repository import AppIndicator3
        except:
            APPIND_SUPPORT = False

        if APPIND_SUPPORT:
            self.icon = AppIndicator3.Indicator.new(
                APPID, icon_path,
                AppIndicator3.IndicatorCategory.APPLICATION_STATUS)
            self.icon.set_status(AppIndicator3.IndicatorStatus.ACTIVE)
            self.icon.set_menu(self.menu)
        else:
            self.icon = Gtk.StatusIcon()
            self.icon.set_from_file(icon_path)
            self.icon.connect('popup-menu', self.on_popup_menu)

    def on_popup_menu(self, icon, button, time):
        self.menu.popup(
            None, None, Gtk.StatusIcon.position_menu,
            icon, button, time)


class Handler(object):
    def on_quit(self, *args, **kwargs):
        Notify.uninit()
        Gtk.main_quit()

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


def gtk3_main():
    # Handle pressing Ctr+C properly, ignored by default
    signal.signal(signal.SIGINT, signal.SIG_DFL)

    builder = Gtk.Builder()
    builder.add_from_string('''
<?xml version="1.0" encoding="UTF-8"?>
<interface>
  <requires lib="gtk+" version="3.10"/>

  <object class="GtkMenu" id="menu">
    <property name="visible">True</property>
    <property name="can_focus">False</property>

    <child>
      <object class="GtkMenuItem" id="menu_autostart_enable">
        <property name="visible">True</property>
        <property name="can_focus">False</property>
        <property name="label" translatable="yes">Enable Autorun</property>
        <property name="use_underline">True</property>
        <signal name="activate" handler="on_autostart_enable" swapped="no"/>
      </object>
    </child>

    <child>
      <object class="GtkMenuItem" id="menu_autostart_disable">
        <property name="visible">True</property>
        <property name="can_focus">False</property>
        <property name="label" translatable="yes">Disable Autorun</property>
        <property name="use_underline">True</property>
        <signal name="activate" handler="on_autostart_disable" swapped="no"/>
      </object>
    </child>

    <child>
      <object class="GtkMenuItem" id="menu_quit">
        <property name="visible">True</property>
        <property name="can_focus">False</property>
        <property name="label" translatable="yes">Quit</property>
        <property name="use_underline">True</property>
        <signal name="activate" handler="on_quit" swapped="no"/>
      </object>
    </child>

  </object>
</interface>''')
    builder.connect_signals(Handler())

    trayicon = TrayIcon(next(find_icons()), builder.get_object('menu'))
    Notify.init(APPID)
    Gtk.main()
