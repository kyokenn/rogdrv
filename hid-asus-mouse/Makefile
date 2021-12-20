obj-m += hid-asus-mouse-gen1.o
# obj-m += hid-asus-mouse-gen2.o
KERNEL_DIR ?= /lib/modules/$(shell uname -r)/build

all:
	make -C $(KERNEL_DIR) M=$(shell pwd) modules
install:
	make -C $(KERNEL_DIR) M=$(shell pwd) modules_install
clean:
	make -C $(KERNEL_DIR) M=$(shell pwd) clean
