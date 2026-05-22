#include "isr.h"
#include "screen.h"
#include "fault_handler.h"

void isr_handler(unsigned int num, unsigned int err) {
    screen_set_color(0x0C);
    screen_writeln("Interrupt received!", 0x0C);
    screen_putchar('I', 0x0C);
    screen_putchar('S', 0x0C);
    screen_putchar('R', 0x0C);
    screen_putchar(':', 0x0C);
    screen_putchar('0' + num / 10, 0x0C);
    screen_putchar('0' + num % 10, 0x0C);
    screen_putchar(' ', 0x0C);
    screen_putchar('E', 0x0C);
    screen_putchar('R', 0x0C);
    screen_putchar('R', 0x0C);
    screen_putchar(':', 0x0C);
    screen_putchar('0' + err / 10, 0x0C);
    screen_putchar('0' + err % 10, 0x0C);
    screen_putchar('\n', 0x0C);

    fault_handler(num, err);
}