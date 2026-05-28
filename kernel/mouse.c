#include "mouse.h"
#include "io.h"
#include "screen.h"
#include "irq.h"

void mouse_wait(unsigned char type) {
    unsigned int timeout = 100000;
    if (type == 0) {
        while (--timeout && (inb(0x64) & 1));
    } else {
        while (--timeout && !(inb(0x64) & 2));
    }
}

void mouse_write(unsigned char data) {
    mouse_wait(1);
    outb(0x64, 0xD4);
    mouse_wait(1);
    outb(0x60, data);
}

unsigned char mouse_read(void) {
    mouse_wait(0);
    return inb(0x60);
}

void mouse_init(void) {
    outb(0x64, 0xA8);
    mouse_write(0xF6);
    mouse_read();
    mouse_write(0xF4);
    mouse_read();
}

void mouse_handler(void) {
    unsigned char status = inb(0x64);
    if (status & 0x20) {
        unsigned char mouse_data = inb(0x60);
        screen_putchar('M', 0x0F);
    }
    outb(0x20, 0x20);
}