#include "fault_handler.h"
#include "isr.h"

void isr_handler(unsigned int num, unsigned int err) {
    if (num < 32) {
        fault_handler(num, err);
    } else {
        screen_writeln("IRQ: ", 0x0C);
        screen_putchar('0' + num, 0x0C);
        screen_putchar('\n', 0x0C);
    }
}