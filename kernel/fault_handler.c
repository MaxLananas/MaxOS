#include "fault_handler.h"
#include "screen.h"
#include "io.h"

void fault_handler(registers_t regs) {
    screen_set_color(0x0C);
    screen_writeln("EXCEPTION: ", 0x0C);
    screen_putchar('0' + regs.int_no, 0x0C);
    screen_writeln("", 0x0C);

    if (regs.err_code != 0) {
        screen_writeln("Error code: ", 0x0C);
        screen_putchar('0' + regs.err_code, 0x0C);
        screen_writeln("", 0x0C);
    }

    for (;;);
}