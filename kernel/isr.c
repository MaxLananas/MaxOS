#include "isr.h"
#include "fault_handler.h"
#include "screen.h"

void isr_handler(unsigned int num, unsigned int err) {
    screen_writeln("Received interrupt", 0x0C);
    screen_putchar('0' + num / 10, 0x0C);
    screen_putchar('0' + num % 10, 0x0C);
    while (1);
}