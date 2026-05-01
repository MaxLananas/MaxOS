#include "irq.h"
#include "screen.h"

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