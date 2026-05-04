#include "mouse.h"
#include "../kernel/io.h"

void mouse_init(void) {
    unsigned char status;

    outb(0x64, 0xA8);
    outb(0x64, 0x20);
    status = inb(0x64) | 2;
    outb(0x64, 0x60);
    outb(0x64, status);

    outb(0x64, 0xD4);
    outb(0x60, 0xF4);

    inb(0x60);
}

void mouse_handler(void) {
    unsigned char mouse_data = inb(0x60);
    (void)mouse_data;
}