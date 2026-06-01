#include "isr.h"
#include "fault_handler.h"
#include "screen.h"

void isr_handler(unsigned int num, unsigned int err)
{
    screen_set_color(0x0C);
    screen_writeln("INTERRUPT OCCURRED", 0x0F);
    screen_write("Interrupt: ", 0x0F);
    screen_putchar('0' + num / 10, 0x0F);
    screen_putchar('0' + num % 10, 0x0F);
    screen_writeln("", 0x0F);

    if (err != 0) {
        screen_write("Error code: ", 0x0F);
        screen_putchar('0' + err / 10, 0x0F);
        screen_putchar('0' + err % 10, 0x0F);
        screen_writeln("", 0x0F);
    }

    for (;;);
}