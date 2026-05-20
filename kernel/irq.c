#include "irq.h"
#include "screen.h"
#include "io.h"

void irq_handler(unsigned int num) {
    screen_write("IRQ: ", 0x0F);
    screen_putchar('0' + num / 10, 0x0F);
    screen_putchar('0' + num % 10, 0x0F);
    screen_writeln("", 0x0F);
    outb(0x20, 0x20);
}