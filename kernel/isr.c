#include "isr.h"
#include "screen.h"
#include "idt.h"

void isr_handler(unsigned int num, unsigned int err) {
    screen_writeln("Received interrupt:", 0x0F);
    screen_putchar('0' + num / 10, 0x0F);
    screen_putchar('0' + num % 10, 0x0F);
    screen_putchar('\n', 0x0F);
}