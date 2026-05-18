#include "isr.h"
#include "idt.h"
#include "io.h"
#include "fault_handler.h"

void isr_handler(unsigned int num, unsigned int err) {
    screen_writeln("Received interrupt:", 0x0F);
    screen_putchar('0' + num / 10, 0x0F);
    screen_putchar('0' + num % 10, 0x0F);
    screen_putchar('\n', 0x0F);
}

void irq_handler(unsigned int num) {
    if (num >= 40) {
        outb(0xA0, 0x20);
    }
    outb(0x20, 0x20);
}