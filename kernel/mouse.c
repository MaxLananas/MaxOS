#include "mouse.h"
#include "io.h"
#include "screen.h"
#include "irq.h"

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

void mouse_handler(void) {
    unsigned char status = inb(0x64);
    if (status & 0x20) {
        unsigned char data = inb(0x60);
        screen_putchar('M', 0x0A);
    }
}

void mouse_init(void) {
    mouse_wait(1);
    outb(0x64, 0xA8);
    mouse_wait(1);
    outb(0x64, 0x20);
    mouse_wait(0);
    unsigned char status = inb(0x60) | 2;
    mouse_wait(1);
    outb(0x64, 0x60);
    mouse_wait(1);
    outb(0x60, status);
    mouse_write(0xF6);
    mouse_read();
    mouse_write(0xF4);
    mouse_read();
    irq_install_handler(12, mouse_handler);
}