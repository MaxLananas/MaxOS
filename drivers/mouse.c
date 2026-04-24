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
    unsigned char status = inb(0x64);
    if (!(status & 0x20)) return;

    static unsigned char cycle = 0;
    static unsigned char packet[3];
    unsigned char data = inb(0x60);

    switch (cycle) {
        case 0:
            if (!(data & 0x08)) return;
            packet[0] = data;
            break;
        case 1:
            packet[1] = data;
            break;
        case 2:
            packet[2] = data;
            screen_putchar('M', 0x0F);
            break;
    }
    cycle = (cycle + 1) % 3;
}