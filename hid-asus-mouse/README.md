hid-asus-mouse
==========

ASUS ROG & TUF mouse driver as Linux kernel module.

This driver is work in progress. It’s unfinished and may crash your system.

Status
------

* Loading driver and attaching to HID device - **DONE**
* Parse events for the gen2 (array) and gen3 (bitmask) mice - **DONE**
* Print parsed keyboard event from event mapping to __dmesg__ - **DONE**
* Generate keyboard events - **DONE**


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
