#include "irq_handler.h"
#include "idt.h"
#include "io.h"

void *irq_routines[16] = {0};

void irq_handler(unsigned int num) {
    void (*handler)(struct regs *r);

    handler = irq_routines[num - 32];
    if (handler) {
        handler(0);
    }

    if (num >= 40) {
        outb(0xA0, 0x20);
    }
    outb(0x20, 0x20);
}