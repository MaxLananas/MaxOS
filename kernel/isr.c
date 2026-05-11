#include "isr.h"
#include "screen.h"
#include "io.h"

void *irq_routines[16] = {0};

void isr_handler(unsigned int num, unsigned int err) {
    screen_writeln("Received interrupt", 0x0C);
}

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

void irq_install_handler(int irq, void (*handler)(struct regs *r)) {
    irq_routines[irq] = handler;
}

void irq_uninstall_handler(int irq) {
    irq_routines[irq] = 0;
}