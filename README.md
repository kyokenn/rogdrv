rogdrv
======

**rogdrv** is a simple ASUS ROG (Republic of Gamers) userspace mouse driver for Linux.
The mouse is a composite device which consists of 3 interfaces:
mouse, keyboard and consumer control (for changing the mouse settings).

The keyboard interface for some devices is unsupported on Linux,
but it's recognised as HID device.
So this driver maps HID events to the generic keyboard events.

The protocol was reverse-engineered, so everything is experimental. Use at your own risk.


Alternative solutions
---------------------

**Keyboard events handling module**

HID kernel module - [hid-asus-mouse](https://github.com/kyokenn/hid-asus-mouse)


**Mouse configuration tool**

[piper](https://github.com/libratbag/piper)

with

[libratbag](https://github.com/libratbag/libratbag)

Current missing features:

* Button response
* Angle snapping
* Extra LED modes
* Key binding
* Sleep timeout


Supported devices and features
------------------------------

Device name                   | Profiles | Button Bindings | Performance Settings | LEDs | Sleep
------------------------------|----------|-----------------|----------------------|------|-------
**Buzzard**                   | +        | ?               | ?                    | ?    | N/A
**Gladius II**                | +        | +               | +                    | +    | N/A
**Gladius II Origin**         | +        | +               | +                    | +    | N/A
**Gladius II Origin PNK LTD** | +        | +               | +                    | +    | N/A
**Keris Wireless**            | +        | +               | +                    | +    | +
**Chakram**                   | +        | ?               | +                    | +    | +
**Pugio**                     | +        | +               | +                    | +    | N/A
**Pugio II**                  | +        | ?               | ?                    | +    | ?
**Strix Carry**               | +        | +               | +                    | N/A  | +
**Strix Impact II Wireless**  | +        | +               | +                    | +    | ?
**Strix Impact**              | N/A      | ?               | ?                    | +    | N/A

* **Profiles** - Profile switching feature
* **Button Bindings** - Buttons binding feature
* **Performance Settings** - DPI, polling rate, buttons response, angle snapping configuration feature
* **LEDs** - LED color customization feature
* **Sleep** - Sleep timeout setting feature for the wireless mices

There is a chance that a driver can be compatible with other mouse devices
from ASUS ROG (Republic of Gamers) series.

Unsupported devices
-------------------

Those devices are from the same generation and they are based on the same ASUS hardware which
is not compatible with **hid-generic** linux driver.

You can check it with:
```
LIBUSB_DEBUG=9 sudo -E lsusb -v -d 0b05:<mouse product ID>
```

There would be no **Consumer Control** interface in the device descriptor
which means they are not compatible.
It would report only **Mouse** and **Keyboard** interfaces.

* Spatha
* Gladius
* Strix Evolve


Requirements
------------

**Common requirements**

* python >= 3.0
* python-evdev
* gir-appindicator3

**HID requirements**

Only single one of it is required

* [python3-hid](https://github.com/trezor/cython-hidapi)
* [python3-hidapi](https://github.com/jbaiter/hidapi-cffi)
* [hid](https://github.com/apmorton/pyhidapi) from PyPi (could fail to find devices, **not recommended!**)

Ubuntu:
```
apt install python3-hidapi python3-evdev gir1.2-appindicator3-0.1
```

Installation
------------

Userspace driver installation:

```
sudo python3 setup.py install
```
or
```
sudo pip3 install .
```

You need r/w permissions for /dev/hidrawX file of your mouse.

You can solve this by installing a custom udev rules:

```
sudo ./install_udev
sudo udevadm control --reload-rules
sudo udevadm trigger
```

Using
-----

Userspace driver consists of 2 programs: **rogdrv** and **rogdrv-config**

**rogdrv** is a virtual uinput device driver which converts mouse events into uinput events.
![rogdrv](/screenshot.png)
```
Usage: rogdrv [--debug] [--console]
  --help - display help
  --debug - debug mode
  --console - starts in pure console mode, disables tray icon
```

**rogdrv-config** is a mouse configuration tool.
```
Usage:
  rogdrv-config <command> --help - display help for a command
  rogdrv-config <command> [--debug] [args] - run a command

Available commands:
  rogdrv-config actions - display list of available action codes
  rogdrv-config bind - bind a button or display current bindings
  rogdrv-config color - get/set LED colors
  rogdrv-config dpi - get/set DPI
  rogdrv-config dump - dump settings to stdout or .json file
  rogdrv-config load - load settings from .json file
  rogdrv-config profile - get/set profile
  rogdrv-config rate - get/set polling rate
  rogdrv-config response - get/set button response
  rogdrv-config sleep - get/set sleep timeout and battery alert level
  rogdrv-config snapping - enable/disable snapping
  rogdrv-config version - get device firmware version
```
