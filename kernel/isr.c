#include "isr.h"
#include "fault_handler.h"
#include "screen.h"

void isr_handler(unsigned int num, unsigned int err) {
    screen_set_color(0x0C);
    screen_writeln("INTERRUPT RECEIVED", 0x0C);
    screen_putchar('I', 0x0C);
    screen_putchar('S', 0x0C);
    screen_putchar('R', 0x0C);
    screen_putchar(':', 0x0C);
    screen_putchar('0' + num / 10, 0x0C);
    screen_putchar('0' + num % 10, 0x0C);
    screen_putchar('\n', 0x0C);

    fault_handler(num, err);
}