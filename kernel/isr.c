#include "isr.h"
#include "screen.h"
#include "idt.h"

void isr_handler(unsigned int num, unsigned int err) {
    screen_set_color(0x0C);
    screen_writeln("Interrupt received:", 0x0C);
    screen_putchar('0' + num, 0x0C);
    screen_putchar('\n', 0x0C);

    if (err != 0) {
        screen_writeln("Error code:", 0x0C);
        screen_putchar('0' + err, 0x0C);
        screen_putchar('\n', 0x0C);
    }

    asm volatile("cli");
    while (1) {
        asm volatile("hlt");
    }
}

void irq_handler(unsigned int num) {
    if (num >= 40) {
        outb(0xA0, 0x20);
    }
    outb(0x20, 0x20);

    if (num == 33) {
        keyboard_handler();
    } else if (num == 32) {
        timer_handler();
    }
}