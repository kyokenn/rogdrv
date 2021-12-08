obj-m = hid-asus-mouse.o

ARGS=-C /lib/modules/$(shell uname -r)/build/ M=$(PWD)

all:
	make $(ARGS) modules

clean:
	make $(ARGS) clean

load:
	sudo insmod hid-asus-mouse.ko

reload:
	sudo rmmod hid-asus-mouse.ko
	sudo insmod hid-asus-mouse.ko
