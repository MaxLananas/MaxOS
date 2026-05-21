#include "isr.h"
#include "screen.h"
#include "fault_handler.h"

void isr_handler(unsigned int num, unsigned int err) {
    screen_writeln("Interrupt occurred!", 0x0C);
    screen_writeln("Interrupt number: ", 0x0C);
    screen_putchar((char)('0' + num), 0x0C);
    screen_putchar('\n', 0x0C);
}