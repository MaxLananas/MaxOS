#include "irq_handler.h"
#include "screen.h"

void irq_handler(unsigned int num) {
    screen_putchar('I', 0x0E);
    screen_putchar('R', 0x0E);
    screen_putchar('Q', 0x0E);
    screen_putchar(' ', 0x0E);
    screen_putchar('0' + num / 10, 0x0E);
    screen_putchar('0' + num % 10, 0x0E);
}