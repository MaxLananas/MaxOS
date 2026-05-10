#include "fault_handler.h"
#include "screen.h"
#include "idt.h"

void fault_handler(unsigned int num, unsigned int err) {
    screen_writeln("Exception occurred", 0x0F);
    screen_writeln("Exception number:", 0x0F);
    screen_putchar('0' + num, 0x0F);
    screen_putchar('\n', 0xFF);

    while (1);
}