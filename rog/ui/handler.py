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

import os

from . import Gtk, Notify
from .utils import get_autostart_path
from .. import logger


class TrayMenuEventHandler(object):
    """
    GTK event handler for tray icon menu.
    """
    def __init__(self, builder):
        self._builder = builder
        self._device = None

        menu_profile = self._builder.get_object('menu_profile')
        menu_profile.set_visible(False)

        menu_dpi = self._builder.get_object('menu_dpi')
        menu_dpi.set_visible(False)

        menu_led = self._builder.get_object('menu_led')
        menu_led.set_visible(False)

        menu_rate = self._builder.get_object('menu_rate')
        menu_rate.set_visible(False)

        menu_perf = self._builder.get_object('menu_perf')
        menu_perf.set_visible(False)

        autostart = self._builder.get_object('menu_autostart')
        autostart.set_active(os.path.exists(get_autostart_path()))

    def on_device_added(self, r, device):
        self._device = device

        for i in range(6):
            if i >= len(device.profiles):
                menu_item = self._builder.get_object('menu_profile_{}'.format(i))
                menu_item.set_visible(False)
        menu_profile = self._builder.get_object('menu_profile')
        menu_profile.set_visible(bool(device.profiles))

        for profile in device.profiles:
            if not profile.active:
                continue

            for i in range(4):
                menu_item = self._builder.get_object('menu_dpi_{}'.format(i))
                if i >= len(profile.resolutions):
                    menu_item.set_visible(False)
            menu_dpi = self._builder.get_object('menu_dpi')
            menu_dpi.set_visible(True)

            # if not self._device.wireless:
            if True:
                self._builder.get_object('menu_sleep').set_visible(False)
                self._builder.get_object('menu_battery').set_visible(False)

            if profile.leds:
                for i in range(3):
                    if i >= len(profile.leds):
                        menu_item = self._builder.get_object('menu_led_{}'.format(i))
                        menu_item.set_visible(False)
            menu_led = self._builder.get_object('menu_led')
            menu_led.set_visible(bool(profile.leds))

            menu_rate = self._builder.get_object('menu_rate')
            menu_rate.set_visible(True)

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
        for profile in self._device.profiles:
            menu_item = self._builder.get_object('menu_profile_{}'.format(profile.index))
            if profile.active:
                logger.debug('current profile is {}'.format(profile.index))
                menu_item.set_active(True)

    def on_profile(self, item, *args, **kwargs):
        """
        Event on profile select.
        """
        if item.get_active():
            profile_old = 0
            profile_new = int(str(item.get_action_target_value()))  # GVariant -> str -> int

            for profile in self._device.profiles:
                if profile.active:
                    profile_old = profile.index

            if profile_old != profile_new:
                logger.debug(
                    'switching profile from {} to {}'
                    .format(profile_old, profile_new))
                for profile in self._device.profiles:
                    if profile.index == profile_new:
                        profile.set_active()

    def on_dpi_choice(self, item, *args, **kwargs):
        """
        Event on DPI submenu expanding.
        """
        for profile in self._device.profiles:
            if not profile.active:
                continue

            for resolution in profile.resolutions:
                menu_item = self._builder.get_object('menu_dpi_{}'.format(resolution.index))
                menu_item.set_label(
                    'Preset {}: {}'
                    .format(resolution.index, resolution.dpi[0]))

    def on_rate_choice(self, item, *args, **kwargs):
        """
        Event on polling rate submenu expanding.
        """
        for profile in self._device.profiles:
            if not profile.active:
                continue

            logger.debug('current polling rate is {}'.format(profile.report_rate))
            for irate in profile.report_rates:
                menu_item = self._builder.get_object('menu_rate_{}'.format(irate))
                if irate == profile.report_rate:
                    menu_item.set_active(True)

    def on_rate(self, item, *args, **kwargs):
        """
        Event on polling rate select.
        """
        if item.get_active():
            for profile in self._device.profiles:
                if not profile.active:
                    continue

                rate_old = profile.report_rate
                rate_new = int(str(item.get_action_target_value()))  # GVariant -> str -> int

                if rate_old != rate_new:
                    logger.debug(
                        'changing polling rate from {} to {}'
                        .format(rate_old, rate_new))
                    profile.set_report_rate(rate_new)
                    self._device.emit('commit', None)

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

    def on_led_choice(self, item, *args, **kwargs):
        iled = int(str(item.get_action_target_value()))  # GVariant -> str -> int

        for profile in self._device.profiles:
            if not profile.active:
                continue

            for led in profile.leds:
                if iled == led.index:
                    c = self._builder.get_object('menu_led_{}_color'.format(led.index))
                    c.set_label('Color: #{:02x}{:02x}{:02x}'.format(*led.color))

                    b = self._builder.get_object('menu_led_{}_brightness'.format(led.index))
                    b.set_label('Brightness: {}%'.format(round(led.brightness / 255 * 100)))

                    m = self._builder.get_object('menu_led_{}_mode'.format(led.index))
                    m.set_label('Mode: {}'.format(led.mode.name))

    def on_led_mode_choice(self, item, *args, **kwargs):
        iled = int(str(item.get_action_target_value()))  # GVariant -> str -> int

        for profile in self._device.profiles:
            if not profile.active:
                continue

            for led in profile.leds:
                if iled == led.index:
                    menu_item = self._builder.get_object(
                        'menu_led_{}_mode_{}'.format(led.index, led.mode.name.lower()))
                    menu_item.set_active(True)

    def on_led_mode(self, item, *args, **kwargs):
        # GVariant -> str -> int -> str
        led_id, mode = '{:02d}'.format(int(str(item.get_action_target_value())))

        if item.get_active():
            for profile in self._device.profiles:
                if not profile.active:
                    continue

                for led in profile.leds:
                    if int(led_id) == led.index:
                        led_mode_old = led.mode
                        led_mode_new = None

                        for name in dir(led.Mode):
                            led_mode = getattr(led.Mode, name)
                            if hasattr(led_mode, 'value') and led_mode.value == int(mode):
                                led_mode_new = led_mode
                                break

                        if led_mode_old != led_mode_new:
                            led.set_mode(led_mode_new)
                            self._device.emit('commit', None)

    def on_led_brightness_choice(self, item, *args, **kwargs):
        led_id = int(str(item.get_action_target_value()))  # GVariant -> str -> int

        for profile in self._device.profiles:
            if not profile.active:
                continue

            for led in profile.leds:
                if led_id == led.index:
                    menu_item = self._builder.get_object(
                        'menu_led_{}_brightness_{}'
                        .format(led.index, round(led.brightness / 255 * 100)))
                    menu_item.set_active(True)

    def on_led_brightness(self, item, *args, **kwargs):
        # GVariant -> str -> int -> str
        s = '{:04d}'.format(int(str(item.get_action_target_value())))
        led_id = int(s[0])
        brightness = int(s[1:])

        if item.get_active():
            for profile in self._device.profiles:
                if not profile.active:
                    continue

                for led in profile.leds:
                    if led_id == led.index:
                        brightness_old = led.brightness
                        brightness_new = round(brightness / 100 * 255)

                        if brightness_old != brightness_new:
                            led.set_brightness(brightness_new)
                            self._device.emit('commit', None)
