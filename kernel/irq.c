#include "io.h"
#include "idt.h"

void irq_set_mask(unsigned char irq_line, unsigned char mask) {
    unsigned short port;
    unsigned char value;

    if (irq_line < 8) {
        port = 0x21;
    } else {
        port = 0xA1;
        irq_line -= 8;
    }

    value = inb(port);
    if (mask) {
        value |= (1 << irq_line);
    } else {
        value &= ~(1 << irq_line);
    }
    outb(port, value);
}

void irq_init(void) {
    outb(0x20, 0x11);
    outb(0xA0, 0x11);
    outb(0x21, 0x20);
    outb(0xA1, 0x28);
    outb(0x21, 0x04);
    outb(0xA1, 0x02);
    outb(0x21, 0x01);
    outb(0xA1, 0x01);
    outb(0x21, 0x0);
    outb(0xA1, 0x0);
}