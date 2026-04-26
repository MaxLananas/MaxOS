#include "irq_handler.h"
#include "screen.h"

void irq_handler(unsigned int num) {
    screen_writeln("IRQ received", 0x0E);
    screen_writeln("IRQ number: ", 0x0E);
    screen_putchar('0' + num, 0x0E);
    screen_putchar('\n', 0x0E);
}