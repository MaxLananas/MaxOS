#include "isr.h"
#include "idt.h"
#include "fault_handler.h"
#include "io.h"

isr_t interrupt_handlers[256];

void isr_handler(unsigned int num, unsigned int err) {
    if (interrupt_handlers[num] != 0) {
        isr_t handler = interrupt_handlers[num];
        handler(err);
    } else {
        fault_handler(num, err);
    }
}

void irq_handler(unsigned int num) {
    if (num >= 40) {
        outb(0xA0, 0x20);
    }
    outb(0x20, 0x20);

    if (interrupt_handlers[num] != 0) {
        isr_t handler = interrupt_handlers[num];
        handler(0);
    }
}

void register_interrupt_handler(unsigned char n, isr_t handler) {
    interrupt_handlers[n] = handler;
}