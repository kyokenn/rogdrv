rogdrv
======

rogdrv is a simple ASUS ROG Pugio userspace mouse driver for Linux.
The mouse device consists of 2 input devices: mouse and keyboard.
The keyboard part is unsupported on Linux, but it's recognised as HID device.
So this driver maps HID events to the generic keyboard events.

There is a chance that a driver can be compatible with other mouse devices
from ASUS ROG (Republic of Gamers) series.

The protocol was reverse-engineered, so everything is experimental. Use at your own risk.

Requirements
============

* python >= 3.0
* python-hidapi
* python-evdev

Features
========

* Virtual uinput device
* Button bindings
* LED colors

Installation
============

Userspace driver installation:
```
sudo python3 setup.py install
```

You need r/w permissions for /dev/hidrawX file or your mouse.
You can solve this by installing a custom udev rules:
```
sudo cp -f udev/50-rogdrv.rules /etc/udev/rules.d/
sudo udevadm control --reload-rules
sudo udevadm trigger
```

Using
=====

Userspace driver consists of 2 programs: rogdrv and rogdrv-config

rogdrv is a virtual uinput device driver which converts mouse events into uinput events
```
Usage: rogdrv [--console]
  --help       - display help
  --console    - starts in pure console mode, disables tray icon
```

rogdrv-config is a mouse configuration tool.
```
Usage:
  rogdrv-config actions  - display help

  rogdrv-config actions  - display list of actions

  rogdrv-config bind [button action]  - bind a button or display list of bindings
    button: 1-10
    action: action code (241 or 0xF1 or 0xf1)

  rogdrv-config color [name red green blue [mode] [bright.]]  - get/set LED colors
    name: logo, wheel, bottom, all
    red: 0-255
    green: 0-255
    blue: 0-255
    mode: default, breath, rainbow, wave, reactive, flasher
    bright.: 0-4

  rogdrv-config profile  - switch profile
    profile: 1-3

  rogdrv-config dpi [dpi [type]]  - get/set DPI
    dpi: DPI (50-7200)
    type: 1 (default) or 2

  rogdrv-config rate [rate]  - get/set polling rate
    rate: rate in Hz (125, 250, 500, 1000)
```
