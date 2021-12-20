hid-asus-mouse
==============

HID driver for ASUS ROG & TUF mice
providing generation of keyboard events.


Device compatibility
--------------------

**Generation 1 devices with broken HID descriptors**

Those devices needs some HID descriptor fixes, so patches are welcome.

You can’t change mouse settings without descriptor fixes but keyboard events should work.

* Gladius
* Spatha
* Strix Evolve

**Generation 1 devices with good HID descriptors**

* Buzzard
* Gladius II
* Gladius II Origin
* Gladius II Origin PNK LTD
* Pugio
* Strix Carry
* Strix Impact
* Strix Impact II Wireless

**Generation 2 devices**

You don’t need any driver for those devices.
It was made as a reference for testing and debugging purposes.

* Chakram
* Keris Wireless


Building
--------

Build the kernel module

```
make
```


Running
------

Load the kernel module

```
sudo insmod hid-asus-mouse.ko
```

Check the module status

```
dmesg
```
