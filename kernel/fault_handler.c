#include "fault_handler.h"
#include "screen.h"
#include "io.h"

void fault_handler(registers_t regs) {
    screen_set_color(0x0C);
    screen_writeln("EXCEPTION OCCURRED", 0x0C);

    screen_writeln("Exception number:", 0x0C);
    screen_putchar('0' + regs.int_no / 10, 0x0C);
    screen_putchar('0' + regs.int_no % 10, 0x0C);
    screen_putchar('\n', 0x0C);

    screen_writeln("Error code:", 0x0C);
    screen_putchar('0' + regs.err_code / 10, 0x0C);
    screen_putchar('0' + regs.err_code % 10, 0x0C);
    screen_putchar('\n', 0x0C);

    while (1) {
        asm volatile("hlt");
    }
}