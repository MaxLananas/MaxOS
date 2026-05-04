#include "mouse.h"
#include "io.h"
#include "screen.h"
#include "irq.h"

void mouse_wait(unsigned char a_type) {
    unsigned int timeout = 100000;
    if (a_type == 0) {
        while (--timeout && (inb(0x64) & 1))
            ;
    } else {
        while (--timeout && (inb(0x64) & 2))
            ;
    }
}

void mouse_write(unsigned char a_write) {
    mouse_wait(1);
    outb(0x64, 0xD4);
    mouse_wait(1);
    outb(0x60, a_write);
}

unsigned char mouse_read(void) {
    mouse_wait(0);
    return inb(0x60);
}

void mouse_callback(struct regs *r) {
    unsigned char status = inb(0x64);
    if (status & 0x20) {
        unsigned char mouse_in = inb(0x60);
        static unsigned char cycle = 0;
        static unsigned char mouse_bytes[3];
        mouse_bytes[cycle++] = mouse_in;
        if (cycle == 3) {
            cycle = 0;
            screen_putchar('M', 0x0A);
        }
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
    irq_install_handler(12, mouse_callback);
}