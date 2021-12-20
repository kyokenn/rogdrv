#include <linux/hid.h>
#include <linux/module.h>
#include <linux/usb.h>
/* #include "hid-ids.h" */

// TODO: move to hid-ids.h
// *_RF devices are wireless devices connected with RF receiver
// *_USB devices are wireless devices connected with usb cable
#define USB_VENDOR_ID_ASUSTEK		0x0b05
#define USB_DEVICE_ID_ASUSTEK_ROG_BUZZARD 0x1816
#define USB_DEVICE_ID_ASUSTEK_ROG_GLADIUS2 0x1845
#define USB_DEVICE_ID_ASUSTEK_ROG_GLADIUS2_ORIGIN 0x1877
#define USB_DEVICE_ID_ASUSTEK_ROG_GLADIUS2_ORIGIN_PINK 0x18cd
#define USB_DEVICE_ID_ASUSTEK_ROG_KERIS_WIRELESS_RF 0x1960
#define USB_DEVICE_ID_ASUSTEK_ROG_KERIS_WIRELESS_USB 0x195e
#define USB_DEVICE_ID_ASUSTEK_ROG_PUGIO 0x1846
#define USB_DEVICE_ID_ASUSTEK_ROG_STRIX_CARRY 0x18b4
#define USB_DEVICE_ID_ASUSTEK_ROG_STRIX_CHAKRAM_RF 0x18E5
#define USB_DEVICE_ID_ASUSTEK_ROG_STRIX_CHAKRAM_USB 0x18E3
#define USB_DEVICE_ID_ASUSTEK_ROG_STRIX_EVOLVE 0x185B
#define USB_DEVICE_ID_ASUSTEK_ROG_STRIX_IMPACT 0x1847
#define USB_DEVICE_ID_ASUSTEK_ROG_STRIX_IMPACT2_WIRELESS_RF 0x1949
#define USB_DEVICE_ID_ASUSTEK_ROG_STRIX_IMPACT2_WIRELESS_USB 0x1947
#define USB_DEVICE_ID_ASUSTEK_ROG_STRIX_SPATHA_RF 0x1824
#define USB_DEVICE_ID_ASUSTEK_ROG_STRIX_SPATHA_USB 0x181C

#define ASUS_MOUSE_DEBUG 1

#define ASUS_MOUSE_DATA_KEY_STATE_SIZE 4
struct asus_mouse_data {
	__u32 key_state[ASUS_MOUSE_DATA_KEY_STATE_SIZE];
	struct input_dev *input;
};

#define ASUS_MOUSE_MAPPING_SIZE 98
static unsigned char asus_mouse_mapping[] = {
	0,
	0,
	0,
	0,
	KEY_A,  // 4
	KEY_B,
	KEY_C,
	KEY_D,
	KEY_E,
	KEY_F,
	KEY_G,
	KEY_H,
	KEY_I,
	KEY_J,
	KEY_K,
	KEY_L,
	KEY_M,
	KEY_N,
	KEY_O,
	KEY_P,
	KEY_Q,
	KEY_R,
	KEY_S,
	KEY_T,
	KEY_U,
	KEY_V,
	KEY_W,
	KEY_X,
	KEY_Y,
	KEY_Z,
	KEY_1,
	KEY_2,
	KEY_3,
	KEY_4,
	KEY_5,
	KEY_6,
	KEY_7,
	KEY_8,
	KEY_9,
	KEY_0,
	KEY_ENTER,
	KEY_ESC,
	KEY_BACKSPACE,
	KEY_TAB,
	KEY_SPACE,
	KEY_MINUS,
	KEY_KPPLUS,  // 46
	0,
	0,
	0,
	0,
	0,
	0,
	KEY_GRAVE,  // 53
	KEY_EQUAL,
	0,
	KEY_SLASH,  // 56
	0,
	KEY_F1,  // 58
	KEY_F2,
	KEY_F3,
	KEY_F4,
	KEY_F5,
	KEY_F6,
	KEY_F7,
	KEY_F8,
	KEY_F9,
	KEY_F10,
	KEY_F11,
	KEY_F12,  // 69
	0,
	0,
	0,
	0,
	KEY_HOME,  // 74
	KEY_PAGEUP,
	KEY_DELETE,
	0,
	KEY_PAGEDOWN,  // 78
	KEY_RIGHT,
	KEY_LEFT,
	KEY_DOWN,
	KEY_UP,  // 82
	0,
	0,
	0,
	0,
	0,
	0,
	KEY_KP1,  // 89
	KEY_KP2,
	KEY_KP3,
	KEY_KP4,
	KEY_KP5,
	KEY_KP6,
	KEY_KP7,
	KEY_KP8,
	KEY_KP9,  // 97
	0,
};

