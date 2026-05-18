#include "irq.h"
#include "io.h"
#include "idt.h"

void (*irq_handlers[16])(void);

void irq_set_handler(unsigned char irq, void (*handler)(void)) {
    irq_handlers[irq] = handler;
}

void irq_handler(unsigned int num) {
    void (*handler)(void);

    handler = irq_handlers[num - 32];
    if (handler) {
        handler();
    }

    if (num >= 40) {
        outb(0xA0, 0x20);
    }
    outb(0x20, 0x20);
}