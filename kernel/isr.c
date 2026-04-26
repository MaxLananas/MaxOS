#include "isr.h"
#include "screen.h"
#include "idt.h"

void isr_handler(unsigned int num, unsigned int err) {
    screen_writeln("Received interrupt", 0x0C);
    screen_writeln("Interrupt number: ", 0x0C);
    screen_putchar('0' + num, 0x0C);
    screen_putchar('\n', 0x0C);
}