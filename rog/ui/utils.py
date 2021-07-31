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

from gi.repository import Gtk


def get_autostart_path():
    xdg_home = os.environ.get('XDG_CONFIG_HOME')
    if xdg_home and os.path.isdir(xdg_home):
        home = xdg_home
    else:
        home = os.path.expanduser('~')

    return os.path.join(home, '.config', 'autostart', 'rogdrv.desktop')


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
