#include "fault_handler.h"
#include "screen.h"
#include "idt.h"

void fault_handler(unsigned int num, unsigned int err) {
    screen_clear();
    screen_writeln("EXCEPTION OCCURRED", 0x0C);
    screen_putchar('E', 0x0C);
    screen_putchar('R', 0x0C);
    screen_putchar('R', 0x0C);
    screen_putchar(':', 0x0C);
    screen_putchar('0' + num / 10, 0x0C);
    screen_putchar('0' + num % 10, 0x0C);
    while (1);
}