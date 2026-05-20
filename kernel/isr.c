#include "isr.h"
#include "screen.h"
#include "idt.h"

void isr_handler(unsigned int num, unsigned int err) {
    (void)err;
    screen_writeln("Received interrupt:", 0x0F);
    screen_write("Interrupt number: ", 0x0F);
    screen_putchar('0' + num / 10, 0x0F);
    screen_putchar('0' + num % 10, 0x0F);
    screen_writeln("", 0x0F);
}