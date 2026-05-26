#include "isr_handler.h"
#include "fault_handler.h"
#include "screen.h"

void isr_handler(unsigned int num, unsigned int err) {
    screen_set_color(0x0C);
    screen_writeln("Received interrupt: ", 0x0C);
    screen_putchar('0' + num, 0x0C);
    screen_writeln(" Error code: ", 0x0C);
    screen_putchar('0' + err, 0x0C);
    screen_writeln("\n", 0x0C);

    if (num < 32) {
        fault_handler(num, err);
    }
}