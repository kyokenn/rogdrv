rogdrv
======

**rogdrv** is a simple ASUS ROG (Republic of Gamers) userspace mouse driver for Linux.
It acts as native (no D-BUS interaction) front-end to [ratbag-python](https://github.com/kyokenn/ratbag-python)


Supported devices
-----------------

[Device files](https://github.com/kyokenn/ratbag-python/tree/master/ratbag/devices)


Installation
------------

Clone the git repository (including **ratbag-python** submodule):
```
git clone --recurse-submodules https://github.com/kyokenn/rogdrv.git
cd rogdrv
```

Install the ratbag-python:
```
sudo pip3 install ./ratbag-python
```

Install the rogdrv:
```
sudo pip3 install .
```

**rogdrv** and **rogdrv-config** requires r/w permissions
for /dev/hidrawX file of your mouse.
If you want to run them in _rootless_ mode without "sudo",
then you can install the custom udev rules:
```
sudo ./install_udev
sudo udevadm control --reload-rules
sudo udevadm trigger
```

Using
-----

Userspace driver consists of 2 programs: **rogdrv** and **rogdrv-config**

Your mouse must be connected using RF or USB.

**rogdrv** is mouse configuration tool with GUI,
which have easy access to some simple settings like profile switching.
![rogdrv](/screenshot.png)
```
Usage:
  rogdrv
```

**rogdrv-config** is a mouse configuration tool for the console,
which covers the almost all settings.
```
Usage:
  rogdrv-config <command> --help - display help for a command
  rogdrv-config <command> [--debug] [args] - run a command

Available commands:
  rogdrv-config actions - display list of available action codes
  rogdrv-config bind - bind a button or display current bindings
  rogdrv-config color - get/set LED colors
  rogdrv-config dpi - get/set DPI
  rogdrv-config profile - get/set profile
  rogdrv-config rate - get/set polling rate
  rogdrv-config response - get/set button response
  rogdrv-config snapping - enable/disable snapping
```


See also
--------

**hid-asus-mouse**

If your mouse doesn't support native HID-compatible keyboard events
(old Gladius II generation and earlier mice in RF mode) or you want some extra features,
then you can try the kernel module
[hid-asus-mouse](https://github.com/kyokenn/hid-asus-mouse)


**ratbag-python**

You can run the **ratbag-python** daemon and use it with [piper](https://github.com/libratbag/piper)

Install the D-BUS settings:
```
sudo cp -fv ./ratbag-python/dbus/org.freedesktop.ratbag1.conf /etc/dbus-1/system.d/
```

Run the **ratbag-python** daemon:
```
sudo ratbagd
```

Run the **piper** GUI.
```
piper
```


**libratbag**

You can also replace **ratbag-python** daemon with original
[libratbag](https://github.com/libratbag/libratbag)
