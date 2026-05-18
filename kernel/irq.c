#include "irq.h"
#include "screen.h"
#include "idt.h"

void irq_handler(unsigned int num) {
    screen_set_color(0x0A);
    screen_writeln("IRQ received:", 0x0A);
    screen_putchar('I', 0x0A);
    screen_putchar('R', 0x0A);
    screen_putchar('Q', 0x0A);
    screen_putchar(':', 0x0A);
    screen_putchar('0' + num / 10, 0x0A);
    screen_putchar('0' + num % 10, 0x0A);
    screen_putchar('\n', 0xFF);
    screen_set_color(0x0F);
}