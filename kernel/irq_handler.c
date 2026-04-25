#include "irq.h"
#include "io.h"

void irq_send_eoi(void) {
    outb(0x20, 0x20);
    if (inb(0xA0) & 0x80) {
        outb(0xA0, 0x20);
    }
}

void irq_handler(unsigned int num) {
    if (num >= 40) {
        irq_send_eoi();
    }

    if (irq_routines[num] != 0) {
        void (*handler)(void) = irq_routines[num];
        handler();
    }

    if (num < 40) {
        irq_send_eoi();
    }
}