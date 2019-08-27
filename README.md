rogdrv
======

rogdrv is a simple ASUS ROG (Republic of Gamers) userspace mouse driver for Linux.
The mouse device consists of 2 input devices: mouse and keyboard.
The keyboard part is unsupported on Linux, but it's recognised as HID device.
So this driver maps HID events to the generic keyboard events.

The protocol was reverse-engineered, so everything is experimental. Use at your own risk.

Supported devices and features
------------------------------

Device name      | Own device | Profiles | Button Bindings | Performance Settings | LEDs | Sleep
-----------------|------------|----------|-----------------|----------------------|------|-------
**Pugio**        | +          | +        | +               | +                    | +    | N/A
**Strix Carry**  | +          | +        | +               | +                    | N/A  | +
**Strix Impact** |            | ?        | ?               | ?                    | +    | N/A
**Strix Evolve** |            | ?        | ?               | ?                    | ?    | N/A
**Buzzard**      |            | +        | ?               | ?                    | ?    | N/A
**Spatha**       |            | +        | ?               | ?                    | ?    | ?

* **Own device** - I own this device, which means I can reverse engeneer, implement and test all the features
* **Profiles** - Profile switching feature
* **Button Bindings** - Buttons binding feature
* **Performance Settings** - DPI, polling rate, buttons response, angle snapping configuration feature
* **LEDs** - LED color customization feature
* **Sleep** - Sleep timeout setting feature for the wireless mices

There is a chance that a driver can be compatible with other mouse devices
from ASUS ROG (Republic of Gamers) series.

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
or
```
sudo pip3 install .
```

You need r/w permissions for /dev/hidrawX file of your mouse.

You can solve this by installing a custom udev rules:

```
sudo cp -f udev/50-rogdrv.rules /etc/udev/rules.d/
sudo udevadm control --reload-rules
sudo udevadm trigger
```
or
```
./install_udev.sh
```

Using
-----

Userspace driver consists of 2 programs: **rogdrv** and **rogdrv-config**

rogdrv is a virtual uinput device driver which converts mouse events into uinput events.
![rogdrv](/screenshot.png)
```
Usage: rogdrv [--console]
  --help       - display help
  --console    - starts in pure console mode, disables tray icon
```

rogdrv-config is a mouse configuration tool.
```
Usage:
  rogdrv-config --help                            - displays help
  rogdrv-config --debug                           - enables debug mode

  rogdrv-config actions                           - display list of available actions

  rogdrv-config profile [value]                   - get/set profile
    value: profile no. (1-3)

  rogdrv-config bind [button action]              - bind a button or display bindings
    button: button no. (1-99)
    action: action code (241 or 0xF1 or 0xf1)

  rogdrv-config dpi [value [preset]]              - get/set DPI
    value: DPI (50-7200)
    preset: 1 (default) or 2

  rogdrv-config rate [hz]                         - get/set polling rate
    hz: rate in Hz (125, 250, 500, 1000)

  rogdrv-config response [ms]                     - get/set buttons response
    ms: response in ms (4, 8, 12, 16, 20, 24, 28, 32)

  rogdrv-config snapping [type]                   - get/set angle snapping type
    type: angle snapping type (1 or 2)

  rogdrv-config color [name r g b [mode] [brght]] - get/set LED colors
    name: logo, wheel, bottom, all
    r: red (0-255)
    g: green (0-255)
    b: blue (0-255)
    mode: default, breath, rainbow, wave, reactive, flasher
    brght: brightness 0-4 (default-4)

  rogdrv-config sleep [value]                     - get/set sleep timeout
    value: timeout in minutes (0-disabled, 1, 2, 3, 5, 10)

  rogdrv-config dump [file]                       - save settings into file
    file: path to json file

  rogdrv-config load file                         - load settings from file
    file: path to json file
```
