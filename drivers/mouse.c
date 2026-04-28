#include "kernel/io.h"

void mouse_init(void) {
    outb(0x64, 0xA8);
    outb(0x64, 0x20);
    unsigned char status = inb(0x60) | 2;
    outb(0x64, 0x60);
    outb(0x60, status);
    outb(0x64, 0xD4);
    outb(0x60, 0xF4);
    inb(0x60);
}

void mouse_handler(void) {
    static unsigned char cycle = 0;
    static unsigned char mouse_bytes[3];
    unsigned char data = inb(0x60);

    switch (cycle) {
        case 0:
            if ((data & 0x08) == 0) break;
            mouse_bytes[0] = data;
            cycle++;
            break;
        case 1:
            mouse_bytes[1] = data;
            cycle++;
            break;
        case 2:
            mouse_bytes[2] = data;
            cycle = 0;
            break;
    }
}