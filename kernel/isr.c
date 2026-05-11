#include "isr.h"
#include "screen.h"
#include "idt.h"

void isr_handler(unsigned int num, unsigned int err) {
    screen_clear();
    screen_writeln("Interrupt received:", 0x0C);
    screen_putchar('I', 0x0C);
    screen_putchar('S', 0x0C);
    screen_putchar('R', 0x0C);
    screen_putchar(':', 0x0C);
    screen_putchar((char)('0' + num / 10), 0x0C);
    screen_putchar((char)('0' + num % 10), 0x0C);
    screen_putchar('\n', 0x0C);
    screen_writeln("Error code:", 0x0C);
    screen_putchar((char)('0' + err / 100), 0x0C);
    screen_putchar((char)('0' + (err / 10) % 10), 0x0C);
    screen_putchar((char)('0' + err % 10), 0x0C);
    while (1) {
        asm volatile("hlt");
    }
}

void irq_handler(unsigned int num) {
    if (num >= 40) {
        outb(0xA0, 0x20);
    }
    outb(0x20, 0x20);
}