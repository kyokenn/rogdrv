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

from . import defs, logger

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


class TrayMenu(object):
    """
    Tray icon menu.
    """
    def __init__(self, icon_path, menu):
        self._menu = menu

        APPIND_SUPPORT = True
        try:
            from gi.repository import AppIndicator3
        except Exception as e:
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


class TrayMenuEventHandler(object):
    """
    GTK event handler for tray icon menu.
    """
    def __init__(self, builder, device):
        self._builder = builder
        self._device = device

        for i in range(1, 6 + 1):
            if i > self._device.profiles:
                menu_item = self._builder.get_object('menu_profile_{}'.format(i))
                menu_item.set_visible(False)

        for i in range(1, 4 + 1):
            menu_item = self._builder.get_object('menu_dpi_{}'.format(i))
            if i > self._device.dpis:
                menu_item.set_visible(False)

        if not self._device.wireless:
            self._builder.get_object('menu_sleep').set_visible(False)
            self._builder.get_object('menu_battery').set_visible(False)

        for i, name in enumerate(defs.LEDS[:3]):
            if i >= self._device.leds:
                menu_item = self._builder.get_object('menu_led_{}'.format(name))
                menu_item.set_visible(False)

    def on_quit(self, *args, **kwargs):
        Notify.uninit()
        Gtk.main_quit()

    def on_autostart(self, item, *args, **kwargs):
        """
        Event on autostart option toggle.
        """
        logger.debug(
            'autostart '.format('enabled' if item.get_active() else 'disabled'))
        if item.get_active():
            with open(get_autostart_path(), 'w') as f:
                f.write('''
[Desktop Entry]
Name=ROGDRV
GenericName=ASUS ROG userspace driver
Exec=rogdrv
Terminal=false
Type=Application
Icon=input-mouse
StartupNotify=false
''')
        else:
            if os.path.exists(get_autostart_path()):
                os.remove(get_autostart_path())

    def on_profile_choice(self, item, *args, **kwargs):
        """
        Event on profile submenu expanding.
        """
        profile, _, _ = self._device.get_profile_version()
        logger.debug('current profile is {}'.format(profile))
        for i in range(1, self._device.profiles + 1):
            menu_item = self._builder.get_object('menu_profile_{}'.format(i))
            if i == profile:
                menu_item.set_active(True)

    def on_profile(self, item, *args, **kwargs):
        """
        Event on profile select.
        """
        if item.get_active():
            profile_old, _, _ = self._device.get_profile_version()
            profile_new = int(str(item.get_action_target_value()))  # GVariant -> str -> int
            if profile_old != profile_new:
                logger.debug(
                    'switching profile from {} to {}'
                    .format(profile_old, profile_new))
                self._device.set_profile(profile_new)

    def on_dpi_choice(self, item, *args, **kwargs):
        """
        Event on DPI submenu expanding.
        """
        dpis, _, _, _ = self._device.get_dpi_rate_response_snapping()
        for i, dpi in enumerate(dpis, start=1):
            menu_item = self._builder.get_object('menu_dpi_{}'.format(i))
            menu_item.set_label(
                'Preset {} ({}): {}'
                .format(i, defs.DPI_PRESET_COLORS[i], dpi))

    def on_rate_choice(self, item, *args, **kwargs):
        """
        Event on polling rate submenu expanding.
        """
        _, rate, _, _ = self._device.get_dpi_rate_response_snapping()
        logger.debug('current polling rate is {}'.format(rate))
        for irate in defs.POLLING_RATES.values():
            menu_item = self._builder.get_object('menu_rate_{}'.format(irate))
            if irate == rate:
                menu_item.set_active(True)

    def on_rate(self, item, *args, **kwargs):
        """
        Event on polling rate select.
        """
        if item.get_active():
            _, rate_old, _, _ = self._device.get_dpi_rate_response_snapping()
            rate_new = int(str(item.get_action_target_value()))  # GVariant -> str -> int
            if rate_old != rate_new:
                logger.debug(
                    'changing polling rate from {} to {}'
                    .format(rate_old, rate_new))
                self._device.set_rate(rate_new)
                self._device.save()

    def on_perf_choice(self, item, *args, **kwargs):
        """
        Event on performance submenu expanding.
        """
        _, _, _, snapping = self._device.get_dpi_rate_response_snapping()
        logger.debug(
            'angle snapping is {}'
            .format('enabled' if snapping else 'disabled'))
        menu_item = self._builder.get_object('menu_snapping')
        menu_item.set_active(snapping)

    def on_snapping(self, item, *args, **kwargs):
        """
        Event on angle snapping option toggle.
        """
        _, _, _, snapping = self._device.get_dpi_rate_response_snapping()
        if item.get_active() != snapping:
            logger.debug(
                'angle snapping is {}'
                .format('enabled' if snapping else 'disabled'))

            logger.debug(
                '{} angle snapping'
                .format('enabling' if item.get_active() else 'disabling'))
            self._device.set_snapping(item.get_active())
            self._device.save()

    def on_sleep_choice(self, item, *args, **kwargs):
        """
        Event on sleep submenu expanding.
        """
        sleep, _, _ = self._device.get_sleep_charge_alert()
        logger.debug('current sleep timeout is {}'.format(sleep))
        for isleep in defs.SLEEP_TIME.values():
            menu_item = self._builder.get_object('menu_sleep_{}'.format(isleep))
            if isleep == sleep:
                menu_item.set_active(True)

    def on_sleep(self, item, *args, **kwargs):
        """
        Event on sleep timeout option select.
        """
        if item.get_active():
            sleep_old, _, alert = self._device.get_sleep_charge_alert()
            sleep_new = int(str(item.get_action_target_value()))  # GVariant -> str -> int
            if sleep_old != sleep_new:
                logger.debug(
                    'changing sleep timeout from {} to {}'
                    .format(sleep_old, sleep_new))
                self._device.set_sleep_alert(sleep_new, alert)
                self._device.save()

    def on_battery_choice(self, item, *args, **kwargs):
        """
        Event on battery submenu expanding.
        """
        _, charge, alert = self._device.get_sleep_charge_alert()
        logger.debug('current battery alert level is {}%'.format(alert))
        for ialert in (0, 25, 50):
            menu_item = self._builder.get_object('menu_alert_{}'.format(ialert))
            if ialert == alert:
                menu_item.set_active(True)

        self._builder.get_object('menu_charge').set_label('Charge: {}%'.format(charge))

    def on_alert(self, item, *args, **kwargs):
        """
        Event on battery alert level select.
        """
        if item.get_active():
            sleep, _, alert_old = self._device.get_sleep_charge_alert()
            alert_new = int(str(item.get_action_target_value()))  # GVariant -> str -> int
            if alert_old != alert_new:
                logger.debug(
                    'changing battery alert level from {}% to {}%'
                    .format(alert_old, alert_new))
                self._device.set_sleep_alert(sleep, alert_new)
                self._device.save()

    def on_led_logo_choice(self, item, *args, **kwargs):
        self._on_led_choice('logo', item, *args, **kwargs)

    def on_led_wheel_choice(self, item, *args, **kwargs):
        self._on_led_choice('wheel', item, *args, **kwargs)

    def on_led_bottom_choice(self, item, *args, **kwargs):
        self._on_led_choice('bottom', item, *args, **kwargs)

    def _on_led_choice(self, name, item, *args, **kwargs):
        leds = self._device.get_leds()
        for i, led in enumerate(leds):
            if defs.LEDS[i] == name:
                c = self._builder.get_object('menu_led_{}_color'.format(name))
                c.set_label('Color: {}'.format(led.hex))

                b = self._builder.get_object('menu_led_{}_brightness'.format(name))
                b.set_label('Brightness: {}%'.format(led.brightness * 25))

                m = self._builder.get_object('menu_led_{}_mode'.format(name))
                m.set_label('Mode: {}'.format(led.mode))

    def on_led_mode_choice(self, item, *args, **kwargs):
        pass


def gtk3_main(device):
    # Handle pressing Ctr+C properly, ignored by default
    signal.signal(signal.SIGINT, signal.SIG_DFL)

    # generate UI
    builder = Gtk.Builder()
    builder.add_from_file(os.path.join(
        os.path.abspath(os.path.dirname(__file__)),
        'gtk3.glade'))

    # check autostart status
    autostart = builder.get_object('menu_autostart')
    autostart.set_active(os.path.exists(get_autostart_path()))

    # disable profiles if unsupported
    if not device.profiles:
        profile = builder.get_object('menu_profile')
        profile.set_visible(False)

    # bind events
    builder.connect_signals(TrayMenuEventHandler(builder, device))

    # create tray icon
    trayicon = TrayMenu(next(find_icons()), builder.get_object('menu'))
    Notify.init(APPID)
    Gtk.main()
