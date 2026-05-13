#include "isr_handler.h"
#include "screen.h"
#include "idt.h"

void isr_handler(unsigned int num, unsigned int err) {
    screen_set_color(0x0C);
    screen_writeln("Interrupt received!", 0x0C);
    screen_write("Interrupt: ", 0x0C);
    screen_putchar('0' + num, 0x0C);
    screen_writeln("", 0x0C);
}

void irq_handler(unsigned int num) {
    if (num >= 40) {
        outb(0xA0, 0x20);
    }
    outb(0x20, 0x20);
}