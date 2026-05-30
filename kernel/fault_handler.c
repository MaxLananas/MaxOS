#include "fault_handler.h"
#include "screen.h"

void fault_handler(unsigned int num, unsigned int err) {
    screen_set_color(0x0C);
    screen_writeln("Exception occurred:", 0x0C);
    screen_putchar('E', 0x0C);
    screen_putchar('x', 0x0C);
    screen_putchar('c', 0x0C);
    screen_putchar('e', 0x0C);
    screen_putchar('p', 0x0C);
    screen_putchar('t', 0x0C);
    screen_putchar('i', 0x0C);
    screen_putchar('o', 0x0C);
    screen_putchar('n', 0x0C);
    screen_putchar(':', 0x0C);
    screen_putchar('0' + num / 10, 0x0C);
    screen_putchar('0' + num % 10, 0x0C);
    screen_putchar('\n', 0x0C);

    for (;;);
}