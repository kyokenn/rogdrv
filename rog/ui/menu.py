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

from . import Gtk
from .. import defs, logger


class TrayMenu(object):
    """
    Tray icon menu.
    """
    def __init__(self, appid, icon_path, menu):
        self._menu = menu

        APP_INDICATOR_SUPPORT = True
        try:
            gi.require_version('AppIndicator3', '0.1')
            from gi.repository import AppIndicator3
        except Exception as e:
            APP_INDICATOR_SUPPORT = False

        if APP_INDICATOR_SUPPORT:
            self._icon = AppIndicator3.Indicator.new(
                appid, icon_path,
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
