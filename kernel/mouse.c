#include "mouse.h"
#include "io.h"
#include "screen.h"

static unsigned char mouse_bytes[3];
static unsigned char mouse_byte_count = 0;

void mouse_init(void) {
    outb(0x64, 0xA8);
    outb(0x64, 0x20);
    unsigned char status = inb(0x60) | 2;
    outb(0x64, 0x60);
    outb(0x60, status);
    outb(0x64, 0xD4);
    outb(0x60, 0xF4);
    outb(0x64, 0x20);
    inb(0x60);
}

void mouse_handler(void) {
    unsigned char status = inb(0x64);
    if (status & 0x20) {
        unsigned char data = inb(0x60);
        mouse_bytes[mouse_byte_count++] = data;

        if (mouse_byte_count == 3) {
            mouse_byte_count = 0;
            int x = mouse_bytes[1];
            int y = mouse_bytes[2];
            screen_putchar('M', 0x0F);
        }
    }
}