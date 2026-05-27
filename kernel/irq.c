#include "irq.h"
#include "io.h"
#include "idt.h"
#include "screen.h"

irq_handler_t irq_handlers[16] = {0};

void irq_handler(struct regs *r) {
    unsigned char irq = r->int_no - 32;

    if (irq_handlers[irq] != 0) {
        irq_handlers[irq](r);
    }

    if (irq >= 8) {
        outb(0xA0, 0x20);
    }
    outb(0x20, 0x20);
}