rogdrv
======

rogdrv is a simple ASUS ROG userspace mouse driver for Linux.
The mouse device consists of 2 input devices: mouse and keyboard.
The keyboard part is unsupported on Linux, but it's recognised as HID device.
So this driver maps HID events to the generic keyboard events.

The protocol was reverse-engineered, so everything is experimental. Use at your own risk.

Supported devices
-----------------

Device name      | Own device | Profiles | Buttons | DPI    | Polling rate | LED colors
-----------------|------------|----------|---------|--------|--------------|-----------
**Pugio**        | +          | +        | +       | +      | +            | +
**Strix Carry**  | +          | +        | +       | +      | +            | N/A
**Strix Impact** |            | ?        | ?       | ?      | ?            | +
**Buzzard**      |            | +        | ?       | ?      | ?            | ?
**Spatha**       |            | +        | ?       | ?      | ?            | ?

**Own device** - I own this device, which means I can reverce engeneer,
implement and test all the features.

**Profiles** - Profile switching feature.

**Buttons** - Buttons binding feature.

**DPI** - DPI setting feature.

**Polling rate** - Polling rate setting feature.

**LED colors** - LED color customization feature.

There is a chance that a driver can be compatible with other mouse devices
from ASUS ROG (Republic of Gamers) series.

Features
--------

* Virtual uinput device
* Profiles switching
* Buttons bindings
* DPI setting
* Polling rate setting
* LED colors customization

Requirements
------------

* python >= 3.0
* python-hidapi + python-cffi (hidapi-cffi)
* python-evdev
* gir-appindicator3

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

You need r/w permissions for /dev/hidrawX file of your mouse.
You can solve this by installing a custom udev rules:
```
sudo cp -f udev/50-rogdrv.rules /etc/udev/rules.d/
sudo udevadm control --reload-rules
sudo udevadm trigger
```

Using
-----

Userspace driver consists of 2 programs: *rogdrv* and *rogdrv-config*

rogdrv is a virtual uinput device driver which converts mouse events into uinput events.
![rogdrv](/screenshot.png)
```
Usage: rogdrv [--console]
  --help       - display help
  --console    - starts in pure console mode, disables tray icon
```

rogdrv-config is a mouse configuration tool.
```
Usage: rogdrv-config [options...]
  --help       - display help
  ...
```
