#include "mouse.h"
#include "io.h"
#include "screen.h"

void mouse_wait(unsigned char type) {
    unsigned int timeout = 100000;
    if (type == 0) {
        while (timeout--) {
            if ((inb(0x64) & 1) == 1) {
                return;
            }
        }
    } else {
        while (timeout--) {
            if ((inb(0x64) & 2) == 0) {
                return;
            }
        }
    }
}

void mouse_init(void) {
    mouse_wait(1);
    outb(0x64, 0xA8);
    mouse_wait(1);
    outb(0x64, 0x20);
    mouse_wait(0);
    unsigned char status = inb(0x60);
    status |= 2;
    mouse_wait(1);
    outb(0x64, 0x60);
    mouse_wait(1);
    outb(0x60, status);
    outb(0x64, 0xD4);
    outb(0x60, 0xF4);
    mouse_wait(0);
    inb(0x60);
}

void mouse_handler(void) {
    unsigned char data = inb(0x60);
    screen_putchar('M', 0x0F);
}