static int asus_mouse_probe(struct hid_device *hdev, const struct hid_device_id *id)
{
	struct usb_interface *iface = to_usb_interface(hdev->dev.parent);
	struct hid_input *next, *hidinput = NULL;
	struct asus_mouse_data *drv_data;
	int error, i;

	drv_data = devm_kzalloc(&hdev->dev, sizeof(*drv_data), GFP_KERNEL);
	if (drv_data == NULL) {
		hid_err(hdev, "can't alloc device descriptor\n");
		return -ENOMEM;
	}

	for (i = 0; i < ASUS_MOUSE_DATA_KEY_STATE_SIZE; i++)
		drv_data->key_state[i] = 0;
	drv_data->input = NULL;
	hid_set_drvdata(hdev, drv_data);

	error = hid_parse(hdev);
	if (error) {
		hid_err(hdev, "parse failed\n");
		return error;
	}

	error = hid_hw_start(hdev, HID_CONNECT_DEFAULT);
	if (error) {
		hid_err(hdev, "hw start failed\n");
		return error;
	}

#ifdef ASUS_MOUSE_DEBUG
	/* printk(KERN_INFO "ASUS MOUSE: MOUS %d", USB_INTERFACE_PROTOCOL_MOUSE); */
	/* printk(KERN_INFO "ASUS MOUSE: KEYB %d", USB_INTERFACE_PROTOCOL_KEYBOARD); */
	printk(KERN_INFO "ASUS MOUSE: PROB %d %X", iface->cur_altsetting->desc.bInterfaceProtocol, hdev->collection->usage);
#endif

	list_for_each_entry_safe(hidinput, next, &hdev->inputs, list) {
		if (hidinput->registered && hidinput->input != NULL) {
			drv_data->input = hidinput->input;
			break;
		}
	}

	return 0;
}

static void asus_mouse_remove(struct hid_device *hdev)
{
	struct asus_mouse_data *drv_data = hid_get_drvdata(hdev);
	if (drv_data != NULL) {
		/* TODO: clean up? */
	}
	hid_hw_stop(hdev);
}

static int asus_mouse_raw_event(struct hid_device *hdev, struct hid_report *report,
		u8 *data, int size)
{
	int i, bit, offset, asus_code, key_code;
	u32 bitmask[4], modified;
	struct usb_interface *iface = to_usb_interface(hdev->dev.parent);
	struct asus_mouse_data *drv_data = hid_get_drvdata(hdev);

	if (drv_data == NULL)
		return 0;

	/* if (iface->cur_altsetting->desc.bInterfaceProtocol != USB_INTERFACE_PROTOCOL_KEYBOARD) */
	if (iface->cur_altsetting->desc.bInterfaceProtocol != 0)
		return 0;

	// build bitmask from event data
	if (size == 9) {  // gen1 & gen2 mice - got array of active key codes
#ifdef ASUS_MOUSE_DEBUG
		printk(KERN_INFO "ASUS MOUSE: DATA %02X %02X %02X %02X %02X %02X %02X %02X %02X",
			data[0], data[1], data[2], data[3], data[4], data[5], data[6], data[7], data[8]);
#endif

		if (data[0] != 0x01)  // validate packet
			return 0;

		for (i = 0; i < ASUS_MOUSE_DATA_KEY_STATE_SIZE; i++)  // init/reset bitmasks
			bitmask[i] = 0;

		for (offset = 3; offset < size; offset++) {
			bit = data[offset];
			if (!bit)
				continue;
			bitmask[ASUS_MOUSE_DATA_KEY_STATE_SIZE - (bit / 32) - 1] |= 1 << (bit % 32);
		}
	} else if (size == 17) {  // gen3 mice - got packed bitmask
#ifdef ASUS_MOUSE_DEBUG
		printk(KERN_INFO "ASUS MOUSE: DATA %02X %02X %02X %02X %02X %02X %02X %02X",
			data[0], data[1], data[2], data[3], data[4], data[5], data[6], data[7]);
		printk(KERN_INFO "ASUS MOUSE: DATA %02X %02X %02X %02X %02X %02X %02X %02X %02X",
			data[8], data[9], data[10], data[11], data[12], data[13], data[14], data[15], data[16]);
#endif

		if (data[0] != 0x04)  // validate packet
			return 0;

		offset = size - 1;
		for (i = 0; i < ASUS_MOUSE_DATA_KEY_STATE_SIZE; i++) {
			bitmask[i] = 0;
			bit = 0;
			if (i == 0)  // first byte of 16-byte number is missing, so we skip it
				bit = 8;
			for (; bit < 32; bit += 8) {
				bitmask[i] |= data[offset] << (24 - bit);
				offset--;
			}
		}
	} else {
		return 0;
	}

#ifdef ASUS_MOUSE_DEBUG
	printk(KERN_INFO "ASUS MOUSE: STAT %08X %08X %08X %08X",
		drv_data->key_state[0], drv_data->key_state[1], drv_data->key_state[2], drv_data->key_state[3]);
	printk(KERN_INFO "ASUS MOUSE: MASK %08X %08X %08X %08X",
		bitmask[0], bitmask[1], bitmask[2], bitmask[3]);
#endif

	// get key codes
	for (i = 0; i < ASUS_MOUSE_DATA_KEY_STATE_SIZE; i++) {
		modified = drv_data->key_state[ASUS_MOUSE_DATA_KEY_STATE_SIZE - i - 1] ^
			bitmask[ASUS_MOUSE_DATA_KEY_STATE_SIZE - i - 1];
		for (bit = 0; bit < 32; bit += 1) {
			if (!(modified & (1 << bit)))
				continue;

			asus_code = i * 32 + bit;
			if (asus_code >= ASUS_MOUSE_MAPPING_SIZE) {
				hid_warn(hdev, "unmapped special key code 0x%02X: ignoring\n", asus_code);
				return 0;
			}

			key_code = asus_mouse_mapping[asus_code];

			if (bitmask[ASUS_MOUSE_DATA_KEY_STATE_SIZE - i - 1] & (1 << bit)) {
#ifdef ASUS_MOUSE_DEBUG
				printk(KERN_INFO "ASUS MOUSE: PRES 0x%02X (%d) - 0x%02X (%d) '%c'", asus_code, asus_code, key_code, key_code, key_code);
#endif
				input_event(drv_data->input, EV_KEY, key_code, 1);
			} else {
#ifdef ASUS_MOUSE_DEBUG
				printk(KERN_INFO "ASUS MOUSE: RELE 0x%02X (%d) - 0x%02X (%d) '%c'", asus_code, asus_code, key_code, key_code, key_code);
#endif
				input_event(drv_data->input, EV_KEY, key_code, 0);
			}
			input_sync(drv_data->input);
		}
	}

	// save current keys state for tracking released keys
	for (i = 0; i < ASUS_MOUSE_DATA_KEY_STATE_SIZE; i++)
		drv_data->key_state[i] = bitmask[i];

	return 0;
}

