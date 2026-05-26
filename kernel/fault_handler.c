#include "fault_handler.h"
#include "screen.h"
#include "idt.h"

void fault_handler(unsigned int num, unsigned int err) {
    screen_set_color(0x0C);
    screen_writeln("EXCEPTION: ", 0x0C);
    screen_putchar('0' + num, 0x0C);
    screen_writeln("", 0x0C);

    if (err != 0) {
        screen_writeln("Error code: ", 0x0C);
        screen_putchar('0' + err, 0x0C);
        screen_writeln("", 0x0C);
    }

    while (1);
}