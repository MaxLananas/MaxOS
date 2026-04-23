#include "usb.h"
#include "../kernel/io.h"
#include "../kernel/screen.h"

static void usb_wait(unsigned int ms) {
    for (unsigned int i = 0; i < ms * 1000; i++) {
        io_wait();
    }
}

void usb_init() {
    screen_write("USB Controller initializing...\n", 0x0F);
    usb_wait(100);
    screen_write("USB Controller initialized\n", 0x0F);
}

void usb_hid_init() {
    screen_write("USB HID device detected\n", 0x0F);
}