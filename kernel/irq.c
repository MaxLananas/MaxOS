#include "kernel/irq.h"
#include "kernel/io.h"

void register_interrupt_handler(unsigned char n, void (*handler)(struct regs *r)) {
    interrupt_handlers[n] = handler;
}

void irq_handler(unsigned int num) {
    if (num >= 40) {
        outb(0xA0, 0x20);
    }
    outb(0x20, 0x20);
}