static const struct hid_device_id asus_mouse_devices[] = {
	{ HID_USB_DEVICE(USB_VENDOR_ID_ASUSTEK, USB_DEVICE_ID_ASUSTEK_ROG_BUZZARD) },
	{ HID_USB_DEVICE(USB_VENDOR_ID_ASUSTEK, USB_DEVICE_ID_ASUSTEK_ROG_GLADIUS2) },
	{ HID_USB_DEVICE(USB_VENDOR_ID_ASUSTEK, USB_DEVICE_ID_ASUSTEK_ROG_GLADIUS2_ORIGIN) },
	{ HID_USB_DEVICE(USB_VENDOR_ID_ASUSTEK, USB_DEVICE_ID_ASUSTEK_ROG_GLADIUS2_ORIGIN_PINK) },
	{ HID_USB_DEVICE(USB_VENDOR_ID_ASUSTEK, USB_DEVICE_ID_ASUSTEK_ROG_KERIS_WIRELESS_RF) },
	{ HID_USB_DEVICE(USB_VENDOR_ID_ASUSTEK, USB_DEVICE_ID_ASUSTEK_ROG_KERIS_WIRELESS_USB) },
	{ HID_USB_DEVICE(USB_VENDOR_ID_ASUSTEK, USB_DEVICE_ID_ASUSTEK_ROG_PUGIO) },
	{ HID_USB_DEVICE(USB_VENDOR_ID_ASUSTEK, USB_DEVICE_ID_ASUSTEK_ROG_STRIX_CARRY) },
	{ HID_USB_DEVICE(USB_VENDOR_ID_ASUSTEK, USB_DEVICE_ID_ASUSTEK_ROG_STRIX_CHAKRAM_RF) },
	{ HID_USB_DEVICE(USB_VENDOR_ID_ASUSTEK, USB_DEVICE_ID_ASUSTEK_ROG_STRIX_CHAKRAM_USB) },
	{ HID_USB_DEVICE(USB_VENDOR_ID_ASUSTEK, USB_DEVICE_ID_ASUSTEK_ROG_STRIX_EVOLVE) },
	{ HID_USB_DEVICE(USB_VENDOR_ID_ASUSTEK, USB_DEVICE_ID_ASUSTEK_ROG_STRIX_IMPACT) },
	{ HID_USB_DEVICE(USB_VENDOR_ID_ASUSTEK, USB_DEVICE_ID_ASUSTEK_ROG_STRIX_IMPACT2_WIRELESS_RF) },
	{ HID_USB_DEVICE(USB_VENDOR_ID_ASUSTEK, USB_DEVICE_ID_ASUSTEK_ROG_STRIX_IMPACT2_WIRELESS_USB) },
	{ HID_USB_DEVICE(USB_VENDOR_ID_ASUSTEK, USB_DEVICE_ID_ASUSTEK_ROG_STRIX_SPATHA_RF) },
	{ HID_USB_DEVICE(USB_VENDOR_ID_ASUSTEK, USB_DEVICE_ID_ASUSTEK_ROG_STRIX_SPATHA_USB) },
	{ }
};
MODULE_DEVICE_TABLE(hid, asus_mouse_devices);

static struct hid_driver asus_mouse_driver = {
	.name = "asus-mouse",
	.id_table = asus_mouse_devices,
	.probe = asus_mouse_probe,
	.remove = asus_mouse_remove,
	.raw_event = asus_mouse_raw_event,
};
module_hid_driver(asus_mouse_driver);

MODULE_LICENSE("GPL");
