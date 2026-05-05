#include "irq.h"
#include "io.h"

extern void irq_install_handler(unsigned char irq, void (*handler)(void));

void irq_install_handler(unsigned char irq, void (*handler)(void)) {
    unsigned char mask = inb(0x21);
    mask &= ~(1 << irq);
    outb(0x21, mask);
}