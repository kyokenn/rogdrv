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

Using
=====

You need r/w permissions for /dev/hidrawX file for your mouse.

```
    rogdrv  - start in virtual uinput device mode

    rogdrv --help  - display help

    rogdrv actions  - display list of actions

    rogdrv bind [button action]  - bind a button or display list of bindings
        button: 1-10
        action: action code (241 or 0xF1 or 0xf1)

    rogdrv color [name red green blue [mode] [bright.]]  - get/set LED colors
        name: logo, wheel, bottom, all
        red: 0-255
        green: 0-255
        blue: 0-255
        mode: default, breath, rainbow, wave, reactive, flasher
        bright.: 0-4

    rogdrv profile  - switch profile
        profile: 1-3

    rogdrv dpi [dpi [type]]  - get/set DPI
        dpi: DPI
        type: 1 (default) or 2

```
