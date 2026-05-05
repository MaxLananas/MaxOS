#include "idt.h"
#include "irq.h"
#include "io.h"

void irq_set_mask(unsigned char irq) {
    unsigned short port;
    unsigned char value;

    if (irq < 8) {
        port = 0x21;
    } else {
        port = 0xA1;
        irq -= 8;
    }
    value = inb(port) | (1 << irq);
    outb(port, value);
}

void irq_clear_mask(unsigned char irq) {
    unsigned short port;
    unsigned char value;

    if (irq < 8) {
        port = 0x21;
    } else {
        port = 0xA1;
        irq -= 8;
    }
    value = inb(port) & ~(1 << irq);
    outb(port, value);
}