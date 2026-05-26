#include "isr.h"
#include "screen.h"
#include "fault_handler.h"

void isr_handler(unsigned int num, unsigned int err) {
    screen_set_color(0x0C);
    screen_writeln("Received interrupt:", 0x0C);
    screen_putchar('0' + num / 10, 0x0C);
    screen_putchar('0' + num % 10, 0x0C);

    if (err != 0) {
        screen_writeln("Error code:", 0x0C);
    }

    if (num < 32) {
        fault_handler(num, err);
    }
}