#include <linux/hid.h>
#include <linux/module.h>
#include <linux/usb.h>
/* #include "hid-ids.h" */

#include "hid-asus-mouse-common.h"
#include "hid-asus-mouse-common.c"

static void asus_mouse_gen1_parse_events(u32 bitmask[], u8 *data, int size)
{
	int i, bit, code, offset;
	for (i = 0; i < ASUS_MOUSE_DATA_KEY_STATE_NUM; i++)
		bitmask[i] = 0;

	// build bitmask from array of active key codes
	if (size == ASUS_MOUSE_GEN2_EVENT_SIZE) {
#ifdef ASUS_MOUSE_DEBUG
		printk(KERN_INFO "ASUS MOUSE: DATA %02X %02X %02X %02X %02X %02X %02X %02X %02X",
			data[0], data[1], data[2], data[3], data[4], data[5], data[6], data[7], data[8]);
#endif

		for (offset = 3; offset < size; offset++) {
			code = data[offset];
			if (!code)
				continue;
			i = ASUS_MOUSE_DATA_KEY_STATE_NUM - (code / ASUS_MOUSE_DATA_KEY_STATE_BITS) - 1;
			bitmask[i] |= 1 << (code % ASUS_MOUSE_DATA_KEY_STATE_BITS);
		}
	}
}

static int asus_mouse_gen1_raw_event(struct hid_device *hdev, struct hid_report *report,
		u8 *data, int size)
{
	struct usb_interface *iface = to_usb_interface(hdev->dev.parent);
	struct asus_mouse_data *drv_data = hid_get_drvdata(hdev);
	u32 bitmask[ASUS_MOUSE_DATA_KEY_STATE_NUM];

	if (drv_data == NULL)
		return 0;

	if (iface->cur_altsetting->desc.bInterfaceProtocol != 0)
		return 0;

	asus_mouse_gen1_parse_events(bitmask, data, size);

#ifdef ASUS_MOUSE_DEBUG
	printk(KERN_INFO "ASUS MOUSE: STAT %08X %08X %08X %08X",
		drv_data->key_state[0], drv_data->key_state[1], drv_data->key_state[2], drv_data->key_state[3]);
	printk(KERN_INFO "ASUS MOUSE: MASK %08X %08X %08X %08X",
		bitmask[0], bitmask[1], bitmask[2], bitmask[3]);
#endif

	asus_mouse_common_send_events(bitmask, drv_data);
	return 0;
}

// *_RF devices are wireless devices connected with RF receiver
// *_USB devices are wireless devices connected with usb cable
static const struct hid_device_id asus_mouse_gen1_devices[] = {
	{ HID_USB_DEVICE(USB_VENDOR_ID_ASUSTEK, USB_DEVICE_ID_ASUSTEK_ROG_BUZZARD) },
	{ HID_USB_DEVICE(USB_VENDOR_ID_ASUSTEK, USB_DEVICE_ID_ASUSTEK_ROG_GLADIUS2) },
	{ HID_USB_DEVICE(USB_VENDOR_ID_ASUSTEK, USB_DEVICE_ID_ASUSTEK_ROG_GLADIUS2_ORIGIN) },
	{ HID_USB_DEVICE(USB_VENDOR_ID_ASUSTEK, USB_DEVICE_ID_ASUSTEK_ROG_GLADIUS2_ORIGIN_PINK) },
	{ HID_USB_DEVICE(USB_VENDOR_ID_ASUSTEK, USB_DEVICE_ID_ASUSTEK_ROG_PUGIO) },
	{ HID_USB_DEVICE(USB_VENDOR_ID_ASUSTEK, USB_DEVICE_ID_ASUSTEK_ROG_STRIX_CARRY) },
	{ HID_USB_DEVICE(USB_VENDOR_ID_ASUSTEK, USB_DEVICE_ID_ASUSTEK_ROG_STRIX_EVOLVE) },
	{ HID_USB_DEVICE(USB_VENDOR_ID_ASUSTEK, USB_DEVICE_ID_ASUSTEK_ROG_STRIX_IMPACT) },
	{ HID_USB_DEVICE(USB_VENDOR_ID_ASUSTEK, USB_DEVICE_ID_ASUSTEK_ROG_STRIX_IMPACT2_WIRELESS_RF) },
	{ HID_USB_DEVICE(USB_VENDOR_ID_ASUSTEK, USB_DEVICE_ID_ASUSTEK_ROG_STRIX_IMPACT2_WIRELESS_USB) },
	{ HID_USB_DEVICE(USB_VENDOR_ID_ASUSTEK, USB_DEVICE_ID_ASUSTEK_ROG_STRIX_SPATHA_RF) },
	{ HID_USB_DEVICE(USB_VENDOR_ID_ASUSTEK, USB_DEVICE_ID_ASUSTEK_ROG_STRIX_SPATHA_USB) },
	{ }
};
MODULE_DEVICE_TABLE(hid, asus_mouse_gen1_devices);

static struct hid_driver asus_mouse_gen1_driver = {
	.name = "asus-mouse-gen1",
	.id_table = asus_mouse_gen1_devices,
	.probe = asus_mouse_common_probe,
	.remove = asus_mouse_common_remove,
	.raw_event = asus_mouse_gen1_raw_event,
};
module_hid_driver(asus_mouse_gen1_driver);

MODULE_LICENSE("GPL");
