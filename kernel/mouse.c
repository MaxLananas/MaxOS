#include "mouse.h"
#include "io.h"
#include "screen.h"

void mouse_init(void) {
    outb(0x64, 0xA8);
    outb(0x64, 0xD4);
    outb(0x60, 0xF4);
    inb(0x60);
}

void mouse_handler(void) {
    unsigned char status = inb(0x64);
    if (status & 0x20) {
        unsigned char mouse_data = inb(0x60);
        screen_putchar(mouse_data, 0x0F);
    }
}