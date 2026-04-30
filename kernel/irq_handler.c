#include "irq_handler.h"
#include "io.h"

void irq_set_mask(unsigned char irq, unsigned char mask) {
    unsigned short port;
    unsigned char value;

    if (irq < 8) {
        port = 0x21;
    } else {
        port = 0xA1;
        irq -= 8;
    }

    value = inb(port);
    if (mask) {
        value |= (1 << irq);
    } else {
        value &= ~(1 << irq);
    }
    outb(port, value);
}

void irq_handler(unsigned int num) {
    if (num >= 40) {
        outb(0xA0, 0x20);
    }
    outb(0x20, 0x20);
}