#include "irq.h"
#include "idt.h"
#include "io.h"

void *irq_routines[16] = {0};

void irq_set_handler(int irq, void (*handler)(struct regs *r)) {
    irq_routines[irq] = handler;
}

void irq_handler(struct regs *r) {
    void (*handler)(struct regs *r);
    handler = irq_routines[r->int_no - 32];
    if (handler) {
        handler(r);
    }
    if (r->int_no >= 40) {
        outb(0xA0, 0x20);
    }
    outb(0x20, 0x20);
}