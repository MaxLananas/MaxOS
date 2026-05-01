#include "screen.h"
#include "fault_handler.h"

void isr_handler(unsigned int num, unsigned int err) {
    screen_writeln("Received interrupt:", 0x0F);
    screen_putchar('0' + num / 10, 0x0F);
    screen_putchar('0' + num % 10, 0x0F);
    screen_putchar('\n', 0x0F);
    fault_handler(num, err);
}