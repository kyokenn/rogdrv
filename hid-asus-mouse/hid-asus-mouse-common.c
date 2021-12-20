#include <linux/hid.h>
#include <linux/module.h>
#include <linux/usb.h>

#include "hid-asus-mouse-common.h"

static int asus_mouse_common_probe(struct hid_device *hdev, const struct hid_device_id *id)
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

	for (i = 0; i < ASUS_MOUSE_DATA_KEY_STATE_NUM; i++)
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

static void asus_mouse_common_remove(struct hid_device *hdev)
{
	struct asus_mouse_data *drv_data = hid_get_drvdata(hdev);
	if (drv_data != NULL) {
		/* TODO: clean up? */
	}
	hid_hw_stop(hdev);
}

static void asus_mouse_common_send_events(u32 bitmask[], struct asus_mouse_data *drv_data)
{
	int i, bit, asus_code, key_code;
	u32 modified;

	// get key codes and send key events
	for (i = 0; i < ASUS_MOUSE_DATA_KEY_STATE_NUM; i++) {
		modified = drv_data->key_state[ASUS_MOUSE_DATA_KEY_STATE_NUM - i - 1] ^
			bitmask[ASUS_MOUSE_DATA_KEY_STATE_NUM - i - 1];
		for (bit = 0; bit < ASUS_MOUSE_DATA_KEY_STATE_BITS; bit += 1) {
			if (!(modified & (1 << bit)))
				continue;

			asus_code = i * ASUS_MOUSE_DATA_KEY_STATE_BITS + bit;
			if (asus_code >= ASUS_MOUSE_MAPPING_SIZE) {
				continue;
			}

			key_code = asus_mouse_mapping[asus_code];

			if (bitmask[ASUS_MOUSE_DATA_KEY_STATE_NUM - i - 1] & (1 << bit)) {
#ifdef ASUS_MOUSE_DEBUG
				printk(KERN_INFO "ASUS MOUSE: PRES 0x%02X (%d) - 0x%02X (%d) '%c'",
				       asus_code, asus_code, key_code, key_code, key_code);
#endif
				input_event(drv_data->input, EV_KEY, key_code, 1);
			} else {
#ifdef ASUS_MOUSE_DEBUG
				printk(KERN_INFO "ASUS MOUSE: RELE 0x%02X (%d) - 0x%02X (%d) '%c'",
				       asus_code, asus_code, key_code, key_code, key_code);
#endif
				input_event(drv_data->input, EV_KEY, key_code, 0);
			}
			input_sync(drv_data->input);
		}
	}

	// save current keys state for tracking released keys
	for (i = 0; i < ASUS_MOUSE_DATA_KEY_STATE_NUM; i++)
		drv_data->key_state[i] = bitmask[i];
}
