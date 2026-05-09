#include "mouse.h"
#include "io.h"
#include "screen.h"
#include "idt.h"

void mouse_init(void) {
    unsigned char status;

    status = inb(0x64);
    outb(0x64, 0xA8);

    status = inb(0x64);
    outb(0x64, 0x20);
    status = inb(0x60) | 2;
    outb(0x64, 0x60);
    outb(0x60, status);

    outb(0x64, 0xD4);
    outb(0x60, 0xF4);

    outb(0x64, 0x20);
    status = inb(0x60);
    outb(0x64, 0x60);
    outb(0x60, status & 0xDF);

    unsigned char mask = inb(0x21);
    outb(0x21, mask & 0xEF);
}

void mouse_handler(void) {
    static unsigned char mouse_bytes[3];
    static unsigned char byte_count = 0;

    unsigned char data = inb(0x60);
    mouse_bytes[byte_count++] = data;

    if (byte_count == 3) {
        byte_count = 0;
        int x = mouse_bytes[1];
        int y = mouse_bytes[2];
        screen_putchar('M', 0x0F);
    }
}