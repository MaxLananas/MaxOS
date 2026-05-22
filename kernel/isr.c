#include "isr.h"
#include "idt.h"
#include "screen.h"
#include "io.h"

void isr_handler(unsigned int num, unsigned int err) {
    screen_writeln("Received interrupt:", 0x04);
    screen_write("Interrupt number: ", 0x04);
    screen_putchar('0' + num / 10, 0x04);
    screen_putchar('0' + num % 10, 0x04);
    screen_putchar('\n', 0x04);
    outb(0x20, 0x20);
}

void irq_handler(unsigned int num) {
    if (num >= 40) {
        outb(0xA0, 0x20);
    }
    outb(0x20, 0x20);
}