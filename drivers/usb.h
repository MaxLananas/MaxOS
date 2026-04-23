#ifndef USB_H
#define USB_H

#include "../kernel/io.h"

#define USB_BASE 0xC000

void usb_init();
void usb_hid_init();

#endif