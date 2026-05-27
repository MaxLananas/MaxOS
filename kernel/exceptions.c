#include "screen.h"

void isr_handler(unsigned int num, unsigned int err) {
    screen_write("Exception: ", 0x0C);
    screen_putchar('0' + num, 0x0C);
    screen_putchar('\n', 0x0C);
}