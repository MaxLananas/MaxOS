#include "fault_handler.h"
#include "screen.h"
#include "isr.h"

void fault_handler(unsigned int num, unsigned int err) {
    screen_writeln("Fault occurred:", 0x0C);
    screen_write("Fault number: ", 0x0C);
    screen_putchar('0' + num / 10, 0x0C);
    screen_putchar('0' + num % 10, 0x0C);
    screen_writeln("", 0x0C);
    (void)err;
}