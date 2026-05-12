#include "isr.h"
#include "screen.h"
#include "idt.h"

void isr_handler(unsigned int num, unsigned int err) {
    screen_writeln("Interrupt occurred", 0x0C);
    while (1);
}

void irq_handler(unsigned int num) {
    if (num >= 40) {
        outb(0xA0, 0x20);
    }
    outb(0x20, 0x20);
}