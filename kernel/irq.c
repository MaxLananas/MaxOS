#include "kernel/irq.h"
#include "kernel/isr.h"
#include "drivers/screen.h"

void irq_handler(unsigned int num) {
    if (num >= 40) {
        outb(0xA0, 0x20);
    }
    outb(0x20, 0x20);

    isr_handler(num, 0);
}