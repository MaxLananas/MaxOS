#include "fault_handler.h"
#include "io.h"

void isr_handler(unsigned int num, unsigned int err) {
    fault_handler(num, err);
}

void irq_handler(unsigned int num) {
    if (num >= 40) outb(0xA0, 0x20);
    outb(0x20, 0x20);
}