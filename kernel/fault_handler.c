#include "fault_handler.h"
#include "screen.h"

void fault_handler(unsigned int num, unsigned int err) {
    screen_putchar('F', 0x0C);
    screen_putchar('A', 0x0C);
    screen_putchar('U', 0x0C);
    screen_putchar('L', 0x0C);
    screen_putchar('T', 0x0C);
    screen_putchar(':', 0x0C);
    screen_putchar('0' + num / 10, 0x0C);
    screen_putchar('0' + num % 10, 0x0C);
    screen_putchar('\n', 0x0C);
    while(1);
}